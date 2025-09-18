import logging
import os
from typing import List, Dict

from langchain_google_genai import ChatGoogleGenerativeAI

from pipelines.classify_consciousness_level.prompt import prompt
from pipelines.schema import ConsciousnessProposal, TimePeriod

DEFAULT_MODEL = "gemini-2.0-flash-lite-001"
logger = logging.getLogger("uvicorn.error")  # shows up in Cloud Run logs


def make_consciousness_proposal(
    messages: List[Dict[str, str]],
    proposal_options: Dict[int, str],
    time_period: TimePeriod,
    model_name: str = DEFAULT_MODEL,
) -> ConsciousnessProposal:
    """
    Nutzt die gesamte Nachrichtenliste als Kontext, klassifiziert aber nur die letzte Nachricht.
    Setze debug=True, um die exakt an das LLM gesendeten Prompt-Messages zu sehen.
    """
    logger.info("Start propose")
    if not messages:
        raise ValueError("Message list must not be empty")

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is not set")

    llm = ChatGoogleGenerativeAI(model=model_name, api_key=api_key)
    structured_llm = llm.with_structured_output(ConsciousnessProposal)

    # run chain
    chain = prompt | structured_llm
    raw = chain.invoke({"messages": messages, "proposal_options": proposal_options})

    # ensure correct type (re-validate in case parser returns a dict/BaseModel)
    result = ConsciousnessProposal.model_validate(raw)
    return result


if __name__ == "__main__":
    messages = [
        {"role": "user", "content": "Ich kann Teile meines Körpers spüren.\nMein Atem kommt und geht."},
        {"role": "tool", "content": "koerperempfindung"},
        {"role": "assistant", "content": "Und du brauchst nichts damit zu tun."},
        {"role": "user", "content": "Glückseligkeit.\nIch bin Glückseligkeit.\nUnd da ist.\nKörper und Dinge."},
        {"role": "tool", "content": "tiefere_erfahrung"},
    ]
    proposal_options = {
        1: "Und vielleicht kannst du schauen, wie tief die Erfahrung ist.",
        2: "Und vielleicht kannst du schauen, ob sie eine Grenze hat.",
        3: "Und vielleicht kannst du dich ihr ganz hingeben",
        4: "Und vielleicht kannst du dich ganz in ihr auflösen.",
    }
