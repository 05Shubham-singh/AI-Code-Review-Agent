import re
import shutil 
import tempfile 
from pathlib import Path
from git import Repo

GITHUB_URL_CHECK=re.compile( r"^https:\/\/github\.com\/[\w.-]+\/[\w.-]+(?:\.git)?$")

def fine_github_url(repo_url:str) -> bool:
    if not repo_url:
        return False
    repo_url=repo_url.strip()
    return bool(GITHUB_URL_CHECK.match(repo_url))

def clone_repository(repo_url:str) ->Path:
    repo_url=repo_url.strip()
    if not fine_github_url(repo_url):
        raise ValueError("Invalid GITHUB URL. Use correct format: https://github.com/username/repository")
    temp_dir=Path(tempfile.mkdtemp(prefix="code_review_repo"))
    try:
        Repo.clone_from(repo_url,temp_dir,depth=1)
        return temp_dir
    except Exception as error:
        shutil.rmtree(temp_dir,ignore_errors=True)
        raise RuntimeError(f"Failed to clone repository: {error}")
    
def cleanup_repository(repo_path:Path)->None:
    if repo_path and repo_path.exists():
        shutil.rmtree(repo_path,ignore_errors=True)

