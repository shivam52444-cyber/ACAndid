import math
from collections import Counter

def tokenize(text):
    return text.lower().split()


def bm25_score(query, document, k1=1.5, b=0.75):
    # tokenize
    q_tokens = tokenize(query)
    d_tokens = tokenize(document)
    
    # term frequencies
    tf = Counter(d_tokens)
    
    # document length
    doc_len = len(d_tokens)
    
    # since we have only ONE document, avgdl = doc_len
    avgdl = doc_len if doc_len > 0 else 1
    
    score = 0.0
    
    for term in q_tokens:
        if term not in tf:
            continue
        
        # term frequency in document
        freq = tf[term]
        
        # IDF (since only one doc → simplified)
        idf = math.log((1 + 1) / (1))  # ≈ log(2)
        
        # BM25 formula
        numerator = freq * (k1 + 1)
        denominator = freq + k1 * (1 - b + b * (doc_len / avgdl))
        
        score += idf * (numerator / denominator)
    
    return score/(score+1)

