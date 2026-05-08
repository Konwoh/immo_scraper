from fastapi import status, HTTPException, Depends, Path, APIRouter
from backend.database.models import Apartment, get_db, SearchParams, SearchResults
from sqlalchemy.orm import Session
from backend.api.auth.oauth2 import get_current_user

router = APIRouter(
    prefix="/apartments",
    tags=["Apartment"]
)

@router.get("/", status_code=status.HTTP_200_OK)
def get_apartmens(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    apartment_ids = (
        db.query(SearchResults.apartment_id)
        .join(SearchParams, SearchResults.search_params_id == SearchParams.id)
        .filter(SearchParams.user_id == current_user.id)
    )

    apartments = db.query(Apartment).filter(Apartment.id.in_(apartment_ids)).all()
    
    if apartments:
        return apartments
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No apartments found") 

@router.get("/{apartment_id}", status_code=status.HTTP_200_OK)
def get_apartment_by_id(db: Session = Depends(get_db), apartment_id: int = Path(gt=0), current_user = Depends(get_current_user)):
    allowed_house_ids = (
        db.query(SearchResults.apartment_id).join(SearchParams, SearchResults.search_params_id == SearchParams.id).filter(SearchParams.user_id == current_user.id).all()
    )

    allowed_house_ids = [id[0] for id in allowed_house_ids]

    apartment = (db.query(Apartment).filter(Apartment.id == apartment_id).first())

    if apartment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"House with id {apartment_id} not found")

    if apartment.id not in allowed_house_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to retrieve this house")
    
    return apartment