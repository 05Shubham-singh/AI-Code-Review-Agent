from pathlib import Path
from typing import List 

Max_File_size_KB=500

def find_pythonfiles(repo_path:Path)->List[Path]:
    ignored_dirs={   ".git",
        "venv",
        ".venv",
        "__pycache__",
        "node_modules",
        "site-packages",
        ".mypy_cache",
        ".pytest_cache",
        ".streamlit",}
    
    python_files=[]
    for file_path in repo_path.rglob("*.py"):
        if any(part in ignored_dirs for part in file_path.parts):
            continue
        try:
            size_kb=file_path.stat().st_size/1024 

            if size_kb<=Max_File_size_KB:
                python_files.append(file_path)
        except OSError:
            continue
    return python_files
