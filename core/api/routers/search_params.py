from fastapi import status, HTTPException, Depends, Path, APIRouter
from database.models import SearchParams, get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("search_params", status_code=status.HTTP_200_OK)
def get_search_params(db: Session = Depends(get_db)):
    search_params = db.query(SearchParams).all()
    if search_params is not None:
        return search_params
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No search params found")

@router.get("search_params/{id}", status_code=status.HTTP_200_OK)
def get_search_params_by_id(db: Session = Depends(get_db), search_params_id: int = Path(gt=0)):
    search_param = db.query(SearchParams).filter(SearchParams.id == search_params_id).first()
    if search_param is not None:
        return search_param
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"search param with id: {search_params_id} not found")