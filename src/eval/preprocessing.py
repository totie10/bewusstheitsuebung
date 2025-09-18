import json
from pathlib import Path
from typing import List

from pipelines.schema import ConsciousnessMessage, MAPPING_BEWUSSTHEITSEBENE, ConsciousnessSample


def preprocess_dialogue(messages: List[str]) -> List[ConsciousnessMessage]:
    """
    Preprocess dialogue:
    - Combine consecutive 'Nutzer:' messages until the next 'Agent...'
    - Remove 'Nutzer:' prefix
    - Join combined Nutzer-strings with newline
    - Ignore 'Agent...' entries
    If include_all_messages = True, keep messages with old format (no Nutzer or Agent)
    Returns a list of combined user message blocks.
    """
    results: List[ConsciousnessMessage] = []
    buffer: List[str] = []

    for raw in messages:
        msg = raw.strip()
        if msg.startswith("Nutzer:"):
            text = msg.replace("Nutzer:", "", 1).strip()
            buffer.append(text)
        elif msg.startswith("Agent"):
            if buffer:
                consciousness_message = ConsciousnessMessage(
                    text="\n".join(buffer),
                    vorhergesagte_bewusstheitsebene=MAPPING_BEWUSSTHEITSEBENE[msg.split(": ")[1]],
                )
                results.append(consciousness_message)
                buffer = []
        else:
            break

    return results


def export_preprocessed_lists(in_path: Path, out_path: Path) -> None:
    """
    Loads the input JSON (a list of users),
    extracts only the preprocessed nutzer dialogues (list of lists of strings),
    and writes them to a new JSON file.
    """
    with in_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    all_dialogues: List[ConsciousnessSample] = []

    if not isinstance(data, list):
        raise ValueError("Top-level JSON must be a list of user objects.")

    for user in data:
        username = user.get("username")
        usages = user.get("usage", [])
        if not isinstance(usages, list) or len(usages) == 0:
            continue

        for u in usages:
            if not isinstance(u, dict):
                continue
            nutzer_list = u.get("nutzer", [])
            if not isinstance(nutzer_list, list) or len(nutzer_list) == 0:
                continue

            consciousness_messages = preprocess_dialogue(nutzer_list)
            if len(consciousness_messages) > 0:
                consciousness_sample = ConsciousnessSample(
                    username=username, timestamp=u.get("timestamp"), consciousness_messages=consciousness_messages
                )
                all_dialogues.append(consciousness_sample)

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(
            [dialogue.model_dump(mode="json") for dialogue in all_dialogues],
            f,
            ensure_ascii=False,
            indent=2,
        )


if __name__ == "__main__":
    in_path = Path(r"C:\data\bewusstheitsuebung\20250910\users.json")
    out_path = in_path.parent / "preprocessed_users.json"
    export_preprocessed_lists(in_path, out_path)
