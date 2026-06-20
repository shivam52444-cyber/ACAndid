import logging
import gc
import copy
import json
import re

from clone import get_repo, read_repo_files_clean, delete_repo
from graph import build_clean_dependency_pipeline
from code_chunck import chunk_all_code_files
from otherchunking import chunk_non_code
from embeding import create_embeddings
from final import score_chunks
from llmreason import call_llm
from parser import extract_text_from_pdf
from BM import bm25_score
from cosine import cosine_similarity
from text_embedding import get_embedding
from mode_loader import get_model

from logger import setup_logger

# -------------------------
# LOGGER SETUP
# -------------------------
setup_logger()
logger = logging.getLogger(__name__)

# -------------------------
# LOAD MODEL
# -------------------------
model = get_model()


def run_pipeline(resume_path, jd, repo_url):

    url = repo_url
    logger.info(f"🚀 Pipeline started | Repo: {url}")

    # -------------------------
    # CLONE + READ
    # -------------------------
    repo_path = get_repo(url)
    data = read_repo_files_clean(repo_path)

    logger.info(f"📂 Code files: {len(data['code'])}")

    # -------------------------
    # GRAPH
    # -------------------------
    graph_data = build_clean_dependency_pipeline(data['code'])

    graph_payload = {
        "top_nodes": graph_data["top_nodes"],
        "graph": graph_data["clean_graph"],
        "summary": graph_data["summary"]
    }

    del graph_data
    gc.collect()

    # -------------------------
    # CHUNKING (FIXED DESIGN)
    # -------------------------
    code_chunk = chunk_all_code_files(data['code'])

    # 🔥 Merge ALL non-code sources
    non_code_data = {
        "docs": data.get("docs", {}),
        "config": data.get("config", {}),
        "infra": data.get("infra", {})
    }

    doc_chunk = chunk_non_code(non_code_data)

    doc_chunk = chunk_non_code(non_code_data)

    # 🔥 Normalize doc structure → make everything "code"
    for c in doc_chunk:
        if isinstance(c, dict):
            if "text" in c:
                c["code"] = c["text"]
            elif "doc" in c:
                c["code"] = c["doc"]

    # 🔥 Validate chunks
    code_chunk = [c for c in code_chunk if isinstance(c, dict) and c.get("code")]
    doc_chunk = [c for c in doc_chunk if isinstance(c, dict) and c.get("code")]

    logger.info(f"📦 VALID Code chunks: {len(code_chunk)}")
    logger.info(f"📦 VALID Doc chunks: {len(doc_chunk)}")

    # -------------------------
    # DELETE RAW DATA
    # -------------------------
    del data
    gc.collect()

    # -------------------------
    # EMBEDDING
    # -------------------------
    try:
        code_embed = create_embeddings(copy.deepcopy(code_chunk), repo_url=url)
        doc_embed = create_embeddings(copy.deepcopy(doc_chunk), repo_url=url)
        jd_emb = get_embedding(jd)

        logger.info(f"🧠 Embedding created | Repo: {url}")

    except Exception as e:
        logger.error(f"❌ Embedding failed | Repo: {url} | Error: {str(e)}")
        delete_repo(repo_path)
        raise

    # -------------------------
    # SCORING
    # -------------------------
    aveg_sim_code, top_k_code = score_chunks(
        code_embed, jd_embedding=jd_emb, k=3, repo_url=url
    )

    avg_sim_doc, top_k_doc = score_chunks(
        doc_embed, jd_embedding=jd_emb, k=2, repo_url=url
    )

    logger.info(f"💻 Avg Code Similarity: {aveg_sim_code:.4f}")
    logger.info(f"📄 Avg Doc Similarity: {avg_sim_doc:.4f}")

    # -------------------------
    # CLEAN EMBEDDINGS
    # -------------------------
    del code_embed
    del doc_embed
    gc.collect()

    # -------------------------
    # STRONG FALLBACK (CRITICAL)
    # -------------------------
    if not top_k_code:
        logger.warning("⚠️ Empty code chunks → fallback")
        top_k_code = [c["code"] for c in code_chunk[:3]]

    if not top_k_doc:
        logger.warning("⚠️ Empty doc chunks → fallback")
        top_k_doc = [c["code"] for c in doc_chunk[:2]]

    # -------------------------
    # DELETE CHUNKS AFTER USE
    # -------------------------
    del code_chunk
    del doc_chunk
    gc.collect()

    # -------------------------
    # FORMAT FOR LLM
    # -------------------------
    if top_k_code and isinstance(top_k_code[0], dict):
        top_k_code = [c["code"] for c in top_k_code]

    if top_k_doc and isinstance(top_k_doc[0], dict):
        top_k_doc = [c["code"] for c in top_k_doc]

    # 🔥 FINAL GUARD (never empty)
    if not top_k_code:
        top_k_code = ["No code extracted but repository contains implementation"]

    if not top_k_doc:
        top_k_doc = ["No documentation extracted"]

    # -------------------------
    # LLM CALL
    # -------------------------
    logger.info(f"🤖 Calling LLM | Repo: {url}")

    response_text = call_llm(
        jd=jd,
        code_chunks=top_k_code,
        non_code_chunks=top_k_doc,
        graph=graph_payload,
        repo_url=url
    )

    del graph_payload
    gc.collect()

    # -------------------------
    # PARSE LLM RESPONSE
    # -------------------------
    try:
        clean = response_text.strip()
        clean = re.sub(r'^```(?:json)?\s*', '', clean)
        clean = re.sub(r'\s*```$', '', clean).strip()
        parsed = json.loads(clean)
        llm_score = float(parsed.get("score", 0.0))
    except Exception:
        logger.error("❌ LLM JSON parse failed")
        llm_score = 0.0
        parsed = {}

    # -------------------------
    # RESUME SCORING
    # -------------------------
    resume_text = extract_text_from_pdf(resume_path)
    resume_emb = get_embedding(resume_text)

    cos_sim = cosine_similarity(jd_emb, resume_emb)
    resume_score = 0.5 * bm25_score(jd, resume_text) + 0.5 * cos_sim

    # -------------------------
    # FINAL SCORE
    # -------------------------
    final_score = (
        0.2 * resume_score +
        0.4 * llm_score +
        0.3 * aveg_sim_code +
        0.1 * avg_sim_doc
    )

    # -------------------------
    # CLEANUP
    # -------------------------
    delete_repo(repo_path)

    logger.info(f"✅ Pipeline completed | Repo: {url}")

    return {
        "final_score": final_score,
        "resume_score": resume_score,
        "code_score": aveg_sim_code,
        "doc_score": avg_sim_doc,
        "llm_score": llm_score,
        "strengths": parsed.get("strengths", []),
        "gaps": parsed.get("gaps", []),
        "reasoning": parsed.get("reasoning", "")
    }