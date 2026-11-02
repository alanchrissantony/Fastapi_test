from fastapi import FastAPI, Depends, Cookie, HTTPException, Response
from app.database import Session, Base, get_db, engine
from app.models import User
from app.schemas import UserRegister, UserLogin, UserList
import jwt
from app.auth import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, hash_password, verify_password, create_token

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
            algorithms=[ALGORITHM]
        )

        user_id = int(payload["sub"])

    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Not found"
        )

    return user


@app.post("/register", response_model=UserList, status_code=201)
def register(
    user: UserRegister,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = User(
        name = user.name,
        email = user.email,
        password_hash = hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.post("/login", response_model=UserList)
def login(
    user: UserLogin,
    response: Response,
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.email == user.email).first()

    if db_user is None or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    response.set_cookie(
        key="access_token",
        value=create_token(db_user.id),
        httponly=True,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    return db_user

@app.post("/logout")
def logout(
    response: Response
):
    response.delete_cookie("access_token")

    return {"message": "Logged out"}

@app.get("/me", response_model=UserList)
def me(
    user: User = Depends(authenticate)
):
    return user
