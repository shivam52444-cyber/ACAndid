import os
from dotenv import load_dotenv
from google import genai  # The new way to import

load_dotenv()

# The client automatically picks up GEMINI_API_KEY or GOOGLE_API_KEY from the environment
if not os.getenv("GEMINI_API_KEY"):
    raise EnvironmentError("GEMINI_API_KEY is not set. Add it to your .env file.")

_client = None

def get_model():
    global _client
    if _client is None:
        # Properly initializes the modern client object
        _client = genai.Client()
    return _client
