import json
from pathlib import Path
from typing import List


def preprocess_dialogue(messages: List[str], include_all_messages: bool = False) -> List[str]:
    """
    Preprocess dialogue:
    - Combine consecutive 'Nutzer:' messages until the next 'Agent...'
    - Remove 'Nutzer:' prefix
    - Join combined Nutzer-strings with newline
    - Ignore 'Agent...' entries
    If include_all_messages = True, keep messages with old format (no Nutzer or Agent)
    Returns a list of combined user message blocks.
    """
    results: List[str] = []
    buffer: List[str] = []

    for raw in messages:
        msg = raw.strip()
        if msg.startswith("Nutzer:"):
            text = msg.replace("Nutzer:", "", 1).strip()
            buffer.append(text)
        elif msg.startswith("Agent"):
            if buffer:
                results.append("\n".join(buffer))
                buffer = []
        else:
            if include_all_messages:
                results.append(msg)
            else:
                break

    if buffer:
        results.append("\n".join(buffer))

    return results


def export_preprocessed_lists(in_path: Path, out_path: Path, include_all_messages: bool = False) -> None:
    """
    Loads the input JSON (a list of users),
    extracts only the preprocessed nutzer dialogues (list of lists of strings),
    and writes them to a new JSON file.
    """
    with in_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    all_dialogues: List[List[str]] = []

    if not isinstance(data, list):
        raise ValueError("Top-level JSON must be a list of user objects.")

    for user in data:
        usages = user.get("usage", [])
        if not isinstance(usages, list) or len(usages) == 0:
            continue

        for u in usages:
            if not isinstance(u, dict):
                continue
            nutzer_list = u.get("nutzer", [])
            if not isinstance(nutzer_list, list) or len(nutzer_list) == 0:
                continue

            blocks = preprocess_dialogue(nutzer_list, include_all_messages)
            if len(blocks) > 0:
                all_dialogues.append(blocks)

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(all_dialogues, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    for include_all_messages in [True, False]:
        in_path = Path(r"C:\data\bewusstheitsuebung\20250910\users.json")
        if include_all_messages:
            out_path = in_path.parent / "preprocessed_users_all_messages.json"
        else:
            out_path = in_path.parent / "preprocessed_users.json"
        export_preprocessed_lists(in_path, out_path, include_all_messages=include_all_messages)
