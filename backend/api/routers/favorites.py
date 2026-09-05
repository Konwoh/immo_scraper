from typing import Literal
from fastapi import status, HTTPException, Depends, Path, APIRouter, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.database.models import Favorite, House, Apartment, Property, get_db
from backend.api.auth.oauth2 import get_current_user
from backend.schemas.favorites import FavoriteResponse
from backend.schemas.pagination import Page, PaginationDep, paginate

router = APIRouter(prefix="/favorites", tags=["Favorites"])

ESTATE_MODELS = {"house": House, "apartment": Apartment, "property": Property}
ESTATE_FK_FIELD = {"house": "house_id", "apartment": "apartment_id", "property": "property_id"}


@router.get("/", status_code=status.HTTP_200_OK, response_model=Page[FavoriteResponse])
def get_favorites(pagination: PaginationDep, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    query = db.query(Favorite).filter(Favorite.user_id == current_user.id)
    return paginate(query, pagination)


@router.post("/{estate_type}/{estate_id}", status_code=status.HTTP_201_CREATED, response_model=FavoriteResponse)
def add_favorite(
    estate_type: Literal["house", "apartment", "property"],
    estate_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    estate_model = ESTATE_MODELS[estate_type]
    estate = db.query(estate_model).filter(estate_model.id == estate_id).first()
    if estate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{estate_type} with id {estate_id} not found")

    new_favorite = Favorite(user_id=current_user.id, **{ESTATE_FK_FIELD[estate_type]: estate_id})
    db.add(new_favorite)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This estate is already in your favorites")

    db.refresh(new_favorite)
    return new_favorite


@router.delete("/{estate_type}/{estate_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(
    estate_type: Literal["house", "apartment", "property"],
    estate_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    fk_field = ESTATE_FK_FIELD[estate_type]
    favorite_query = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        getattr(Favorite, fk_field) == estate_id,
    )
    if favorite_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite not found")

    favorite_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)