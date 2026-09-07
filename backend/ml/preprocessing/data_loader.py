import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

_FAVORITE_FK = {"houses": "house_id", "apartments": "apartment_id", "property": "property_id"}

class DataLoader:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def load_from_db(self, estate: str) -> pd.DataFrame:
        sql_stmt = f"select * from {estate}"
        df = pd.read_sql(sql=sql_stmt, con=self.engine)
        return df

    def load_favorite_ids(self, estate: str, user_id: int) -> set[int]:
        fk = _FAVORITE_FK[estate]
        stmt = text(f"SELECT {fk} FROM favorites WHERE user_id = :uid AND {fk} IS NOT NULL")
        rows = pd.read_sql(sql=stmt, con=self.engine, params={"uid": user_id})
        return set(rows[fk].astype(int))

    def load_visible_from_db(self, estate: str, user_id: int) -> pd.DataFrame:
        """Alle fuer den Nutzer sichtbaren Objekte (aus seinen Suchen) plus dessen
        Favoriten -- damit die Favoriten garantiert in der Feature-Matrix landen.
        `estate` / `fk` stammen aus kontrollierten Dicts, kein User-Input."""
        fk = _FAVORITE_FK[estate]
        stmt = text(
            f"""
            SELECT e.* FROM {estate} e
            WHERE e.id IN (
                SELECT sr.{fk} FROM search_results sr
                JOIN search_params sp ON sp.id = sr.search_params_id
                WHERE sp.user_id = :uid AND sr.{fk} IS NOT NULL
                UNION
                SELECT f.{fk} FROM favorites f
                WHERE f.user_id = :uid AND f.{fk} IS NOT NULL
            )
            """
        )
        return pd.read_sql(sql=stmt, con=self.engine, params={"uid": user_id})
    
    def load_house_favorites_from_db(self) -> pd.DataFrame:
        sql_stmt = f"SELECT h.* FROM favorites f LEFT JOIN houses h ON h.id = f.house_id where f.house_id IS NOT Null"
        df = pd.read_sql(sql=sql_stmt, con=self.engine)
        return df

    def load_apartment_favorites_from_db(self) -> pd.DataFrame:
        sql_stmt = f"SELECT a.* FROM favorites f LEFT JOIN apartments a ON a.id = f.apartment_id where f.apartment_id IS NOT Null"
        df = pd.read_sql(sql=sql_stmt, con=self.engine)
        return df

    def load_property_favorites_from_db(self) -> pd.DataFrame:
        sql_stmt = f"SELECT p.* FROM favorites f LEFT JOIN property p ON p.id = f.property_id where f.property_id IS NOT Null"
        df = pd.read_sql(sql=sql_stmt, con=self.engine)
        return df
