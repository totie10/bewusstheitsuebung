import os
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI

from pipeline.prompt import system_prompt
from pipeline.schema import ConsciousnessProposal

DEFAULT_MODEL = "gemini-2.0-flash-lite-001"


def get_consciousness_proposal(messages: List[str], model_name: str = DEFAULT_MODEL) -> ConsciousnessProposal:
    """
    Nutzt die gesamte Nachrichtenliste als Kontext, klassifiziert aber nur die letzte Nachricht.
    """
    if not messages:
        raise ValueError("Message list must not be empty")

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is not set")

    llm = ChatGoogleGenerativeAI(model=model_name, api_key=api_key)
    structured_llm = llm.with_structured_output(ConsciousnessProposal)

    context_text = "\n".join(f"- {m.strip()}" for m in messages[:-1])
    target_text = messages[-1].strip()

    chain = system_prompt | structured_llm
    result: ConsciousnessProposal = chain.invoke({"context_text": context_text, "target_text": target_text})
    return result
