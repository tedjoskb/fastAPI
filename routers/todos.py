from typing import Annotated

from pydantic import  BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends,HTTPException,Path
from starlette import status
from starlette.responses import JSONResponse

import models
from models import Todos
from database import SessionLocal
from .auth import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try :
        yield db
    finally:
        db.close()


db_depedency = Annotated[Session, Depends(get_db)]
user_depedency = Annotated[dict, Depends(get_current_user)]

class TodoRequest(BaseModel):
    title : str = Field(min_length=3, max_length=255)
    description : str  = Field(min_length=3, max_length=255)
    priority : int = Field(gt=0, lt=6)
    complete : bool

    class Config:
        json_schema_extra = {
            'example': {
                'title': 'A new Book',
                'description': 'A new description',
                'priority': 5,
                'complete': False
            }
        }


@router.get("/",status_code=status.HTTP_200_OK)
async def read_all(user:user_depedency,db: db_depedency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    try:
        todos = db.query(Todos).filter(Todos.owner_id == user.get('id')).all()
        return todos
    except Exception as e:
        error_message = {"message": f"An error occurred: {str(e)}"}
        return JSONResponse(content=error_message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/todo/{todo_id}",status_code=status.HTTP_200_OK)
async def read_todo(user:user_depedency,db: db_depedency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    try:
        todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()

        if todo_model is not None:
            todo_info = {
                "message": "Todo found",
                "todo": todo_model
            }
            return todo_info
        else:
            error_message = {"message": "Todo not found"}
            return JSONResponse(content=error_message, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        error_message = {"message": f"An error occurred: {str(e)}"}
        return JSONResponse(content=error_message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/todo/",status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_depedency, db : db_depedency, todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    todo_model = Todos(**todo_request.model_dump(), owner_id = user.get('id'))
    try:
        db.add(todo_model)
        db.commit()
        success_message = {"message": "Todo created successfully"}
        return JSONResponse(content=success_message, status_code=status.HTTP_201_CREATED)
    except Exception as e:
        db.rollback()
        error_message = {"message": f"Failed to create todo. Error: {str(e)}"}
        return JSONResponse(content=error_message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.put("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def update_todo(
                      user:user_depedency,
                      db: db_depedency,
                      todo_request: TodoRequest,
                      todo_id: int = Path(gt=0)
                      ):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    try:
        todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
        if todo_model is None:
            raise HTTPException(status_code=404, detail='Todo not found')

        todo_model.title = todo_request.title
        todo_model.description = todo_request.description
        todo_model.priority = todo_request.priority
        todo_model.complete = todo_request.complete

        db.commit()
        return {"message": "Todo updated successfully"}  # Keterangan pembaruan berhasil
    except Exception as e:
        db.rollback()
        error_message = {"message": f"An error occurred: {str(e)}"}
        return JSONResponse(content=error_message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.delete("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def delete_todo(
                        user:user_depedency,
                        db: db_depedency,
                        todo_id: int):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    try:
        todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
        if todo_model is None:
            raise HTTPException(status_code=404, detail='Todo not found')

        db.delete(todo_model)
        db.commit()
        return {"message": "Todo deleted successfully"}  # Keterangan penghapusan berhasil
    except Exception as e:
        db.rollback()
        error_message = {"message": f"data tidak ditemukan: Id {str(todo_id)}"}
        return JSONResponse(content=error_message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

