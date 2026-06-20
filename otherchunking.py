def chunk_docs(text, file_path, max_len=500):
    chunks = []

    # split by paragraphs
    paragraphs = text.split("\n\n")

    current = ""

    for para in paragraphs:
        if len(current) + len(para) < max_len:
            current += para + "\n\n"
        else:
            if current:
                chunks.append({
                    "file": file_path,
                    "type": "doc",
                    "code": current.strip()
                })
            current = para

    if current:
        chunks.append({
            "file": file_path,
            "type": "doc",
            "code": current.strip()
        })

    return chunks

def chunk_config_lines(text, file_path, chunk_size=50):
    lines = text.split("\n")

    chunks = []

    for i in range(0, len(lines), chunk_size):
        chunk = "\n".join(lines[i:i+chunk_size])

        chunks.append({
            "file": file_path,
            "type": "config",
            "code": chunk
        })

    return chunks

def chunk_infra(text, file_path, max_len=1000):
    return [{
        "file": file_path,
        "type": "infra",
        "code": text[:max_len]
    }]
    
def chunk_non_code(data):
    all_chunks = []

    # docs
    for file, text in data["docs"].items():
        all_chunks.extend(chunk_docs(text, file))

    # config
    for file, text in data["config"].items():
        all_chunks.extend(chunk_config_lines(text, file))

    # infra
    for file, text in data["infra"].items():
        all_chunks.extend(chunk_infra(text, file))

    return all_chunks