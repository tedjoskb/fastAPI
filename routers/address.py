import sys
sys.path.append("...")

from typing import Annotated,Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends,HTTPException,Path
from starlette import status
from starlette.responses import JSONResponse
import models
from models import Address
from database import SessionLocal,engine
from .auth import get_current_user, get_user_exception

router = APIRouter(
    prefix="/address",
    tags=["address"],
    responses={404:{"description":"not found"}}
)

def get_db():
    db = SessionLocal()
    try :
        yield db
    finally:
        db.close()


db_depedency = Annotated[Session, Depends(get_db)]
user_depedency = Annotated[dict, Depends(get_current_user)]


class Address(BaseModel):
    address1 : str
    address2 : Optional[str]
    city: str
    state: str
    country: str
    postalcode: str
    apt_num: str


@router.post("/")
async def create_address(address:Address,
                         user: user_depedency,
                         db: db_depedency
                         ):
    if user is None:
        raise get_user_exception()
    address_model = models.Address()
    address_model.address1 = address.address1
    address_model.address2 = address.address2
    address_model.city = address.city
    address_model.state = address.state
    address_model.country = address.country
    address_model.postalcode = address.postalcode
    address_model.apt_num = address.apt_num

    db.add(address_model)
    db.flush()

    user_model = db.query(models.Users).filter(models.Users.id == user.get('id')).first()
    user_model.address_id = address_model.id

    db.add(user_model)
    db.commit()