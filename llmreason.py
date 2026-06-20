
from groq import Groq
import os
import json
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

FALLBACK = json.dumps({
    "score": 0.0,
    "strengths": [],
    "gaps": ["LLM failed"],
    "reasoning": ""
})


def call_llm(jd, code_chunks, non_code_chunks, graph, repo_url=None):
    import logging
    logger = logging.getLogger(__name__)

    user_prompt = (
        "You are a highly experienced IT Engineering Manager with 15+ years of experience hiring engineers.\n\n"
        "You are strict, unbiased, and evaluate ONLY based on evidence.\n\n"
        "IMPORTANT:\n"
        "- These chunks are already filtered using embedding + cosine similarity\n"
        "- They represent the MOST relevant work of the candidate\n"
        "- Do NOT assume anything outside these\n\n"
        "TASK:\n"
        "1. Give score between 0 and 1\n"
        "2. List strengths\n"
        "3. List gaps\n"
        "4. Give reasoning\n\n"
        "STRICT OUTPUT FORMAT (valid JSON only, absolutely no markdown fences or extra text):\n\n"
        '{"score": 0.0, "strengths": [], "gaps": [], "reasoning": ""}\n\n'
        "---\n\n"
        f"JOB DESCRIPTION:\n{jd}\n\n"
        "---\n\n"
        f"TOP CODE CHUNKS:\n{code_chunks}\n\n"
        "---\n\n"
        f"TOP NON-CODE CHUNKS:\n{non_code_chunks}\n\n"
        "---\n\n"
        f"DEPENDENCY GRAPH:\n{graph}\n"
    )

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a brutally honest senior IT hiring manager. "
                        "Respond ONLY with valid JSON. No markdown fences, no extra text."
                    )
                },
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content

    except Exception as e:
        logger.error("LLM failed | Repo: %s | Error: %s", repo_url, str(e))
        return FALLBACK