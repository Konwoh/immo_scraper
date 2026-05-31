from fastapi import status, HTTPException, Depends, Path, APIRouter, Response
from backend.database.models import Property, get_db, SearchParams, SearchResults
from sqlalchemy.orm import Session
from backend.api.auth.oauth2 import get_current_user

router = APIRouter(
    prefix="/properties",
    tags=["Property"]
)

@router.get("/", status_code=status.HTTP_200_OK)
def get_properties(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    property_ids = (
        db.query(SearchResults.property_id)
        .join(SearchParams, SearchResults.search_params_id == SearchParams.id)
        .filter(SearchParams.user_id == current_user.id)
    )

    properties = db.query(Property).filter(Property.id.in_(property_ids)).all()
    
    if properties is not None:
        return properties
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No properties found")

@router.get("/{property_id}", status_code=status.HTTP_200_OK)
def get_property_by_id(property_id: int = Path(gt=0), db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    
    allowed_property_ids = (
        db.query(SearchResults.property_id).join(SearchParams, SearchResults.search_params_id == SearchParams.id).filter(SearchParams.user_id == current_user.id).all()
    )

    allowed_property_ids = [id[0] for id in allowed_property_ids]

    property = (db.query(Property).filter(Property.id == property_id).first())

    if property is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Property with id {property_id} not found")

    if property.id not in allowed_property_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to retrieve this property")

    return property

@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_property(property_id: int = Path(gt=0), db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    property = db.query(Property).filter(Property.id == property_id).first()

    if property is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Property with id {property_id} not found")

    search_result_ids = [
        result_id
        for (result_id,) in (
            db.query(SearchResults.id)
            .join(SearchParams, SearchResults.search_params_id == SearchParams.id)
            .filter(
                SearchResults.property_id == property_id,
                SearchParams.user_id == current_user.id,
            )
            .all()
        )
    ]

    if not search_result_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this property")

    (
        db.query(SearchResults)
        .filter(SearchResults.id.in_(search_result_ids))
        .delete(synchronize_session=False)
    )
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
