import os
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session, load_only

from backend.api.auth.oauth2 import get_current_user
from backend.api.rate_limit import limiter
from backend.database.models import Apartment, House, User, get_db
from backend.ml.recommendation.recommend import get_recommender
from backend.schemas.recommendation import RecommendationItem, RecommendationResponse
from backend.shared.exceptions import NoFavoritesError
from backend.shared.loki_handler import get_loki_logger

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

recommendation_logger = get_loki_logger(
    "recommendations", {"app": "api", "env": os.getenv("ENV", "dev")}
)

_ESTATE_TABLE = {"house": "houses", "apartment": "apartments"}
_ESTATE_MODEL = {"house": House, "apartment": Apartment}
_HYDRATE_COLS = (
    "id", "title", "url", "price", "city", "zip_code",
    "living_space", "rooms", "estate_type", "images",
)


@router.get(
    "/{estate_type}",
    status_code=status.HTTP_200_OK,
    response_model=RecommendationResponse,
)
@limiter.limit("20/minute")
def get_recommendations(
    request: Request,
    estate_type: Literal["house", "apartment"],
    top_n: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RecommendationResponse:
    try:
        recommender = get_recommender(_ESTATE_TABLE[estate_type], current_user.id)
    except HTTPException:
        raise
    except Exception as exc:  # ValueError (NaN-Matrix), DB-Fehler, ...
        recommendation_logger.error(
            "recommender build failed for %s: %s", estate_type, exc
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Der Empfehlungsdienst ist derzeit nicht verfuegbar.",
        ) from exc

    try:
        results = recommender.recommend_for_user(top_n=top_n)
    except NoFavoritesError:
        return RecommendationResponse(count=0, items=[])

    model = _ESTATE_MODEL[estate_type]
    sim_by_id = {r.id: r.similarity for r in results}
    rows = (
        db.query(model)
        .options(load_only(*(getattr(model, c) for c in _HYDRATE_COLS)))
        .filter(model.id.in_(sim_by_id))
        .all()
    )
    rows_by_id = {row.id: row for row in rows}

    items = [
        RecommendationItem(
            **{c: getattr(row, c) for c in _HYDRATE_COLS},
            similarity=sim_by_id[row.id],
        )
        for r in results
        if (row := rows_by_id.get(r.id)) is not None  # Zeile seit Build entfernt -> skip
    ]
    return RecommendationResponse(count=len(items), items=items)
