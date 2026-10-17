
from fastapi import FastAPI

app = FastAPI(title="JARVIS")

@app.get("/")
def home():
    return {
        "assistant": "JARVIS",
        "status": "online",
        "message": "Hola. JARVIS está funcionando."
    }

@app.get("/health")
def health():
    return {"status": "ok"}
