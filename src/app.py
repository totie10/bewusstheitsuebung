import logging
from typing import List

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from pipeline.classify import classify_consciousness_level
from pipeline.schema import ConsciousnessLevel

app = FastAPI(title="Bewusstheitsuebung API")
logger = logging.getLogger("uvicorn.error")  # uses Uvicorn's logger


class ClassifyRequest(BaseModel):
    messages: List[str] = Field(..., description="Conversation history; last item is target.")


@app.get("/healthz")
def healthz():
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
