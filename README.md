# AI Code Review Agent

## 1. Project Overview

AI Code Review Agent is a Streamlit-based web application that reviews GitHub repositories using Python, GitPython, AST parsing, and Gemini API.

The app allows a user to enter a public GitHub repository URL. It clones the repository, finds Python files, parses functions/classes/imports using Python AST, creates review chunks, sends selected chunks to Gemini, and displays structured review comments with severity, category, confidence score, suggestions, and verification status.

The goal of this project is to make code review easier by combining static code analysis with AI-generated suggestions while still marking uncertain comments for manual verification.

---

## 2. Features

- Clone public GitHub repositories using GitPython
- Use shallow cloning with `depth=1` for faster repository loading
- Store cloned repositories temporarily and delete them after analysis
- Find and parse Python files from the repository
- Ignore unnecessary folders like `.git`, `venv`, `__pycache__`, and `node_modules`
- Parse Python code using the built-in `ast` module
- Extract imports, functions, classes, docstrings, line numbers, and source code
- Create review chunks from functions and classes
- Review chunks using Gemini API
- Generate structured JSON review comments
- Show severity, category, confidence score, and suggestions
- Mark low-confidence comments as **Verify This**
- Filter comments by confidence, severity, and category
- Display results in a Streamlit dashboard
- Export review results as a Markdown report

---

## 3. Tech Stack

- Python
- Streamlit
- GitPython
- Python AST
- Gemini API
- Pandas
- python-dotenv

---

## 4. Project Structure

```text
AI-Code-Review-Agent/
│
├── app.py
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── src/
│   ├── __init__.py
│   ├── ingest.py
│   ├── parser.py
│   ├── reviewer.py
│   ├── pipeline.py
│   └── markdown.py
│
└── outputs/
    └── .gitkeep
```

---

## 5. Architecture

```text
User enters GitHub repository URL
        ↓
Repository is cloned using GitPython
        ↓
Python files are discovered and filtered
        ↓
Files are parsed using Python AST
        ↓
Functions and classes are converted into review chunks
        ↓
Chunks are reviewed using Gemini API
        ↓
Structured comments are generated
        ↓
Streamlit dashboard displays results
        ↓
Markdown report can be exported
```

---

## 6. Setup Instructions

### Clone the repository

```bash
git clone https://github.com/05Shubham-singh/AI-Code-Review-Agent.git
cd AI-Code-Review-Agent
```

### Create a virtual environment

```bash
python -m venv venv
```

### Activate the virtual environment

For Windows PowerShell:

```bash
.\venv\Scripts\Activate.ps1
```

If activation is blocked, run:

```bash
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate again:

```bash
.\venv\Scripts\Activate.ps1
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Create `.env` file

Create a `.env` file in the root folder and add:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash-lite
```

### Run the app

```bash
streamlit run app.py
```

---

## 7. Environment Variables

The project uses environment variables to keep API keys safe.

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash-lite
```

The real `.env` file is not uploaded to GitHub. Only `.env.example` is included to show which variables are required.

---

## 8. How It Works

1. The user enters a public GitHub repository URL.
2. The repository is cloned into a temporary folder using GitPython.
3. Python files are discovered and unnecessary folders are skipped.
4. Python AST is used to extract functions, classes, imports, docstrings, line numbers, and source code.
5. The extracted functions and classes are converted into smaller review chunks.
6. Selected chunks are sent to Gemini for AI-based review.
7. Gemini returns structured JSON review comments.
8. The comments are cleaned and normalized before display.
9. The Streamlit dashboard shows comments with severity, category, confidence score, and suggestions.
10. Comments with confidence below 70% are marked as **Verify This**.
11. The temporary repository is deleted after the review process.
12. The final review can be exported as a Markdown report.

---

## 9. Responsible AI Design

The app does not blindly trust AI-generated feedback.

Each review comment includes:

- Severity level
- Category
- Confidence score
- Verification flag
- Practical suggestion

Comments with confidence below 70% are marked as **Verify This**, so users know they should manually check those suggestions before applying them.

This design helps reduce blind trust in AI output and encourages human review before making code changes.

---

## 10. Known Limitations

- Current version focuses mainly on Python files.
- AST-based parsing is Python-specific.
- Gemini API quota may limit how many chunks can be reviewed.
- Large repositories may take more time to process.
- The app reviews selected chunks, not always the full repository.
- Some AI comments may still require manual verification.
- Private GitHub repositories are not supported in the current version.
- GitHub Pull Request inline comments are not included in the current version.

---

## 11. Future Improvements

- Add support for JavaScript, TypeScript, Java, and C++
- Add GitHub Pull Request inline comment support
- Add downloadable JSON reports
- Add support for private repositories
- Rank chunks based on importance before sending them to Gemini
- Add unit tests for parser, reviewer, and pipeline modules
- Improve duplicate comment removal
- Add charts for severity and category distribution
- Add better handling for very large repositories
- Add option to review only changed files in a pull request

---

## 12. Demo

Live Demo: Add your Streamlit Cloud or Hugging Face Spaces link here.

Demo Video: Add your Loom or YouTube unlisted demo video link here.

---

## 13. Author

**Shubham Singh**

GitHub: https://github.com/05Shubham-singh  
LinkedIn: https://www.linkedin.com/in/shubham-kumar-05s2005/

---

## 14. Website Link

LINK:-https://ai-code-review-agent-s.streamlit.app/

## 14. Note

This project was built as a student AI code review tool. The architecture, prompt design, parsing logic, review pipeline, and dashboard flow were designed step by step to make the project understandable, modular, and easy to extend.
