import os
import subprocess
import shutil
import tempfile
import logging
import json

logger = logging.getLogger(__name__)

# ---------------------------
# EXTENSIONS
# ---------------------------
CODE_EXT = {
    ".py", ".js", ".ts", ".cpp", ".c", ".java",
    ".go", ".rs", ".php", ".sh", ".ipynb"
}

CONFIG_EXT = {
    ".yaml", ".yml", ".json", ".toml",
    ".ini", ".cfg", ".env"
}

DOC_EXT = {
    ".md", ".txt", ".rst"
}

SPECIAL_FILES = {
    "Dockerfile", "docker-compose.yml",
    "requirements.txt", "setup.py", "Makefile"
}

IGNORE_DIRS = {
    ".git", "__pycache__", "venv", "node_modules", ".idea"
}

# ---------------------------
# TEMP PATH (NO CACHE AT ALL)
# ---------------------------
def get_repo_path():
    return tempfile.mkdtemp()

# ---------------------------
# CLONE (FULL CLONE)
# ---------------------------
def clone_repo(repo_url):
    logger.info(f"⬇️ Cloning repo | Repo: {repo_url}")

    path = get_repo_path()

    result = subprocess.run(
        ["git", "clone", repo_url, path],  # 🔥 FULL CLONE (no depth)
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        logger.error(result.stderr)
        raise Exception("Git clone failed")

    total_files = sum(len(files) for _, _, files in os.walk(path))
    logger.info(f"📂 Repo cloned | Files: {total_files}")

    if total_files == 0:
        raise ValueError("Empty repo")

    return path

# ---------------------------
# PUBLIC API
# ---------------------------
def get_repo(repo_url):
    return clone_repo(repo_url)

# ---------------------------
# FILE READER
# ---------------------------
def read_repo_files_clean(repo_path):
    data = {
        "code": {},
        "docs": {},
        "config": {},
        "infra": {}
    }

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            path = os.path.join(root, file)

            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except:
                continue

            if not content.strip():
                continue

            ext = os.path.splitext(file)[1].lower()
            name = file.lower()

            # NOTEBOOK SUPPORT
            if ext == ".ipynb":
                try:
                    nb = json.loads(content)
                    code_cells = [
                        "".join(cell["source"])
                        for cell in nb.get("cells", [])
                        if cell.get("cell_type") == "code"
                    ]
                    if code_cells:
                        data["code"][path] = "\n\n".join(code_cells)
                except:
                    continue

            elif file in SPECIAL_FILES:
                data["infra"][path] = content

            elif name == "readme.md":
                data["docs"][path] = content

            elif ext in DOC_EXT:
                data["docs"][path] = content

            elif ext in CONFIG_EXT:
                data["config"][path] = content

            elif ext in CODE_EXT:
                data["code"][path] = content

    logger.info(
        f"📊 Files scanned | Code: {len(data['code'])} | Docs: {len(data['docs'])}"
    )

    return data

# ---------------------------
# DELETE (CLEANUP)
# ---------------------------
def delete_repo(repo_path):
    logger.info(f"🗑️ Deleting repo | Path: {repo_path}")
    shutil.rmtree(repo_path, ignore_errors=True)