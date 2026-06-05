from fastapi import status, HTTPException, Depends, Path, APIRouter, Response
from backend.database.models import Apartment, get_db, SearchParams, SearchResults
from sqlalchemy.orm import Session
from backend.api.auth.oauth2 import get_current_user
from backend.schemas.Apartment import ApartmentResponse
from backend.schemas.pagination import Page, PaginationDep, paginate

router = APIRouter(
    prefix="/apartments",
    tags=["Apartment"]
)

@router.get("/", status_code=status.HTTP_200_OK, response_model=Page[ApartmentResponse])
def get_apartments(pagination: PaginationDep, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    apartment_ids = (
        db.query(SearchResults.apartment_id)
        .join(SearchParams, SearchResults.search_params_id == SearchParams.id)
        .filter(SearchParams.user_id == current_user.id)
    )

    query = db.query(Apartment).filter(Apartment.id.in_(apartment_ids))
    
    apartments = paginate(query, pagination)
    
    if apartments is not None:
        return apartments
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No apartments found") 

@router.get("/{apartment_id}", status_code=status.HTTP_200_OK, response_model=ApartmentResponse)
def get_apartment_by_id(db: Session = Depends(get_db), apartment_id: int = Path(gt=0), current_user = Depends(get_current_user)):
    allowed_apartment_ids = (
        db.query(SearchResults.apartment_id).join(SearchParams, SearchResults.search_params_id == SearchParams.id).filter(SearchParams.user_id == current_user.id).all()
    )

    allowed_apartment_ids = [id[0] for id in allowed_apartment_ids]

    apartment = (db.query(Apartment).filter(Apartment.id == apartment_id).first())

    if apartment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Apartment with id {apartment_id} not found")

    if apartment.id not in allowed_apartment_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to retrieve this apartment")
    
    return apartment

@router.delete("/{apartment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_apartment(db: Session = Depends(get_db), current_user = Depends(get_current_user), apartment_id: int = Path(gt=0)):
    apartment = db.query(Apartment).filter(Apartment.id == apartment_id).first()
    
    if apartment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Apartment with id {apartment_id} not found")

    search_result_ids = [
        result_id
        for (result_id,) in (
            db.query(SearchResults.id)
            .join(SearchParams, SearchResults.search_params_id == SearchParams.id)
            .filter(
                SearchResults.apartment_id == apartment_id,
                SearchParams.user_id == current_user.id,
            )
            .all()
        )
    ]

    if not search_result_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this apartment")

    (
        db.query(SearchResults)
        .filter(SearchResults.id.in_(search_result_ids))
        .delete(synchronize_session=False)
    )
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
