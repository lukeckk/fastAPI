from datetime import timedelta, datetime, timezone
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse

from ..database import SessionLocal
from ..models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="TodoApp/templates")


# the parameter separates the auth and todos API endpoints in swagger by adding "/author" in the front
router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

# add secret key and algorithm for JWT
SECRET_KEY = "e737e5081cf36c93fff413b4a8f81ea0abdfeccc073d796f057159e827a61b41"
ALGORITHM = "HS256"

# setting up passlib with hashing schemes/algorithm of bcrypt to be used for hashing
# for encoding
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# add a login form for get_current_user() which is later passed in create_todo()
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str

class Token(BaseModel):
    access_token: str
    token_type: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# below is login functionality for full stack app
class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get("email")
        self.password = form.get("password")


db_dependency = Annotated[Session, Depends(
    get_db)]  #Depends = dependency injection that allows us to do code behind scence such as get_db() then inject to it

def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    # verify user exists
    if not user:
        return False
    # verify password is correct
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    # if no False returned, return user
    return user

# for encoding
def create_access_token(username: str, user_id: int, role:str, expires_delta: timedelta):
    # JWT Encoding
    encode = {"sub": username, "id": user_id, "role": role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

# for decoding
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        #sun is the username as set in encoding method
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")

        return {"username": username, "id": user_id, "user_role": user_role}
    # throw exceptions below
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    # ** dict() is not used here because this user class has 'password' while the users table is ''hashed_password'
    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        is_active=True,
        phone_number=create_user_request.phone_number
    )
    db.add(create_user_model)
    db.commit()

@router.post("/token", response_model=Token)
async def login_for_access_token(response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    # Get result from authenticate_user() whether True or False and print failed or successful authentication
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise False
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=60))

    # setting cookies
    response.set_cookie(key="access_token", value=token, httponly=True)

    return {"access_token": token, "token_type": "bearer"}

@router.get("/", response_class=HTMLResponse)
async def authentication_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

#  for app
@router.post("/", response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    try:
        form = LoginForm(request)
        await form.create_oauth_form()
        response = RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

        validate_user_cookie = await login_for_access_token(reponse=response, form_data=form, db=db)

        if not validate_user_cookie:
            msg = "Incorrect Username or Password"
            return templates.TemplateResponse("login.html", {"request": request, "msg": msg})
        return response
    except HTTPException:
        msg = "Unknown Error"
        return templates.TemplateResponse("login.html", {"request": request, "msg": msg})





