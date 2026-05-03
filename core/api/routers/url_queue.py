from fastapi import status, HTTPException, Depends, Path, APIRouter
from database.models import UrlQueue, get_db, SearchParams
from sqlalchemy.orm import Session
from core.schemas.pydantic_models import UrlQueueRequest
from core.api.oauth2 import get_current_user

router = APIRouter(
    prefix="/url_queue",
    tags=["URL_Queue"]
)

@router.get("/", status_code=status.HTTP_200_OK)
def get_url_queue(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    url_queue = (db.query(UrlQueue).join(SearchParams, UrlQueue.search_params_id == SearchParams.id).filter(SearchParams.user_id == current_user.id).all())
    if url_queue is not None:
        return url_queue
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No url queue found")

@router.get("/{url_queue_id}", status_code=status.HTTP_200_OK)
def get_url_queue_by_id(db: Session = Depends(get_db), url_queue_id: int = Path(gt=0), current_user = Depends(get_current_user)):
    url_queue_obj = db.query(UrlQueue).filter(UrlQueue.id == url_queue_id).first()
    if url_queue_obj is not None:
        search_param = db.query(SearchParams).filter(SearchParams.id == url_queue_obj.search_params_id).first()
        if search_param is not None and search_param.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to retrieve this url queue")
        return url_queue_obj
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"url queue object with id: {url_queue_id} not found")

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_url_queue(url_queue_request: UrlQueueRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    search_param = db.query(SearchParams).filter(SearchParams.id == url_queue_request.search_params_id, SearchParams.user_id == current_user.id).first()
    
    if search_param is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create this url queue")
    
    new_url_queue_obj = UrlQueue(**url_queue_request.model_dump())
    db.add(new_url_queue_obj)
    db.commit()
    
    return new_url_queue_obj