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

from .auth import verify_password

from fastapi import HTTPException

class VisitorCreate(BaseModel):
    name: str

class UserCreate(BaseModel):
    username: str
    password: str

app = FastAPI(title="Demo PSAR API")

templates = Jinja2Templates(directory="app/templates")

Base.metadata.create_all(bind=engine)

def get_current_user(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    username = verify_token(token)

    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return user


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
def create_visitor(
    visitor: VisitorCreate,
    authorization: str = Header(...)
):
    get_current_user(authorization)
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
def delete_visitor(
    visitor_id: int,
    authorization: str = Header(...)
):
    get_current_user(authorization)
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
def update_visitor(
    visitor_id: int,
    visitor_data: VisitorCreate,
    authorization: str = Header(...)
):
    get_current_user(authorization)
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

    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()

    if not user:
        return {"error": "User not found"}

    return {
        "id": user.id,
        "username": user.username
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


@app.post("/api/user-login")
def user_login(user: UserCreate):
    db = SessionLocal()

    existing_user = db.query(User).filter(User.username == user.username).first()

    if not existing_user:
        db.close()
        return {"error": "User not found"}

    if not verify_password(user.password, existing_user.password):
        db.close()
        return {"error": "Invalid password"}

    token = create_access_token({"sub": existing_user.username})
    db.close()

    return {
        "access_token": token,
        "token_type": "bearer"
    }