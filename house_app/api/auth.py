from typing import Optional
from house_app.config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, ALGORITHM
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from house_app.db.database import SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, APIRouter
from house_app.db.models import UserProfile, RefreshToken
from house_app.db.schema import UserCreateSchema
from jose import jwt
from starlette.requests import Request
from fastapi_limiter.depends import RateLimiter


auth_router = APIRouter(prefix='/auth', tags=['/Auth'])


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


oauth2_schema = OAuth2PasswordBearer(tokenUrl='/auth/login/')
password_context = CryptContext(schemes=['bcrypt'], deprecated="auto")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    return create_access_token(data, expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))


def verify_password(plain_password, hash_password):
    return password_context.verify(plain_password, hash_password)

def get_password_hash(password):
    return password_context.hash(password)


@auth_router.post('/register/',)
async def register(user: UserCreateSchema, db: Session = Depends(get_db)):
    user_db = db.query(UserProfile).filter(UserProfile.username==user.username).first()
    if user_db:
        raise HTTPException(status_code=400, detail='мындай username бар экен')
    new_hash_pass = get_password_hash(user.password)
    new_user = UserProfile(
        fio=user.fio,
        username=user.username,
        date_registered=user.date_registered,
        hashed_password=new_hash_pass,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {'message': 'saved'}


@auth_router.post('/login', dependencies=[Depends(RateLimiter(times=3, seconds=60))])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserProfile).filter(UserProfile.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail='маалымат туура эмеc')
    access_token = create_access_token({'sub': user.username})
    refresh_token = create_refresh_token({'sub': user.username})
    token_db = RefreshToken(token=refresh_token, user_id=user.id)
    db.add(token_db)
    db.commit()
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}


@auth_router.post('/logout')
async def logout(refresh_token: str, db: Session = Depends(get_db)):

    stored_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()

    if not stored_token:
        raise HTTPException(status_code=400, detail='маалымат туура эмеc')

    db.delete(stored_token)
    db.commit()
    return {'message': 'вышли'}


@auth_router.post('/refresh')
async def refresh(refresh_token: str, db: Session = Depends(get_db)):
    token_entry = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()

    if not token_entry:
        raise HTTPException(status_code=400, detail='маалымат туура эмеc')

    access_token = create_access_token({'sub': token_entry.user_id})

    return {'access_token': access_token, 'token_type': 'bearer'}
