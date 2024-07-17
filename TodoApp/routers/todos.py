from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path, Request, Form
from starlette import status
from .. import models
from ..models import Todos
from ..database import engine, SessionLocal
from .auth import get_current_user
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from starlette import status

# the parameter separates the auth and todos API endpoints in swagger by adding "/author" in the front
router = APIRouter(
    prefix="/todos",
    tags=["todos"]
)


# important step to instantiate templates
templates = Jinja2Templates(directory="TodoApp/templates")


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

# parameter sets '/' as the home page after the prefix 'todos'
@router.get("/", response_class=HTMLResponse)
# second parameter sets up connection with database
async def read_add_by_user(request: Request, db: Session = Depends(get_db)):
    todos = db.query(models.Todos).filter(models.Todos.owner_id == 1).all()

    return templates.TemplateResponse("home.html", {"request": request, "todos": todos})

# renders the add-todo.html using .get()
@router.get("/add-todo", response_class=HTMLResponse)
async def add_new_todo(request: Request):
    return templates.TemplateResponse("add-todo.html", {"request": request})

# add user using .post()
@router.post("/add-todo", response_class=HTMLResponse)
async def create_todo(request: Request, title: str = Form(...), description: str = Form(...), priority: int = Form(...), db: Session = Depends(get_db)):
    todo_model = models.Todos()
    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority
    #  set to false as default
    todo_model.complete = False
    todo_model.owner_id = 1

    db.add(todo_model)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

@router.get("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):

    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()

    return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": todo})

@router.post("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo_commit(request: Request, todo_id: int, title: str = Form(...), description: str = Form(...), priority: int = Form(...), db: Session = Depends(get_db)):
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority

    db.add(todo_model)
    db.commit()
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

@router.get("/delete/{todo_id}")
async def delete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).filter(models.Todos.owner_id == 1).first()

    if todo_model is None:
        return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

    # if found, .delete()
    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

@router.get("/complete/{todo_id}", response_class=HTMLResponse)
async def complete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()

    #  switch complete from False to True or True to False
    todo.complete = not todo.complete

    db.add(todo)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

'''
Below are functions for API, not full stack application

# Create Pydantic to validate post request
# No need to create id and make it optional because SQLAchemy will do it automatically since it is the primary key
class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool

# templating here to home.html
@router.get("/test")
async def test(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


# Return all data from the Todos table
# @router.get("/", status_code=status.HTTP_200_OK)
# async def read_all(db: db_dependency):
#     return db.query(Todos).all()


# # Return all data based on the use that is logged in
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Todos).filter(Todos.owner_id == user.get("id")).all()


# GET specific to-do by its id and to the user that is logged in
@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()  #filter only the id and return the first match to boost performance
    if todo_model is not None:  # return the data if there is any, if not, return exception below
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found.")


# POST
@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest):
    # Check if get_current_user is successful
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    todo_model = Todos(**todo_request.dict(), owner_id=user.get("id"))
    #Below adds to database
    db.add(todo_model)
    db.commit()


# PUT
@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).delete()

    db.commit()
'''
