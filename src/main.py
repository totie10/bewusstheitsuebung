import subprocess

import requests
from google.auth.transport.requests import Request
from google.oauth2 import id_token

if __name__ == "__main__":

    BASE_URL = "https://bewusst-api-222811362718.europe-west3.run.app"
    AUDIENCE = BASE_URL  # Must match the Cloud Run service URL

    # Get an identity token using your local ADC credentials
    # try:
    #     token = subprocess.check_output(
    #         ["gcloud", "auth", "print-identity-token", f"--audiences={AUDIENCE}"], text=True
    #     ).strip()
    # except subprocess.CalledProcessError:
    #     token = subprocess.check_output(["gcloud", "auth", "print-identity-token"], text=True).strip()

    GLCLOUD = r"C:\Users\tobia\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
    token = subprocess.check_output([GLCLOUD, "auth", "print-identity-token"], text=True).strip()

    payload = {
        "messages": [
            "OK.",
            "Ich kann Teiler meines Körpers spüren.\nMein Atem kommt und geht.",
            "Glückseligkeit.\nIch bin Glückseligkeit.\nUnd da ist.\nKörper und Dinge.",
        ]
    }
    headers = {"Authorization": f"Bearer {token}"}

    res = requests.post(f"{BASE_URL}/classify", json=payload, headers=headers, timeout=30)

    if res.status_code == 200:
        print("✅ Result:", res.json())
    else:
        print(f"❌ Error {res.status_code}: {res.text}")
