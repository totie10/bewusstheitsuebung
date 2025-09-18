import logging
import os
from typing import List, Dict

from langchain_google_genai import ChatGoogleGenerativeAI

from pipelines.make_consciousness_proposal.prompt import SYSTEM_PROMPT
from pipelines.schema import ConsciousnessProposal, TimePeriod

DEFAULT_MODEL = "gemini-2.0-flash-lite-001"
logger = logging.getLogger("uvicorn.error")  # shows up in Cloud Run logs


def format_proposal_options(proposal_options: dict[int, str]) -> str:
    """Erzeugt eine klar lesbare Liste für das LLM."""
    lines = []
    for k, v in sorted(proposal_options.items(), key=lambda x: x[0]):
        lines.append(f"{k}. {v}")
    return "\n".join(lines)


def make_consciousness_proposal(
    messages: List[Dict[str, str]],
    proposal_options: Dict[int, str],
    time_period: TimePeriod,
    model_name: str = DEFAULT_MODEL,
    debug: bool = False,
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

    # System-Prompt + deine Messages direkt
    messages_with_system = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *messages,
        {
            "role": "user",
            "content": (
                f"Zeitabschnitt der Übung: {time_period.value}\n\n"
                f"Hier sind die möglichen Vorschläge:\n"
                f"{format_proposal_options(proposal_options)}\n\n"
                "Wähle die am besten passende Option (nur eine!) "
                "und antworte gemäß der Schema-Definition."
            ),
        },
    ]

    if debug:
        print(messages_with_system)

    raw = structured_llm.invoke(messages_with_system)
    result = ConsciousnessProposal.model_validate(raw)
    return result


if __name__ == "__main__":
    messages = [
        {"role": "user", "content": "Ich kann Teile meines Körpers spüren.\nMein Atem kommt und geht."},
        {"role": "assistant", "content": "koerperempfindung"},
        {"role": "assistant", "content": "Und du brauchst nichts damit zu tun."},
        {"role": "user", "content": "Glückseligkeit.\nIch bin Glückseligkeit.\nUnd da ist.\nKörper und Dinge."},
        {"role": "assistant", "content": "tiefere_erfahrung"},
        {"role": "assistant", "content": "Und vielleicht kannst du schauen, wie tief die Erfahrung ist."},
        {"role": "user", "content": "Immer noch Glückseligkeit."},
        {"role": "assistant", "content": "tiefere_erfahrung"},
    ]
    proposal_options = {
        1: "Und vielleicht kannst du schauen, wie tief die Erfahrung ist.",
        2: "Und vielleicht kannst du schauen, ob sie eine Grenze hat.",
        3: "Und vielleicht kannst du dich ihr ganz hingeben",
        4: "Und vielleicht kannst du dich ganz in ihr auflösen.",
    }
    print(make_consciousness_proposal(messages, proposal_options, time_period=TimePeriod.ANFANG, debug=True))
