from fastapi import FastAPI

app = FastAPI(title="Demo PSAR API")

@app.get("/")
def home():
    return {"message": "Привет, demo.psar.by работает на FastAPI 🚀"}