import os
from collections.abc import Generator

from dotenv import load_dotenv #loads the variables 
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

#Load variables from the .env file 
load_dotenv()

#Read the database connection URl 
DATABASE_URL = os.getenv("DATABASE_URL")

#Stop the application immediately if database_url is missing
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Add it to the project's env file."
    )


#this engine manages connection between Python & postgres

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

#sessionlocal creates individual database sessions 

SessionLocal = sessionmaker(
    bind= engine,
    autoflush=False,
    autocommit = False,
)

#All SQLAlchemy database models will inherit from this class 
class Base(DeclarativeBase):
    pass

def get_db() -> Generator[Session, None, None]:
    """
    Create a database session for one API request.

    The session is always closed after the request finishes.
    """
    db = SessionLocal() #creates a new database session

    try:
        yield db
    finally:
        db.close()