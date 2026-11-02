from os import getenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

Session = sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = Session()

    try:
        yield db
    finally:
        db.close()