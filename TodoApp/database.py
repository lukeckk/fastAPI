from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# creates a sqlite database
SQLALCHEMY_DATABASE_URL = 'sqlite:///./todosapp.db'
# look for thread to interact with the database
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})

# connect to postgres database
# match the password (1234) and name (TodoApplicationDatabase)
# SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:1234@localhost/TodoApplicationDatabase'
# engine = create_engine(SQLALCHEMY_DATABASE_URL)


# Create a local session, prevent database to do things automatically, bind to the engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Create a base to control the database such as creating table and interact with it
Base = declarative_base()