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
    results = []
    buffer = []

    for msg in messages:
        msg = msg.strip()
        if msg.startswith("Nutzer:"):
            # remove prefix and collect
            text = msg.replace("Nutzer:", "", 1).strip()
            buffer.append(text)
        elif msg.startswith("Agent"):
            # time to flush buffer if we collected Nutzer messages
            if buffer:
                combined = "\n".join(buffer)
                results.append(combined)
                buffer = []
            # skip the agent message (ignored)
        else:
            # safety: treat as user text if format unexpected
            if include_all_messages:
                results.append(msg)
            else:
                break

    # flush last buffer if any
    if buffer:
        combined = "\n".join(buffer)
        results.append(combined)

    return results


if __name__ == "__main__":
    messages = [
        "Nutzer: OK.",
        "Agent nach 8 Sekunden: nichts",
        "Nutzer: Ich kann Teiler meines K\u00f6rpers sp\u00fcren.",
        "Nutzer: Mein Atem kommt und geht.",
        "Agent nach 27 Sekunden: Koerpergefuehl",
        "Nutzer: Gl\u00fcckseligkeit.",
        "Nutzer: Ich bin Gl\u00fcckseligkeit.",
        "Nutzer: Und da ist.",
        "Nutzer: K\u00f6rper und Dinge.",
        "Agent nach 35 Sekunden: tiefere Erfahrung",
        "Nutzer: Ja, da gehen mehr Dinge durch den Kopf.",
        "Agent nach 20 Sekunden: Koerpergefuehl",
    ]
    preprocessed_messages = preprocess_dialogue(messages)
    print(preprocessed_messages)
