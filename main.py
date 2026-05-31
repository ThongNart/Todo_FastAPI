from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from typing import Dict, Annotated

from schemas import  TodoCreate, TodoResponse, TodoUpdate

from sqlalchemy import select
from sqlalchemy.orm import Session

import models 
from database import get_db, Base, engine






# Create database at startup, if database not already created
Base.metadata.create_all(bind=engine)

#Create Fast API app
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")




# hard code data
# This data will reset when server goes down
todo_items: list[Dict] = [
    {
        "id": 1,
        "title": "Finish FastAPI setup",
        "description": "Create virtual environment, install dependencies, and run the development server.",
        "urgency_level": "high",
    },
    {
        "id": 2,
        "title": "Write API endpoint docs",
        "description": "Add clear descriptions for todo CRUD endpoints and expected request/response formats.",
        "urgency_level": "medium",
    },
    {
        "id": 3,
        "title": "Clean project structure",
        "description": "Organize files into folders such as routes, models, and services for easier maintenance.",
        "urgency_level": "low",
    },
]




#############
# HTML ROUTES
#############


# @app.get("/", include_in_schema = False, name="home")
# def home_page(request: Request):
#     return templates.TemplateResponse(
#         request,
#         "home.html", {"todos": todo_items, "title": "Todo List Home Page"},
#         status_code=200
#     )


@app.get("/", include_in_schema = False, name="home")
def home_page(request: Request, db: Annotated[Session, Depends(get_db)]):

    result = db.execute(
        select(models.TodoItem).order_by(models.TodoItem.created_at.desc())
    )
    todo_list = result.scalars().all()
    
    return templates.TemplateResponse(
        request,
        "home.html", {"todos": todo_list, "title": "Todo List Home Page"},
        status_code=200
    )





# @app.get("/todo/{todo_id}",include_in_schema = False, name="todo_page")
# def todo_page(request: Request, todo_id: int):
#     for item in todo_items:
#         if item["id"] == todo_id:
#             return templates.TemplateResponse(request, "todo.html", {"todo": item})
#     return templates.TemplateResponse(request, "todo.html", {"todo": None})



@app.get("/todo/{todo_id}",include_in_schema = False, name="todo_page")
def todo_page(request: Request, todo_id: int, db: Annotated[Session, Depends(get_db)]):

    result = db.execute(
        select(models.TodoItem).where(models.TodoItem.id == todo_id)
    )

    todo_item = result.scalars().first()

    if todo_item:
         return templates.TemplateResponse(request, "todo.html", {"todo": todo_item})
    
    raise templates.TemplateResponse(request, "todo.html", {"todo": None})







###############
# API ENDPOINTS
###############





# @app.get("/api/todos", response_model=list[TodoResponse])
# def get_todos():
#     return [TodoResponse(**item) for item in todo_items]


# return todo_items 
# # This Returns your raw Python list of dicts as-is.
# FastAPI may still validate/serialize with response_model, but you are not explicitly constructing model objects yourself.


# return [TodoResponse(**item) for item in todo_items]
# # This Converts each dict into a TodoResponse object first.
# Validation happens immediately in your code (fails early if data is invalid/missing fields).
# Ensures output shape matches the schema before returning.
# **item means “dictionary unpacking” into keyword arguments.

@app.get("/todos",response_model = list[TodoResponse], status_code = 200)
def get_todos(db:Annotated[Session,Depends(get_db)]):
    result = db.execute(
        select(models.TodoItem).order_by(models.TodoItem.created_at.desc())
    )

    todo_list = result.scalars().all()

    return todo_list



# API GET TODO BY ID
# @app.get("/api/todo/{todo_id}", response_model=TodoResponse)
# def get_todo(todo_id: int):
#     for item in todo_items:
#         if item["id"] == todo_id:
#             return TodoResponse(**item)
#     raise HTTPException(status_code=404, detail="Todo item not found")

@app.get("/api/todo/{todo_id}", 
         response_model=TodoResponse, 
         status_code=201
         )
def get_todo(todo_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.TodoItem).where(models.TodoItem.id == todo_id)
        )
    
    todo = result.scalars().first()

    if todo:
        return todo
    raise HTTPException(status_code=404, detail="TODO NOT FOUND")




# API FULL UPDATE USING PUT

@app.put("/api/todo/{todo_id}", 
         response_model=TodoResponse,
         status_code = 201
         )
def update_todo_full(
    todo_id: int,
    todo_data: TodoCreate, 
    db: Annotated[Session, Depends(get_db)]
):

    result = db.execute(
        select(models.TodoItem).where(models.TodoItem.id == todo_id)
        )
    
    todo = result.scalars().first()

    if not todo:
        raise HTTPException(status_code=404, detail="TODO NOT FOUND")
    
    
    todo.title = todo_data.title
    todo.description = todo_data.description
    todo.urgency_level = todo_data.urgency_level

    db.commit()
    db.refresh(todo)
    return todo
    


# API PARTIAL UPDATE USING PATCH

@app.patch("/api/todo/{todo_id}", 
         response_model=TodoResponse,
         status_code = 201
         )
def update_todo_partial(
    todo_id: int,
    todo_data: TodoUpdate, 
    db: Annotated[Session, Depends(get_db)]
):

    result = db.execute(
        select(models.TodoItem).where(models.TodoItem.id == todo_id)
        )
    
    todo = result.scalars().first()

    if not todo:
        raise HTTPException(status_code=404, detail="TODO NOT FOUND")
    
    
    update_data = todo_data.model_dump(exclude_unset=True) # Set this so Pydantic won't set all field to default which is None

    if "title" in update_data:
        todo.title = update_data["title"]
    if "description" in update_data:
        todo.description = update_data["description"]
    if "urgency_level" in update_data:
        todo.urgency_level = update_data["urgency_level"]


    db.commit()
    db.refresh(todo)
    return todo


# API DELETE

@app.delete("/api/todo/{todo_id}", 
          status_code=204
          )
def delete_todo(
    todo_id: int,
    db: Annotated[Session, Depends(get_db)]
):

    result = db.execute(
        select(models.TodoItem).where(models.TodoItem.id == todo_id)
        )
    
    todo = result.scalars().first()

    if not todo:
            raise HTTPException(status_code=404, detail="TODO NOT FOUND")
 
    db.delete(todo)
    db.commit()




# API CREATE TODO

@app.post("/api/todo", 
          response_model=TodoResponse, 
          status_code=201
          )
def create_todo(todo: TodoCreate, db: Annotated[Session, Depends(get_db)]):

    result = db.execute(select(models.TodoItem).where(models.TodoItem.title == todo.title))
    existing_todo = result.scalars().first()

    if existing_todo:
        raise HTTPException(
            status_code= 400,
            detail = "Todo title already exists"
        )
    
    result = db.execute(select(models.TodoItem).where(models.TodoItem.description == todo.description))
    existing_description = result.scalars().first()

    if existing_description:
        raise HTTPException(
            status_code= 400,
            detail = "Todo description already exists"
        )

    new_todo = models.TodoItem (
       title = todo.title,
       description = todo.description,
       urgency_level = todo.urgency_level

   ) 
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)

    return new_todo


    # new_id = max(item["id"] for item in todo_items) + 1 if todo_items else 1
    # new_todo = {
    #     "id": new_id,
    #     "title": todo.title,
    #     "description": todo.description,
    #     "urgency_level": todo.urgency_level,
    # }
    # todo_items.append(new_todo)
    # return TodoResponse(**new_todo)

