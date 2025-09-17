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

payload = {
    "messages": [
        "OK.",
        "Ich kann Teile meines Körpers spüren.\nMein Atem kommt und geht.",
        "Glückseligkeit.\nIch bin Glückseligkeit.\nUnd da ist.\nKörper und Dinge.",
    ]
}

res = authed.post(f"{BASE_URL}/classify", json=payload, timeout=10)
if res.status_code == 200:
    print("✅ Success!")
    print(res.json())
else:
    print(f"❌ Error {res.status_code}: {res.text}")
