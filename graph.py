import re
import builtins
from typing import Dict, List

# ---------------------------
# 1. CONFIG
# ---------------------------

STOPWORDS = {
    "for", "if", "else", "while", "do", "switch",
    "try", "except", "catch", "finally",
    "return", "import", "from", "as",
    "class", "def", "function",
    "var", "let", "const",
    "public", "private", "protected",
    "static", "void", "int", "float", "string",
    "true", "false", "null", "none",
    "with", "and", "or", "not",
    "all", "error", "to"
}

BUILTINS = set(dir(builtins))

FUNC_DEF_PATTERNS = [
    r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)",
    r"function\s+([a-zA-Z_][a-zA-Z0-9_]*)",
]

CLASS_DEF_PATTERNS = [
    r"class\s+([a-zA-Z_][a-zA-Z0-9_]*)"
]

CALL_PATTERN = r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\('


# ---------------------------
# 2. HELPERS
# ---------------------------

def is_valid_symbol(name: str) -> bool:
    return re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', name) is not None


def is_test(name: str) -> bool:
    return name.startswith("test_")


def is_variable_like(name: str) -> bool:
    return name.islower() and "_" not in name


# ---------------------------
# 3. EXTRACT DEFINITIONS
# ---------------------------

def extract_definitions(code_dict: Dict[str, str]) -> set:
    all_defs = set()

    for code in code_dict.values():

        for pattern in FUNC_DEF_PATTERNS:
            matches = re.findall(pattern, code)
            all_defs.update(matches)

        for pattern in CLASS_DEF_PATTERNS:
            matches = re.findall(pattern, code)
            all_defs.update(matches)

    return all_defs


# ---------------------------
# 4. BUILD GRAPH (FILTERED)
# ---------------------------

def build_dependency_graph(code_dict: Dict[str, str]) -> Dict[str, List[str]]:

    graph = {}
    all_defs = extract_definitions(code_dict)

    for file_path, code in code_dict.items():

        definitions = []
        for pattern in FUNC_DEF_PATTERNS:
            definitions += re.findall(pattern, code)

        calls = re.findall(CALL_PATTERN, code)

        for d in definitions:

            if d not in graph:
                graph[d] = []

            for c in calls:

                if c == d:
                    continue

                # 🔥 CRITICAL FILTER
                if c not in all_defs:
                    continue

                if c in BUILTINS:
                    continue

                graph[d].append(c)

    return graph


# ---------------------------
# 5. CLEAN GRAPH
# ---------------------------

def clean_graph(graph: Dict[str, List[str]]) -> Dict[str, List[str]]:

    cleaned = {}

    for node, deps in graph.items():

        # remove test + noise nodes
        if node in STOPWORDS or is_test(node) or is_variable_like(node):
            continue

        filtered = []

        for d in deps:

            if not is_valid_symbol(d):
                continue

            if d in STOPWORDS:
                continue

            if d in BUILTINS:
                continue

            if is_test(d):
                continue

            if is_variable_like(d):
                continue

            if len(d) < 3:
                continue

            filtered.append(d)

        filtered = list(set(filtered))

        if filtered:
            cleaned[node] = filtered

    return cleaned


# ---------------------------
# 6. PRUNE GRAPH
# ---------------------------

def prune_graph(graph: Dict[str, List[str]], max_degree=10):

    return {
        node: deps
        for node, deps in graph.items()
        if len(deps) <= max_degree
    }


# ---------------------------
# 7. IMPORTANCE (RANKING)
# ---------------------------

def get_top_nodes(graph: Dict[str, List[str]], top_k=10):

    importance = {}

    for node in graph:
        importance[node] = sum(node in deps for deps in graph.values())

    sorted_nodes = sorted(importance.items(), key=lambda x: x[1], reverse=True)

    return [n for n, _ in sorted_nodes[:top_k]]


# ---------------------------
# 8. GRAPH SUMMARY
# ---------------------------

def graph_to_summary(graph: Dict[str, List[str]], top_nodes: List[str]):

    lines = []

    for node in top_nodes:
        deps = graph.get(node, [])

        if deps:
            lines.append(f"{node} -> {', '.join(deps[:5])}")

    return "\n".join(lines)


# ---------------------------
# 9. MAIN PIPELINE
# ---------------------------

def build_clean_dependency_pipeline(code_dict: Dict[str, str]):

    raw_graph = build_dependency_graph(code_dict)
    cleaned = clean_graph(raw_graph)
    pruned = prune_graph(cleaned)
    top_nodes = get_top_nodes(pruned)
    summary = graph_to_summary(pruned, top_nodes)

    return {
        "clean_graph": pruned,
        "top_nodes": top_nodes,
        "summary": summary
    }


# ---------------------------
# 10. USAGE
# ---------------------------

