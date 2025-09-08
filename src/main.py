from pipeline.consciousness_proposal import get_consciousness_proposal

if __name__ == "__main__":
    msgs = [
        "Ich bin müde von der Arbeit.",
        "Mein Kopf ist voller Gedanken über morgen.",
        "Ich fühle ein Stechen in der Brust.",
    ]
    res = get_consciousness_proposal(msgs)
    print(res.model_dump(mode="json"))
