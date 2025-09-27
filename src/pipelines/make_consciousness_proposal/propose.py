import logging
import os
from typing import List, Dict

from langchain_google_genai import ChatGoogleGenerativeAI

from pipelines.make_consciousness_proposal.prompt import SYSTEM_PROMPT
from pipelines.schema import ConsciousnessProposal, TimePeriod

DEFAULT_MODEL = "gemini-2.0-flash-lite-001"
logger = logging.getLogger("uvicorn.error")  # shows up in Cloud Run logs


def format_proposal_options(proposal_options: dict[str, str]) -> str:
    """Erzeugt eine klar lesbare Liste für das LLM."""
    lines = []
    for k, v in sorted(proposal_options.items(), key=lambda x: x[0]):
        lines.append(f"{k}: {v}")
    return "\n".join(lines)


def make_consciousness_proposal(
    messages: List[Dict[str, str]],
    proposal_options: Dict[str, str],
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
                "Wähle die am besten passendsten Optionen (maximal drei!) "
                "und antworte gemäß der Schema-Definition."
            ),
        },
    ]

    logger.info(messages_with_system)

    raw = structured_llm.invoke(messages_with_system)
    result = ConsciousnessProposal.model_validate(raw)
    logger.info(result)
    return result


if __name__ == "__main__":
    import re

    messages = [
        {"role": "user", "content": "Ich kann Teile meines Körpers spüren.\nMein Atem kommt und geht."},
        {"role": "assistant", "content": "koerperempfindung"},
        {"role": "assistant", "content": "e1-2: Und du brauchst nichts damit zu tun."},
        {"role": "user", "content": "Glückseligkeit.\nIch bin Glückseligkeit.\nUnd da ist.\nKörper und Dinge."},
        {"role": "assistant", "content": "tiefere_erfahrung"},
        {
            "role": "assistant",
            "content": "e3-5: Und du kannst schauen was geschieht, wenn du bei der Glückseligkeit bleibst.",
        },
        {"role": "user", "content": "Da ist Freude."},
        {"role": "assistant", "content": "gefuehl"},
    ]

    # Your transcripts folder
    FOLDER = r"C:\Users\tobia\OneDrive\Dokumente\Christian Meyer\transcripts\transcripts"

    # Regex to match files like e2-1.txt, e2-42.txt ...
    pattern = re.compile(r"^(e2-\d+)\.txt$")

    proposal_options = {}

    for filename in os.listdir(FOLDER):
        match = pattern.match(filename)
        if match:
            proposal_id = match.group(1)  # e.g. "e2-5"
            file_path = os.path.join(FOLDER, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read().strip()
            proposal_options[proposal_id] = text

    # Optional: sort dictionary by key (so proposals are in natural order)
    proposal_options = dict(sorted(proposal_options.items(), key=lambda kv: int(kv[0].split("-")[1])))

    print(proposal_options)

    print(make_consciousness_proposal(messages, proposal_options, time_period=TimePeriod.ENDE))
