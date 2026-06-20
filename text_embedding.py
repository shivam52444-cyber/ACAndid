import numpy as np
from mode_loader import get_model
from google.genai import types

EMBED_MODEL = "models/gemini-embedding-001"


# ---------------------------
# NORMALIZATION (CRITICAL)
# ---------------------------
def normalize(vec: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(vec)
    if norm == 0:
        return vec
    return vec / norm


# ---------------------------
# MAIN FUNCTION
# ---------------------------
def get_embedding(text: str) -> np.ndarray:
    """
    Embed a single piece of query text (JD or resume)
    """

    client = get_model()

    # safety check
    if not hasattr(client, "models"):
        raise RuntimeError("Invalid client: models API not found")

    try:
        result = client.models.embed_content(
            model=EMBED_MODEL,
            contents=text,
            config=types.EmbedContentConfig(
                task_type="SEMANTIC_SIMILARITY"
            )
        )

        vec = np.array(result.embeddings[0].values, dtype=np.float32)

        # 🔥 CRITICAL FIX
        vec = normalize(vec)

        return vec

    except Exception as e:
        raise RuntimeError(f"Embedding failed (query): {str(e)}")