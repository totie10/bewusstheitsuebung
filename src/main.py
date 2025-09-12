from pipeline.classify import classify_consciousness_level

if __name__ == "__main__":
    msgs = [
        "OK.",
        "Ich kann Teiler meines Körpers spüren.\nMein Atem kommt und geht.",
        "Glückseligkeit.\nIch bin Glückseligkeit.\nUnd da ist.\nKörper und Dinge.",
    ]
    res = classify_consciousness_level(msgs, debug=True)
    print(res.model_dump(mode="json"))
