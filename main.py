from google import genai
import os


def main():
    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
    resp = client.models.generate_content(
        model="gemini-2.0-flash-lite-001", contents="Is fear a feeling or a thought?."
    )
    print(resp.text)


if __name__ == "__main__":
    main()
