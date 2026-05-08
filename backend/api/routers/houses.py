from fastapi import status, HTTPException, Depends, Path, APIRouter
from backend.database.models import House, get_db, SearchParams, SearchResults
from sqlalchemy.orm import Session
from backend.api.auth.oauth2 import get_current_user
from sqlalchemy import select

router = APIRouter(
    prefix="/houses",
    tags=["House"]
)

@router.get("/", status_code=status.HTTP_200_OK)
def get_houses(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    house_ids = (
        db.query(SearchResults.house_id)
        .join(SearchParams, SearchResults.search_params_id == SearchParams.id)
        .filter(SearchParams.user_id == current_user.id)
    )

    houses = db.query(House).filter(House.id.in_(house_ids)).all()
    
    if houses is not None:
        return houses
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No houses found")

@router.get("/{house_id}", status_code=status.HTTP_200_OK)
def get_house_by_id(house_id: int = Path(gt=0), db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    
    allowed_house_ids = (
        db.query(SearchResults.house_id).join(SearchParams, SearchResults.search_params_id == SearchParams.id).filter(SearchParams.user_id == current_user.id).all()
    )

    allowed_house_ids = [id[0] for id in allowed_house_ids]

    house = (db.query(House).filter(House.id == house_id).first())

    if house is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"House with id {house_id} not found")

    if house.id not in allowed_house_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to retrieve this house")

    return house