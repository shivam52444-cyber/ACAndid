import logging
import time
import numpy as np
from mode_loader import get_model
from google.genai import types

logger = logging.getLogger(__name__)

EMBED_MODEL = "models/gemini-embedding-001"
BATCH_SIZE = 20
RETRY_LIMIT = 3
RETRY_DELAY = 5


# ---------------------------
# FORMAT TEXT FOR EMBEDDING
# ---------------------------
def prepare_text(chunk):
    return f"""
TYPE: {chunk['type']}
FILE: {chunk['file']}
CONTENT:
{chunk['code']}
""".strip()


# ---------------------------
# NORMALIZATION (CRITICAL FIX)
# ---------------------------
def normalize(vec: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(vec)
    if norm == 0:
        return vec
    return vec / norm


# ---------------------------
# EMBED SINGLE BATCH
# ---------------------------
def _embed_batch(client, texts: list[str]) -> list[np.ndarray]:
    """Embed a single batch of texts via Gemini API with retry logic."""

    for attempt in range(RETRY_LIMIT):
        try:
            result = client.models.embed_content(
                model=EMBED_MODEL,
                contents=texts,
                config=types.EmbedContentConfig(
                    task_type="CODE_RETRIEVAL_QUERY"
                )
            )

            embeddings = []

            for e in result.embeddings:
                vec = np.array(e.values, dtype=np.float32)
                vec = normalize(vec)  # 🔥 CRITICAL
                embeddings.append(vec)

            return embeddings

        except Exception as e:
            err = str(e)

            if "429" in err or "quota" in err.lower() or "rate" in err.lower():
                if attempt < RETRY_LIMIT - 1:
                    logger.warning(
                        f"Rate limit hit, retrying in {RETRY_DELAY}s... "
                        f"(attempt {attempt + 1})"
                    )
                    time.sleep(RETRY_DELAY)
                    continue

            logger.error(f"Embedding batch failed: {err}")
            raise

    raise RuntimeError("Embedding failed after all retries")


# ---------------------------
# MAIN FUNCTION
# ---------------------------
def create_embeddings(chunks, repo_url=None):

    if not chunks:
        logger.warning("⚠️ No chunks provided for embedding")
        return []

    client = get_model()

    texts = [prepare_text(c) for c in chunks]
    embeddings = []

    for i in range(0, len(texts), BATCH_SIZE):
        batch_texts = texts[i: i + BATCH_SIZE]

        logger.info(
            f"Embedding batch {i // BATCH_SIZE + 1} | "
            f"chunks {i}–{i + len(batch_texts) - 1}"
        )

        batch_embeddings = _embed_batch(client, batch_texts)
        embeddings.extend(batch_embeddings)

        # avoid rate limits
        if i + BATCH_SIZE < len(texts):
            time.sleep(0.7)

    logger.info(
        f"✅ Embedding success | Repo: {repo_url} | Chunks: {len(chunks)}"
    )

    # attach embeddings back to chunks
    for chunk, emb in zip(chunks, embeddings):
        chunk["embedding"] = emb

    return chunks