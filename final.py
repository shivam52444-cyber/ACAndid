import numpy as np


# ---------------------------
# cosine similarity
# ---------------------------
def cosine_similarity(a, b):
    norm1 = np.linalg.norm(a)
    norm2 = np.linalg.norm(b)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    sim = np.dot(a, b) / (norm1 * norm2)

    return (sim + 1) / 2   # 🔥 normalize


# ---------------------------
# main scoring function
# ---------------------------
def score_chunks(chunks, jd_embedding, k=5, repo_url=None):
    import logging
    logger = logging.getLogger(__name__)

    if not chunks:
        return 0.0, []

    

    # compute similarity
    for chunk in chunks:
        score = cosine_similarity(jd_embedding, chunk["embedding"])
        chunk["similarity"] = float(score)

    # average similarity
    avg_similarity = sum(c["similarity"] for c in chunks) / len(chunks)

    # sort
    sorted_chunks = sorted(
        chunks,
        key=lambda x: x["similarity"],
        reverse=True
    )

    # 🔥 ONLY RETURN RAW CHUNKS
    top_k_chunks = [c["code"] for c in sorted_chunks[:k]]
    logger.info(f"📊 Scoring chunks | Repo: {repo_url} | Total: {len(chunks)}")

    logger.info(f"🔥 Highest similarity | Repo: {repo_url} | Score: {sorted_chunks[0]['similarity']:.4f}")
    logger.info(f"🧊 Lowest similarity | Repo: {repo_url} | Score: {sorted_chunks[-1]['similarity']:.4f}")
    return avg_similarity, top_k_chunks
