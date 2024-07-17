# This is database models
from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)   # whether user is admin or not
    phone_number = Column(String)
class Todos(Base):
    __tablename__= "todos"  #naming the table
    #below are the columns
    id = Column(Integer, primary_key=True, index=True)  #set this as primary key, index is to increase performance
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))