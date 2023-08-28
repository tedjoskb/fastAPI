from datetime import timedelta, datetime
from http.client import HTTPException
from sqlite3 import IntegrityError
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy.testing import db
from starlette import status
from starlette.responses import JSONResponse

from database import SessionLocal
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = '47524923acc13e17f45fd29e6b53af4031d4de983fad6338af715baac26a0019'
ALGORITHM  = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

def get_db():
    db = SessionLocal()
    try :
        yield db
    finally:
        db.close()


db_depedency = Annotated[Session, Depends(get_db)]

def authenticate_user(username:str, password:str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password,user.hashed_password):
        return False
    return user


def create_access_token(username:str, user_id: int,role:str, expires_delta: timedelta):
    encode = {'sub' : username, 'id':user_id,'role':role}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token : Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: int = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="couldn't validate user")

        return {'username': username, 'id':user_id,'user_role':user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="couldn't validate user")



class CreateUserRequest(BaseModel):
    username : str = Field(min_length=3, max_length=255)
    email : str  = Field(min_length=3, max_length=255)
    first_name : str  = Field(min_length=3, max_length=255)
    last_name : str  = Field(min_length=3, max_length=255)
    password: str = Field(min_length=3, max_length=255)
    role: str = Field(min_length=3, max_length=255)
    phone_number: str = Field(min_length=3, max_length=255)

class Token(BaseModel):
    access_token : str
    token_type : str

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_depedency, create_user_request: CreateUserRequest):
    try:
        existing_user = db.query(Users).filter(Users.username == create_user_request.username).first()
        if existing_user:
            error_message = {"message": "Username already exists"}
            return JSONResponse(content=error_message, status_code=status.HTTP_400_BAD_REQUEST)

        create_user_model = Users(
            email=create_user_request.email,
            username=create_user_request.username,
            first_name=create_user_request.first_name,
            last_name=create_user_request.last_name,
            role=create_user_request.role,
            hashed_password=bcrypt_context.hash(create_user_request.password),
            is_active=True,
            phone_number = create_user_request.phone_number
        )
        db.close()
        db.begin()
        db.add(create_user_model)
        db.commit()
        success_message = {"message": "User created successfully"}
        return JSONResponse(content=success_message, status_code=status.HTTP_201_CREATED)
    except IntegrityError as e:
        db.rollback()
        error_message = {"message": "Failed to create user. Integrity Error: Username or Email already exists"}
        return JSONResponse(content=error_message, status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        db.rollback()
        error_message = {"message": f"Failed to create user. Error: {str(e)}"}
        return JSONResponse(content=error_message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)



@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_depedency):
    user = authenticate_user(form_data.username,form_data.password,db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="couldn't validate user")

    token = create_access_token(
        user.username,
        user.id,
        user.role,
        timedelta(minutes=20))

    return {'access_token': token, 'token_type' : 'bearer'}


#Exceptions
def get_user_exception():
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return credentials_exception


def token_exception():
    token_exception_response = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return token_exception_response
