import ast
from pathlib import Path
from typing import Any, Dict, List


MAX_FILE_SIZE_KB = 500

def find_python_files(repo_path: Path) -> List[Path]:
    ignored_dirs = {
        ".git",
        "venv",
        ".venv",
        "__pycache__",
        "node_modules",
        "site-packages",
        ".mypy_cache",
        ".pytest_cache",
        ".streamlit",
    }
    python_files = []
    for file_path in repo_path.rglob("*.py"):
        if any(part in ignored_dirs for part in file_path.parts):
            continue
        try:
            size_kb = file_path.stat().st_size / 1024

            if size_kb <= MAX_FILE_SIZE_KB:
                python_files.append(file_path)
        except OSError:
            continue
    return python_files


def read_file_safely(file_path: Path) -> str:
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return file_path.read_text(encoding="latin-1", errors="ignore")


def get_source_segment(source: str, node: ast.AST) -> str:
    segment = ast.get_source_segment(source, node)
    return segment if segment else ""

def parse_python_file(file_path: Path, repo_path: Path) -> Dict[str, Any]:
    source = read_file_safely(file_path)
    relative_path = str(file_path.relative_to(repo_path))
    result = {
        "file_path": relative_path,
        "imports": [],
        "functions": [],
        "classes": [],
        "parse_error": None,
    }
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        result["parse_error"] = f"SyntaxError at line {error.lineno}: {error.msg}"
        return result

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                result["imports"].append(
                    {
                        "name": alias.name,
                        "line": node.lineno,
                    }
                )

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                result["imports"].append(
                    {
                        "name": f"{module}.{alias.name}",
                        "line": node.lineno,
                    }
                )

        elif isinstance(node, ast.FunctionDef):
            result["functions"].append(
                {
                    "name": node.name,
                    "line": node.lineno,
                    "end_line": getattr(node, "end_lineno", node.lineno),
                    "args_count": len(node.args.args),
                    "docstring": ast.get_docstring(node),
                    "code": get_source_segment(source, node),
                    "is_async": False,
                }
            )

        elif isinstance(node, ast.AsyncFunctionDef):
            result["functions"].append(
                {
                    "name": node.name,
                    "line": node.lineno,
                    "end_line": getattr(node, "end_lineno", node.lineno),
                    "args_count": len(node.args.args),
                    "docstring": ast.get_docstring(node),
                    "code": get_source_segment(source, node),
                    "is_async": True,
                }
            )

        elif isinstance(node, ast.ClassDef):
            methods = []
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods.append(item.name)
            result["classes"].append(
                {
                    "name": node.name,
                    "line": node.lineno,
                    "end_line": getattr(node, "end_lineno", node.lineno),
                    "methods": methods,
                    "docstring": ast.get_docstring(node),
                    "code": get_source_segment(source, node),
                }
            )
    return result

def parse_repository(repo_path: Path) -> List[Dict[str, Any]]:
    python_files = find_python_files(repo_path)
    parsed_files = []
    for file_path in python_files:
        parsed_file = parse_python_file(file_path, repo_path)
        parsed_files.append(parsed_file)
    return parsed_files

def create_review_chunks(parsed_files:List[Dict[str,Any]]) -> List[Dict[str,Any]]:
    chunks=[]
    for file_data in parsed_files:
        file_path=file_data["file_path"]
        if file_data.get("parse_error"):
            chunks.append(
                {
                    "file_path":file_path,
                    "symbol_type":"file",
                    "symbol_name":"PARSE_ERROR",
                    "line":1,
                    "end_line":1,
                    "code":file_data["parse_error"],
                    "metadata":{
                        "parse_error":True,
                        "reason":"File could not be parsed by Python AST",
                    },
                }
            )
            continue
        for function_data in file_data["functions"]:
            code=function_data.get("code","").strip()
            if not code:
                continue
            chunks.append(
                {
                    "file_path": file_path,
                    "symbol_type": "function",
                    "symbol_name": function_data["name"],
                    "line": function_data["line"],
                    "end_line": function_data["end_line"],
                    "code": code,
                    "metadata": {
                        "args_count": function_data.get("args_count", 0),
                        "has_docstring": bool(function_data.get("docstring")),
                        "is_async": bool(function_data.get("is_async", False)),
                    },                 
                }
            )
        for class_data in file_data["classes"]:
            code=class_data.get("code","").strip()
            if not code:
                continue
            chunks.append(
                {
                    "file_path": file_path,
                    "symbol_type": "class",
                    "symbol_name": class_data["name"],
                    "line": class_data["line"],
                    "end_line": class_data["end_line"],
                    "code": code,
                    "metadata": {
                        "methods": class_data.get("methods", []),
                        "method_count": len(class_data.get("methods", [])),
                        "has_docstring": bool(class_data.get("docstring")),
                    },
                }               
            )
    return chunks
