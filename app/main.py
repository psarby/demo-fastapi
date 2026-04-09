from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from .database import SessionLocal, engine
from .models import Base, Visitor

from pydantic import BaseModel

from .auth import create_access_token

from fastapi import Header
from .auth import verify_token

from .models import User
from .auth import hash_password



class VisitorCreate(BaseModel):
    name: str

class UserCreate(BaseModel):
    username: str
    password: str

app = FastAPI(title="Demo PSAR API")

templates = Jinja2Templates(directory="app/templates")

Base.metadata.create_all(bind=engine)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    db: Session = SessionLocal()
    visitors = db.query(Visitor).order_by(Visitor.id.desc()).all()
    db.close()

    return templates.TemplateResponse(
        name="index.html",
        request=request,
        context={"visitors": visitors}
    )


@app.post("/hello", response_class=HTMLResponse)
def hello(request: Request, name: str = Form(...)):
    db: Session = SessionLocal()

    visitor = Visitor(name=name)
    db.add(visitor)
    db.commit()

    visitors = db.query(Visitor).order_by(Visitor.id.desc()).all()
    db.close()

    return templates.TemplateResponse(
        name="index.html",
        request=request,
        context={
            "message": f"Привет, {name} 👋",
            "visitors": visitors
        }
    )

@app.get("/api/visitors")
def get_visitors():
    db = SessionLocal()
    visitors = db.query(Visitor).order_by(Visitor.id.desc()).all()
    db.close()

    return [
        {
            "id": visitor.id,
            "name": visitor.name
        }
        for visitor in visitors
    ]

@app.post("/api/visitors")
def create_visitor(visitor: VisitorCreate):
    db = SessionLocal()

    new_visitor = Visitor(name=visitor.name)
    db.add(new_visitor)
    db.commit()
    db.refresh(new_visitor)

    db.close()

    return {
        "id": new_visitor.id,
        "name": new_visitor.name
    }

@app.delete("/api/visitors/{visitor_id}")
def delete_visitor(visitor_id: int):
    db = SessionLocal()

    visitor = db.query(Visitor).filter(Visitor.id == visitor_id).first()

    if not visitor:
        db.close()
        return {"error": "Visitor not found"}

    db.delete(visitor)
    db.commit()
    db.close()

    return {"message": f"Visitor {visitor_id} deleted"}

@app.put("/api/visitors/{visitor_id}")
def update_visitor(visitor_id: int, visitor_data: VisitorCreate):
    db = SessionLocal()

    visitor = db.query(Visitor).filter(Visitor.id == visitor_id).first()

    if not visitor:
        db.close()
        return {"error": "Visitor not found"}

    visitor.name = visitor_data.name
    db.commit()
    db.refresh(visitor)
    db.close()

    return {
        "id": visitor.id,
        "name": visitor.name
    }

@app.post("/api/login")
def login(visitor: VisitorCreate):
    token = create_access_token({"sub": visitor.name})

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@app.get("/api/me")
def get_me(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    username = verify_token(token)

    return {
        "username": username,
        "message": "JWT works"
    }

@app.post("/api/register")
def register(user: UserCreate):
    db = SessionLocal()

    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        db.close()
        return {"error": "Username already exists"}

    new_user = User(
        username=user.username,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()

    return {
        "id": new_user.id,
        "username": new_user.username
    }