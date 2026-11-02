from fastapi import FastAPI, Depends, Cookie, HTTPException, Response
from app.database import Session, Base, get_db, engine
from app.models import User
from app.schemas import UserCreate, UserList
import jwt
from app.auth import SECRET_KEY, ALGORITHM

Base.metadata.create_all(bind=engine)

app = FastAPI()

def authenticate(
        access_token: str | None = Cookie(default=None),
        db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )

    try:
        payload = jwt.decode(
            access_token,
            SECRET_KEY,
            algorithms=ALGORITHM
        )

        user_id = int(payload["sub"])

    except:
        raise HTTPException(
            status_code=401,
            detail="Invailid Token"
        )

    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Not found"
        )

    return user


@app.get("/", response_model=list[UserList])
def list_users(
    db: Session = Depends(get_db)
):
    users = db.query(User).all()

    return users

@app.get("/{user_id}", response_model=UserList)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    users = db.query(User).get(user_id)

    return users

@app.post("/", response_model=UserCreate)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    new_user = User(
        name = user.name,
        email = user.email
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user