import json
from pathlib import Path
from typing import List

from pipeline.classify import classify_consciousness_level
from pipeline.schema import ConsciousnessPrediction, ConsciousnessSample


def run_dataset(in_path: Path, out_path: Path) -> None:
    """
    Load the dataset JSON (list of lists), run predictions,
    and write results to a separate JSON file.
    """
    # Read
    with in_path.open("r", encoding="utf-8") as f:
        all_dialogues = json.load(f)
    all_dialogues = [ConsciousnessSample(**dialogue) for dialogue in all_dialogues]

    consciousness_predictions: List[ConsciousnessPrediction] = []
    for dialogue in all_dialogues:
        context: List[str] = []
        for message in dialogue.consciousness_messages:
            vorhergesagte_bewusstheitsebene_dev = classify_consciousness_level(
                messages=context + [message.text], debug=False
            )
            consciousness_predictions.append(
                ConsciousnessPrediction(
                    username=dialogue.username,
                    timestamp=dialogue.timestamp,
                    text=message.text,
                    vorhergesagte_bewusstheitsebene=message.vorhergesagte_bewusstheitsebene,
                    context=context,
                    vorhergesagte_bewusstheitsebene_dev=vorhergesagte_bewusstheitsebene_dev,
                )
            )
            context.append(message.text)

        # Write
        with out_path.open("w", encoding="utf-8") as f:
            json.dump([cp.model_dump(mode="json") for cp in consciousness_predictions], f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    in_path = Path(r"C:\data\bewusstheitsuebung\20250910\preprocessed_users.json")
    out_path = in_path.parent / "predicted_users.json"
    run_dataset(in_path, out_path)
    print(f"Predictions written to: {out_path}")
