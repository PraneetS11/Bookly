from typing import Optional

from fastapi import FastAPI, Header
from pydantic import BaseModel

app = FastAPI()


@app.get("/")
async def read_root():
    return {"message": "Hello World"}


@app.get("/greet/")
async def greet_name(
    name: str = "User",
    age: int = 0,
) -> dict:
    return {"message": f"Hello {name}", "age": age}


class BookCreateModel(BaseModel):
    title: str
    author: str


@app.post("/create_book")
async def create_book(book_data: BookCreateModel) -> dict:
    return {
        "title": book_data.title,
        "author": book_data.author,
    }


@app.get("/get_headers")
async def get_headers(
    accept: Optional[str] = Header(None),
    content_type: Optional[str] = Header(None),
    host:str = Header(None)
) -> dict:
    return {
        "Accept": accept,
        "Content-Type": content_type,
        "Host":host
    }