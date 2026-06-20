import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

_client = None

def get_model():
    global _client

    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")

        # 🔥 ADD THIS LINE HERE
        print("GEMINI:", api_key)

        if not api_key:
            raise RuntimeError("GEMINI_API_KEY missing")

        _client = genai.Client(api_key=api_key)

    return _client
