import re


def extract_function_chunks_generic(code: str, file_path: str):
    """
    Language-agnostic function chunking.
    Works for Python, JS, Java, C++, Go, etc.
    """

    chunks = []

    # 🔥 detect function definitions (multi-language)
    pattern = r"""
        (def\s+\w+\s*\(.*?\)) |              # Python
        (function\s+\w+\s*\(.*?\)) |         # JS
        (\w+\s+\w+\s*\(.*?\)\s*\{) |         # C/Java
        (class\s+\w+)                        # class
    """

    matches = list(re.finditer(pattern, code, re.VERBOSE | re.DOTALL))

    # If no functions found → fallback
    if not matches:
        return [{
            "file": file_path,
            "type": "file_chunk",
            "code": code[:2000]  # limit size
        }]

    for i, match in enumerate(matches):
        start = match.start()

        # end = next function OR end of file
        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(code)

        chunk_code = code[start:end].strip()

        chunks.append({
            "file": file_path,
            "type": "function",
            "code": chunk_code
        })

    return chunks

def chunk_all_code_files(code_dict):
    all_chunks = []

    for file_path, code in code_dict.items():
        chunks = extract_function_chunks_generic(code, file_path)
        all_chunks.extend(chunks)

    return all_chunks

