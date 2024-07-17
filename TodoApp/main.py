# Main.py only in charge of starting up fastAPI and grab routers
from fastapi import FastAPI
from .models import Base
from .database import engine
from .routers import auth, todos, admin, users
from starlette.staticfiles import StaticFiles

app = FastAPI()

# This creates the database table by importing required info from models and engine
# This will only run if todos.db doesnt exist because it will create it
Base.metadata.create_all(bind=engine)

# start the static files like css and js
app.mount("/static", StaticFiles(directory="TodoApp/static"), name="static")

# compares with the assert response.json() in test_main.py
@app.get("/healthy")
def health_check():
    return {'status': 'healthy'}

# Include the auth file to be on the same port
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)



