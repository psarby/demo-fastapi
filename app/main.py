from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Form

app = FastAPI(title="Demo PSAR API")

templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        name="index.html",
        request=request
    )

@app.post("/hello", response_class=HTMLResponse)
def hello(request: Request, name: str = Form(...)):
    return templates.TemplateResponse(
    name="index.html",
    request=request,
    context={
        "message": f"Привет, {name} 👋"
    }
)

