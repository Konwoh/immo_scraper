from fastapi import status, HTTPException, Depends, Path, APIRouter
from database.models import House, get_db
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/houses",
    tags=["House"]
)

@router.get("/", status_code=status.HTTP_200_OK)
def get_houses(db: Session = Depends(get_db)):
    houses = db.query(House).all()
    if houses is not None:
        return houses
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No houses found")

@router.get("/{id}", status_code=status.HTTP_200_OK)
def get_houses_by_id(db: Session = Depends(get_db), house_id: int = Path(gt=0)):
    house = db.query(House).filter(House.id == house_id).first()
    if house is not None:
        return house
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"house with id: {house_id} not found")