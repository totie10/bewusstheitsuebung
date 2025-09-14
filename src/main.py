import requests

BASE_URL = "https://bewusst-api-222811362718.europe-west3.run.app"

payload = {
    "messages": [
        "OK.",
        "Ich kann Teile meines Körpers spüren.\nMein Atem kommt und geht.",
        "Glückseligkeit.\nIch bin Glückseligkeit.\nUnd da ist.\nKörper und Dinge.",
    ]
}

# Just send a POST request — no auth headers needed
res = requests.post(f"{BASE_URL}/classify", json=payload, timeout=2)

if res.status_code == 200:
    print("✅ Success!")
    print(res.json())
else:
    print(f"❌ Error {res.status_code}: {res.text}")
