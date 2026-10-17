
import os
import secrets

import httpx
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI(title="JARVIS")

OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "")
JARVIS_ACCESS_KEY = os.getenv("JARVIS_ACCESS_KEY", "")
OLLAMA_URL = "https://ollama.com/api/chat"


class ChatRequest(BaseModel):
    message: str


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


@app.post("/chat")
async def chat(
    request: ChatRequest,
    x_jarvis_key: str = Header(default="")
):
    if not JARVIS_ACCESS_KEY or not secrets.compare_digest(
        x_jarvis_key, JARVIS_ACCESS_KEY
    ):
        raise HTTPException(status_code=401, detail="Clave de acceso incorrecta")

    if not OLLAMA_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="La API de Ollama no está configurada"
        )

    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Escribe un mensaje")

    try:
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(
                OLLAMA_URL,
                headers={
                    "Authorization": f"Bearer {OLLAMA_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-oss:20b",
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "Te llamas JARVIS. Responde en español, "
                                "con claridad y de forma útil."
                            ),
                        },
                        {"role": "user", "content": message},
                    ],
                    "stream": False,
                },
            )

        if response.is_error:
            raise HTTPException(
                status_code=502,
                detail="El servicio de IA devolvió un error. Revisa la API de Ollama."
            )

        data = response.json()
        return {
            "assistant": "JARVIS",
            "reply": data["message"]["content"],
        }

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="La IA tardó demasiado en responder. Inténtalo otra vez."
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="No se pudo conectar con el servicio de IA."
        )
