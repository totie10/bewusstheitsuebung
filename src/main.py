from pipeline.consciousness_proposal import get_consciousness_proposal

if __name__ == "__main__":
    msgs = [
        "Nutzer: Mein Herz schl\u00e4gt. Nutzer: Und. Nutzer: Ich bin. Nutzer: \u00c4ngstlich.",
        "Nutzer: \u00c4ngstlich. Nutzer: Ich denke.",
    ]
    res = get_consciousness_proposal(msgs, debug=True)
    print(res.model_dump(mode="json"))
