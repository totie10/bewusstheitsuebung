import logging
from typing import List

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from pipelines.classify_consciousness_level.classify import classify_consciousness_level
from pipelines.schema import ConsciousnessLevel

app = FastAPI(title="Bewusstheitsuebung API")
logger = logging.getLogger("uvicorn.error")  # Uvicorn's logger


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "internal_error"})


# =========================
# Models & routes
# =========================
class ClassifyRequest(BaseModel):
    messages: List[str] = Field(..., description="Conversation history; last item is target.")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/classify", response_model=ConsciousnessLevel, status_code=status.HTTP_200_OK)
def classify(req: ClassifyRequest):
    try:
        return classify_consciousness_level(req.messages)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unhandled error in /classify: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)  # Dateiname:App-Instanz
