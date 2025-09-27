import os

from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account

BASE_URL = "https://bewusst-api-222811362718.europe-west3.run.app"
AUDIENCE = BASE_URL
KEY_FILE = os.environ.get("KEY_FILE")  # path to your downloaded key

creds = service_account.IDTokenCredentials.from_service_account_file(
    KEY_FILE,
    target_audience=AUDIENCE,
)
authed = AuthorizedSession(creds)

payload_classify = {
    "messages": [
        "OK.",
        "Ich kann Teile meines Körpers spüren.\nMein Atem kommt und geht.",
        "Glückseligkeit.\nIch bin Glückseligkeit.\nUnd da ist.\nKörper und Dinge.",
    ]
}

res = authed.post(f"{BASE_URL}/classify", json=payload_classify, timeout=10)
if res.status_code == 200:
    print("✅ Success!")
    print(res.json())
else:
    print(f"❌ Error {res.status_code}: {res.text}")


payload_propose = {
    "messages": [
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
    ],
    "proposal_options": {
        "e2-1": "Und du kannst dieses ganz einfach da sein lassen.",
        "e2-2": "Und vielleicht kannst Du Dich dem Ganzen hingeben.",
        "e2-3": "Vielleicht kannst du dich immer tiefer in das Gefühl hineinfallen lassen.",
        "e2-4": "Und vielleicht kannst du ganz zu diesem Gefühl werden.",
        "e2-5": "Und vielleicht darf dieses Gefühl Raum bekommen.",
        "e2-6": "Und vielleicht kannst du dich von einem Gefühl ganz überwältigen lassen und schauen, wie\nes sich entwickelt.",
        "e2-7": "Vielleicht kannst du schauen, ob unter dem Gefühl eine tiefe Erfahrung da ist.",
    },
    "time_period": "ende",
}

res = authed.post(f"{BASE_URL}/propose", json=payload_propose, timeout=10)
if res.status_code == 200:
    print("✅ Success!")
    print(res.json())
else:
    print(f"❌ Error {res.status_code}: {res.text}")
