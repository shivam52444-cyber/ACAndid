import os

def detect_language_from_file(file_path: str) -> str:
    # get extension
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    # mapping
    extension_map = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".java": "Java",
        ".c": "C",
        ".cpp": "C++",
        ".cc": "C++",
        ".h": "C/C++ Header",
        ".cs": "C#",
        ".go": "Go",
        ".rs": "Rust",
        ".rb": "Ruby",
        ".php": "PHP",
        ".html": "HTML",
        ".css": "CSS",
        ".json": "JSON",
        ".xml": "XML",
        ".sh": "Shell",
        ".sql": "SQL",
        ".ipynb": "Jupyter Notebook",
        ".md": "Markdown",
        ".txt": "Plain Text"
    }

    return extension_map.get(ext, "Unknown")