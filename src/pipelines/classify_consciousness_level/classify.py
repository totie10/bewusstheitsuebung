import logging
import os
from typing import List

from langchain_google_genai import ChatGoogleGenerativeAI

from pipelines.classify_consciousness_level.prompt import prompt
from pipelines.schema import ConsciousnessLevel

DEFAULT_MODEL = "gemini-2.0-flash-lite-001"
logger = logging.getLogger("uvicorn.error")  # shows up in Cloud Run logs


def classify_consciousness_level(
    messages: List[str],
    model_name: str = DEFAULT_MODEL,
    debug: bool = False,
) -> ConsciousnessLevel:
    """
    Nutzt die gesamte Nachrichtenliste als Kontext, klassifiziert aber nur die letzte Nachricht.
    Setze debug=True, um die exakt an das LLM gesendeten Prompt-Messages zu sehen.
    """
    logger.info("Start classify")
    if not messages:
        raise ValueError("Message list must not be empty")

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is not set")

    llm = ChatGoogleGenerativeAI(model=model_name, api_key=api_key)
    structured_llm = llm.with_structured_output(ConsciousnessLevel)

    context_text = "\n".join(f"- {m.strip()}" for m in messages[:-1])
    target_text = messages[-1].strip()

    # --- show exact prompt sent to the model ---
    if debug:
        formatted_msgs = prompt.format_messages(
            context_text=context_text,
            target_text=target_text,
        )
        print("\n====== PROMPT DEBUG (exact messages sent) ======")
        for m in formatted_msgs:
            # m.type is typically "system" / "human" / "ai"
            print(f"\n--- {m.type.upper()} ---\n{m.content}")
        print("====== END PROMPT DEBUG ======\n")

    # run chain
    chain = prompt | structured_llm
    raw = chain.invoke({"context_text": context_text, "target_text": target_text})

    # ensure correct type (re-validate in case parser returns a dict/BaseModel)
    result = ConsciousnessLevel.model_validate(raw)
    return result


if __name__ == "__main__":
    messages = [
        "OK.",
        "Ich kann Teile meines Körpers spüren.\nMein Atem kommt und geht.",
        "Glückseligkeit.\nIch bin Glückseligkeit.\nUnd da ist.\nKörper und Dinge.",
    ]
    print(classify_consciousness_level(messages))
