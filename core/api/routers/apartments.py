from fastapi import status, HTTPException, Depends, Path, APIRouter
from database.models import Apartment, get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/apartments", status_code=status.HTTP_200_OK)
def get_apartmens(db: Session = Depends(get_db)):
    apartments = db.query(Apartment).all()
    if apartments is not None:
        return apartments
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No apartments found") 

@router.get("/apartments/{apartment_id}", status_code=status.HTTP_200_OK)
def get_apartment_by_id(db: Session = Depends(get_db), apartment_id: int = Path(gt=0)):
    apartment = db.query(Apartment).filter(Apartment.id == apartment_id).first()
    if apartment is not None:
        return apartment
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"apartment with id {apartment_id} not found") 