from fastapi import status, HTTPException, Depends, Path, APIRouter, Response
from database.models import SearchParams, get_db
from sqlalchemy.orm import Session
from core.schemas.pydantic_models import SearchParamRequest
from core.api.oauth2 import get_current_user

router = APIRouter(
    prefix="/search_params",
    tags=["Search Params"]
)

@router.get("/", status_code=status.HTTP_200_OK)
def get_search_params(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    search_params = db.query(SearchParams).filter(SearchParams.user_id == current_user.id).all()
    if search_params is not None:
        return search_params
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No search params found")

@router.get("/{search_params_id}", status_code=status.HTTP_200_OK)
def get_search_params_by_id(db: Session = Depends(get_db), search_params_id: int = Path(gt=0), current_user = Depends(get_current_user)):
    search_param = db.query(SearchParams).filter(SearchParams.id == search_params_id, SearchParams.user_id == current_user.id).first()
    if search_param is not None:
        return search_param
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"search param with id: {search_params_id} not found")

@router.post("/", status_code=status.HTTP_200_OK)
def create_search_param(search_param_request: SearchParamRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    new_search_param = SearchParams(user_id = current_user.id, **search_param_request.model_dump())
    db.add(new_search_param)
    db.commit()
    
@router.delete("/{search_params_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_search_param(db: Session = Depends(get_db), current_user = Depends(get_current_user), search_params_id: int = Path(gt=0)):
    search_param_query = db.query(SearchParams).filter(SearchParams.id == search_params_id)
    
    search_param = search_param_query.first()
    
    if search_param == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"search params with id {search_params_id} does not exist")
    
    if search_param.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to perform request action")

    search_param_query.delete(synchronize_session=False)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{search_params_id}")
def update_search_params(updated_search_params: SearchParamRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user), search_params_id: int = Path(gt=0)):
    search_params_query = db.query(SearchParams).filter(SearchParams.id == search_params_id)
    search_param = search_params_query.first()
    
    if search_param == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"search params with id {search_params_id} does not exist")
    
    if search_param.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to perform request action")
    
    search_params_query.update(updated_search_params.model_dump())
    
    db.commit()