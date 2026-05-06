from fastapi import status, HTTPException, Depends, APIRouter
from backend.database.models import get_db, User
from sqlalchemy.orm import Session
from backend.schemas.user import UserRequest, UserResponse
from backend.api.auth.utils import verify_password, get_password_hash

router = APIRouter(
    prefix="/user",
    tags=["User"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def create_user(create_user_request: UserRequest, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(create_user_request.password)
    create_user_request.password = hashed_password
    new_user = User(**create_user_request.model_dump())
    db.add(new_user)
    db.commit()
    
    return new_user
@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is not None:
        return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {user_id} not found")