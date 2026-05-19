import json 
import os
from typing import Any,Dict,List
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

def build_review_prompt(chunk:Dict[str,Any]) -> str:
    return f"""
You are helping review code for a student-built AI Code Review Agent project.
Review only the code block given below.Do not assume anything about files that are not shown.
Look for practical issues such as:
- possible bugs
- missing error handling
- security risks
- repeated or confusing logic
- readability problems
- testing improvements
Keep the feedback specific and useful. Avoid generic comments.
Return only valid JSON. Do not add markdown, headings, or extra explanation.
Rules:
- If the code looks fine, return: {{"comments": []}}
- Confidence must be between 0 and 100.
- If confidence is below 70, set needs_verification to true.
- If confidence is 70 or above, set needs_verification to false.
- Only mention issues visible in this code chunk.

File path: {chunk["file_path"]}
Symbol type: {chunk["symbol_type"]}
Symbol name: {chunk["symbol_name"]}
Starting line: {chunk["line"]}
Ending line: {chunk["end_line"]}
Metadata: {chunk.get("metadata", {})}

Code:
{chunk["code"]}
"""
def safe_json_loads(text:str) -> Dict[str,Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start=text.find("{")
        end=text.rfind("}")
        if start!= -1 and end !=-1 and end>start:
            try:
                return json.loads(text[start:end +1])
            except json.JSONDecodeError:
                return{"comments":[]}
        return{"comments":[]}

def clean_comment(item:Dict[str,Any],chunk:Dict[str,Any]) ->Dict[str,Any]:
    try:
        confidence=int(item.get("confidence",0))
    except (TypeError,ValueError):
        confidence=0
    
    confidence=max(0,min(100,confidence))
    severity=str(item.get("severity","low")).lower()
    category=str(item.get("category","maintainability")).lower()
    allowed_severities={"low","medium","high","critical"}
    allowed_categories={
        "bug","security","performance","maintainablility","readability","testing","style",
    }
    if severity not in allowed_severities:
        severity="low"
    if category not in allowed_categories:
        category="maintainability"
    return{
        "file_path":item.get("file_path",chunk["file_path"]),
        "symbol_name": item.get("symbol_name", chunk["symbol_name"]),
        "line": int(item.get("line", chunk["line"])),
        "severity": severity,
        "category": category,
        "comment": str(item.get("comment", "")).strip(),
        "suggestion": str(item.get("suggestion", "")).strip(),
        "confidence": confidence,
        "needs_verification": confidence < 70,
    }

def review_chunk_with_gemini(chunk:Dict[str,Any]) ->List[Dict[str,Any]]:
    api_key=os.getenv("GEMINI_API_KEY")
    model_name=os.getenv("GEMINI_MODEL","gemini-2.0-flash")

    if not api_key:
        raise EnvironmentError("GEMINI API KEY not found.")
    client=genai.Client(api_key=api_key)
    try:
        response=client.models.generate_content(
            model=model_name,
            contents=build_review_prompt(chunk),
            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json",           
            ),
        )
        parsed=safe_json_loads(response.text)
        raw_comments=parsed.get("comments",[])
        cleaned_comments=[]
        for item in raw_comments:
            cleaned=clean_comment(item,chunk)
            if cleaned["comment"]:
                cleaned_comments.append(cleaned)
        return cleaned_comments
    except Exception as error:
        return [
            {
                "file_path": chunk["file_path"],
                "symbol_name": chunk["symbol_name"],
                "line": chunk["line"],
                "severity": "low",
                "category": "maintainability",
                "comment": f"Gemini review failed for this chunk: {error}",
                "suggestion": "Check the API key, model name, internet connection, or Gemini request limits.",
                "confidence": 50,
                "needs_verification": True,
            }
        ]