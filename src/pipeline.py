from typing import Any,Dict,List
from src.ingest import clone_repository, cleanup_repository
from src.parser import parse_repository, create_review_chunks
from src.reviewer import review_chunk_with_gemini

def run_code_review_pipeline(repo_url:str,max_chunks:int=10,) -> Dict[str,Any]:
    repo_path=None
    try:
        repo_path=clone_repository(repo_url)
        parsed_files=parse_repository(repo_path)
        review_chunks=create_review_chunks(parsed_files)
        selected_chunks=review_chunks[:max_chunks]
        all_comments:List[Dict[str,Any]]=[]
        for index,chunk in enumerate(selected_chunks,start=1):
            print(
                f"Reviewing chunk{index}/{len(selected_chunks)}:"
                f"{chunk["file_path"]}->{chunk['symbol_name']}"
            )
            comments=review_chunk_with_gemini(chunk)
            all_comments.extend(comments)

        summary=build_summary(
            repo_url=repo_url,
            parsed_files=parsed_files,
            review_chunks=review_chunks,
            selected_chunks=selected_chunks,
            comments=all_comments,            
        )
        return {
            "summary": summary,
            "comments": all_comments,
            "parsed_files": parsed_files,
            "reviewed_chunks": selected_chunks,
        }
    finally:
        if repo_path:
            cleanup_repository(repo_path)

def build_summary(    repo_url: str,parsed_files: List[Dict[str, Any]], review_chunks: List[Dict[str, Any]],
    selected_chunks: List[Dict[str, Any]],comments: List[Dict[str, Any]],) -> Dict[str, Any]:
    parsed_error_count=len([file_data for file_data in parsed_files if file_data.get("parse_error")])
    low_confidence_count = len([comment for comment in comments if comment.get("confidence", 0) < 70])
    high_confidence_count = len([comment for comment in comments if comment.get("confidence", 0) >= 70])
    severity_counts = {}   

    for comment in comments:
        severity=comment.get("severity","low")
        severity_counts[severity]=severity_counts.get(severity,0)+1
    
    category_counts={}
    for comment in comments:
        category = comment.get("category", "maintainability")
        category_counts[category]=category_counts.get(category,0)+1
    return {
        "repo_url": repo_url,
        "files_parsed": len(parsed_files),
        "parse_errors": parsed_error_count,
        "chunks_created": len(review_chunks),
        "chunks_reviewed": len(selected_chunks),
        "total_comments": len(comments),
        "high_confidence_comments": high_confidence_count,
        "low_confidence_comments": low_confidence_count,
        "severity_counts": severity_counts,
        "category_counts": category_counts,
    }