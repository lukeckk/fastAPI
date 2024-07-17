from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import Todos, Users
from ..database import SessionLocal
from .auth import get_current_user
from passlib.context import CryptContext

router = APIRouter(
    prefix="/user",
    tags=["user"]
)


# initiate DB connection, fetch information, deliver to users and close the connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(
    get_db)]  #Depends = dependency injection that allows us to do code behind scence such as get_db() then inject to it
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# pydantic class to allow password reset
class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=3)


# returns user's information
@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Users).filter(Users.id == user.get('id')).first()


# change password
@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail="Current password is invalid")

    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()

# change phone number
@router.put("/phonenumber/{phone_number}", status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(user:user_dependency, db: db_dependency, phone_number: str):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    user_model.phone_number = phone_number
    db.add(user_model)
    db.commit()