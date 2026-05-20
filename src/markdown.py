from typing import Any, Dict, List

def comments_to_markdown(result: Dict[str, Any]) -> str:
    summary = result["summary"]
    comments: List[Dict[str, Any]] = result["comments"]

    lines = []
    lines.append("# AI Code Review Report")
    lines.append("")
    lines.append(f"**Repository:** {summary['repo_url']}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Files parsed: {summary['files_parsed']}")
    lines.append(f"- Parse errors: {summary['parse_errors']}")
    lines.append(f"- Chunks created: {summary['chunks_created']}")
    lines.append(f"- Chunks reviewed: {summary['chunks_reviewed']}")
    lines.append(f"- Total comments: {summary['total_comments']}")
    lines.append(f"- High-confidence comments: {summary['high_confidence_comments']}")
    lines.append(f"- Low-confidence comments: {summary['low_confidence_comments']}")
    lines.append("")
    lines.append("## Review Comments")
    lines.append("")

    if not comments:
        lines.append("No review comments were generated.")
        return "\n".join(lines)

    for index, comment in enumerate(comments, start=1):
        verify_label = " — VERIFY THIS" if comment["needs_verification"] else ""
        lines.append(
            f"### {index}. {comment['severity'].upper()} — "
            f"{comment['category']}{verify_label}"
        )
        lines.append("")
        lines.append(f"**File:** `{comment['file_path']}`")
        lines.append("")
        lines.append(f"**Symbol:** `{comment['symbol_name']}`")
        lines.append("")
        lines.append(f"**Line:** {comment['line']}")
        lines.append("")
        lines.append(f"**Confidence:** {comment['confidence']}%")
        lines.append("")
        lines.append(f"**Comment:** {comment['comment']}")
        lines.append("")
        lines.append(f"**Suggestion:** {comment['suggestion']}")
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines)