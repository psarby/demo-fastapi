from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from .database import SessionLocal, engine
from .models import Base, Visitor

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