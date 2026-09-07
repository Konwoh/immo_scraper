import logging
import threading
import time
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from sqlalchemy.engine import Engine
from backend.shared.exceptions import NoFavoritesError

from backend.ml.preprocessing.data_cleaner import DataCleaner
from backend.ml.preprocessing.data_loader import DataLoader
from backend.ml.preprocessing.feature_engineering import FeatureEngineering
from backend.database.models import Recommendation

logger = logging.getLogger("ml_recommender")

ESTATE_TYPES = ("houses", "apartments")

TEXT_COLS = ["general_description", "place_description", "object_description"]
BOOL_LIKE = ["lift", "barrier_free", "garden", "fitted_kitchen", "basement", "rented"]
_ESTATE_TYPE_RENAME = {"Einfamilienhaus (freistehend)": "Einfamilienhaus freistehend"}

class PropertyRecommender:
    def __init__(
        self,
        engine: Engine,
        estate: str,
        user_id: int,
        *,
        alpha: float = 0.5,
        max_features: int = 2000,
        min_frequency: int = 5,
    ) -> None:
        if estate not in ESTATE_TYPES:
            raise ValueError(f"estate muss eines von {ESTATE_TYPES} sein, nicht {estate!r}")
        if not 0.0 <= alpha <= 1.0:
            raise ValueError(f"alpha muss in [0, 1] liegen, nicht {alpha}")

        self.engine = engine
        self.estate = estate
        self.user_id = user_id
        self.alpha = alpha
        self.max_features = max_features
        self.min_frequency = min_frequency

        self._loader = DataLoader(engine)
        self.built_at: float = 0.0
        self._build()

    # ------------------------------------------------------------------
    # Aufbau (einmalig, teuer)
    # ------------------------------------------------------------------
    def _build_cleaner(self) -> DataCleaner:
        return DataCleaner(
            self.engine,
            numeric_cols=[
                "property_space", "price", "living_space", "rent_income",
                "brokerage_commission", "notary_fees", "land_registry_entry",
                "energy_demand", "internet_speed_telekom", "house_money",
                "rent_complete", "rent_cold",
            ],
            american_cols=["energy_demand"],
            bool_cols=BOOL_LIKE,
            drop_cols=[
                "zip_code", "city", "total_costs", "price_m2", "url",
                "other_description", "created_at", "updated_at", "address",
                "incidental_purchase_costs", "property_acquisition_tax",
                "brokerage_commission", "notary_fees", "land_registry_entry",
                "agency_id", "id", "title", "available_from", "rent_deposit",
                "ad_type", "listing_type", "rent_extra_costs", "images", "is_online",
            ],
            drop_missing=["estate_type", "price"],
            fill_none_cols=[
                "general_description", "object_description", "place_description",
                "lift", "barrier_free", "garden", "fitted_kitchen", "basement",
                "rented", "available_from", "garage_parking_slots",
                "estate_condition", "interior_quality", "heating_type",
                "energy_performance_certificate_type", "energy_efficiency_class",
                "energy_demand", "total_costs", "building_year", "living_space",
                "rent_cold", "sleeping_rooms", "house_money", "bathrooms", "floor",
                "energy_source", "internet_speed_telekom",
            ],
            fill_strategies={
                "heating_type": lambda df, col: df[col].fillna("Unbekannt"),
                "estate_condition": lambda df, col: df[col].fillna("Unbekannt"),
                "interior_quality": lambda df, col: df[col].fillna("Unbekannt"),
                "energy_performance_certificate_type": lambda df, col: df[col].fillna("Unbekannt"),
                "energy_efficiency_class": lambda df, col: df[col].fillna("Unbekannt"),
                "general_description": lambda df, col: df[col].fillna(""),
                "object_description": lambda df, col: df[col].fillna(""),
                "place_description": lambda df, col: df[col].fillna(""),
            },
        )

    def _build(self) -> None:
        cleaner = self._build_cleaner()

        # Nur die fuer diesen Nutzer sichtbaren Objekte (+ seine Favoriten) laden.
        # -> jede Empfehlung liegt im SearchResults-Set des Nutzers, GET /houses/{id}
        #    liefert 200 statt 403.
        df = self._loader.load_visible_from_db(self.estate, self.user_id)
        df = cleaner.filter_listing_types(df, cleaner.BUY_LISTING_TYPES)

        # id / is_online liegen in drop_cols -> vor preprocessing nach Index sichern.
        online_by_index = df["is_online"].astype(bool)
        reference = df[["id", "title", "url", "price"]].copy()

        df = cleaner.preprocessing(df, False)
        if df is None:
            raise RuntimeError(f"DataCleaner.preprocessing lieferte None fuer {self.estate}")
        df["estate_type"] = df["estate_type"].replace(_ESTATE_TYPE_RENAME)

        struct_df, tfidf_df = self._engineer_features(df)
        idx = struct_df.index

        self._struct: np.ndarray = struct_df.to_numpy()
        self._tfidf: np.ndarray = tfidf_df.loc[idx].to_numpy()
        self._ids: np.ndarray = reference.loc[idx, "id"].to_numpy()
        self._online: np.ndarray = online_by_index.reindex(idx).fillna(False).to_numpy()
        self._reference = reference.drop_duplicates("id").set_index("id")
        self.built_at = time.monotonic()

        logger.info(
            "recommender[%s] gebaut: struct=%s tfidf=%s (%d online-Kandidaten)",
            self.estate, self._struct.shape, self._tfidf.shape, int(self._online.sum()),
        )

    def _engineer_features(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        fe = FeatureEngineering()
        df_text_removed, tfidf_df = fe.text_tokenization(
            df, TEXT_COLS, max_features=self.max_features
        )
        df_feat = fe.one_hot_encoding(
            df_text_removed, min_frequency=self.min_frequency, drop_nan_rows=False
        )
        df_feat[BOOL_LIKE] = df_feat[BOOL_LIKE].astype(float)
        df_feat = self._standardize_numeric(df_feat)

        n_nan = int(df_feat.select_dtypes("number").isna().sum().sum())
        if n_nan:
            raise ValueError(f"{n_nan} NaN-Werte in der Feature-Matrix ({self.estate})")

        return df_feat.select_dtypes(["float", "int"]), tfidf_df

    @staticmethod
    def _standardize_numeric(df_feat: pd.DataFrame) -> pd.DataFrame:
        df_feat = df_feat.copy()
        scale_cols = [
            c for c in df_feat.select_dtypes(["float", "int"]).columns
            if c not in set(BOOL_LIKE)
            and not set(df_feat[c].dropna().unique()) <= {0.0, 1.0}
        ]
        for c in scale_cols:
            if df_feat[c].isna().any():
                df_feat[c] = df_feat[c].fillna(df_feat[c].median())

        skewed = [c for c in scale_cols if (df_feat[c] >= 0).all()]
        df_feat[skewed] = np.log1p(df_feat[skewed])
        df_feat[scale_cols] = StandardScaler().fit_transform(df_feat[scale_cols])
        return df_feat

    @staticmethod
    def _minmax(v: np.ndarray) -> np.ndarray:
        """Min-Max-Skalierung eines 1-D-Vektors auf ``[0, 1]``."""
        lo, hi = float(np.nanmin(v)), float(np.nanmax(v))
        if hi <= lo:
            return np.zeros_like(v, dtype=float)
        return (v - lo) / (hi - lo)

    # ------------------------------------------------------------------
    # Abfrage (billig, pro Request)
    # ------------------------------------------------------------------
    def recommend(self, favorite_ids: Iterable[int], top_n: int = 20) -> list[Recommendation]:
        top_n = max(int(top_n), 0)
        wanted = {int(x) for x in favorite_ids}
        fav_mask = np.isin(self._ids, list(wanted))
        if not fav_mask.any():
            raise NoFavoritesError(
                f"keine der {len(wanted)} Favoriten-IDs im {self.estate}-Kauf-Feature-Set"
            )

        # k x n Cosine-Similarity, ueber die k Favoriten gemittelt -> n-Vektor.
        struct_sim = cosine_similarity(self._struct[fav_mask], self._struct).mean(axis=0)
        text_sim = cosine_similarity(self._tfidf[fav_mask], self._tfidf).mean(axis=0)
        combined = self.alpha * self._minmax(text_sim) + (1 - self.alpha) * self._minmax(struct_sim)

        candidate = (~fav_mask) & self._online
        cand_ids = self._ids[candidate]
        cand_scores = combined[candidate]
        order = np.argsort(cand_scores)[::-1][:top_n]

        picked_ids = cand_ids[order]
        picked_scores = cand_scores[order]
        rows = self._reference.loc[picked_ids]
        titles = rows["title"].tolist()
        urls = rows["url"].tolist()
        prices = rows["price"].tolist()

        results: list[Recommendation] = []
        for k in range(len(order)):
            price = prices[k]
            results.append(
                Recommendation(
                    id=int(picked_ids[k]),
                    title=str(titles[k]),
                    url=str(urls[k]),
                    price=None if price is None or pd.isna(price) else float(price),
                    similarity=float(picked_scores[k]),
                )
            )
        return results

    def recommend_for_user(self, top_n: int = 20) -> list[Recommendation]:
        favorite_ids = self._loader.load_favorite_ids(self.estate, self.user_id)
        return self.recommend(favorite_ids, top_n)


# ----------------------------------------------------------------------
# Prozess-lokale Factory mit TTL-Cache
# ----------------------------------------------------------------------
_TTL_SECONDS = 3600
_cache: dict[tuple[str, int], PropertyRecommender] = {}
_lock = threading.Lock()


def get_recommender(
    estate: str,
    user_id: int,
    *,
    engine: Engine | None = None,
    **kwargs,
) -> PropertyRecommender:
    """Gecachter Recommender pro (estate, user_id).

    Der Aufbau ist teuer (sichtbaren Katalog laden + fitten), deshalb wird pro
    Nutzer und Estate-Typ eine Instanz fuer ``_TTL_SECONDS`` gehalten. Follow-up:
    bei vielen Nutzern waechst der Cache linear -- dann ein Max-Entries-Limit
    ergaenzen.
    """
    key = (estate, user_id)
    with _lock:
        inst = _cache.get(key)
        if inst is not None and time.monotonic() - inst.built_at < _TTL_SECONDS:
            return inst

        _cache.pop(key, None)  # alte Matrix vor dem Neubau freigeben
        if engine is None:
            from backend.database.models import engine as shared_engine

            engine = shared_engine

        inst = PropertyRecommender(engine, estate, user_id, **kwargs)
        _cache[key] = inst
        return inst
