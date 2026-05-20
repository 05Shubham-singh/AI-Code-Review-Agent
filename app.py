import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from src.pipeline import run_code_review_pipeline
import json
from src.markdown import comments_to_markdown

st.set_page_config(
    page_title="AI Code Review Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)
load_dotenv()
def load_secrets_for_deployment():
    try:
        if "GEMINI_API_KEY" in st.secrets:
            os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
        if "GEMINI_MODEL" in st.secrets:
            os.environ["GEMINI_MODEL"] = st.secrets["GEMINI_MODEL"]
    except Exception:
        pass

def render_header():
    st.markdown(
        """
        <div style="padding: 1.4rem 1.6rem; border-radius: 18px; background-color: #111827; margin-bottom: 1.5rem;">
            <h1 style="margin: 0; color: white;">🤖 AI Code Review Agent</h1>
            <p style="margin-top: 0.6rem; color: #d1d5db; font-size: 1rem;">
                Clone a GitHub repository, parse Python code with AST, review code chunks with Gemini,
                and generate confidence-rated review comments.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_sidebar():
    with st.sidebar:
        st.title("⚙️ Review Settings")
        repo_url = st.text_input(
            "GitHub Repository URL",
            placeholder="https://github.com/username/repository",
        )
        max_chunks = st.slider(
            "Maximum chunks to review",
            min_value=1,
            max_value=30,
            value=5,
            step=1,
            help="Keep this low while testing to save Gemini API quota.",
        )
        st.divider()
        min_confidence = st.slider(
            "Minimum confidence",
            min_value=0,
            max_value=100,
            value=0,
            step=5,
        )
        st.markdown("### Severity")
        severity_options = ["low", "medium", "high", "critical"]
        severity_filter = []
        for severity in severity_options:
            if st.checkbox(
                severity.capitalize(),
                value=True,
                key=f"severity_{severity}",
            ):
                severity_filter.append(severity)
        st.markdown("### Category")
        category_options = [
            "bug",
            "security",
            "performance",
            "maintainability",
            "readability",
            "testing",
            "style",
        ]
        category_filter = []
        for category in category_options:
            label = category.replace("_", " ").capitalize()
            if st.checkbox(
                label,
                value=True,
                key=f"category_{category}",
            ):
                category_filter.append(category)
        st.divider()
        run_button = st.button(
            "🚀 Run Code Review",
            type="primary",
            use_container_width=True,
        )
    return repo_url, max_chunks, min_confidence, severity_filter, category_filter, run_button

def render_summary(summary):
    st.subheader("📊 Review Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Files Parsed", summary.get("files_parsed", 0))
    col2.metric("Chunks Created", summary.get("chunks_created", 0))
    col3.metric("Chunks Reviewed", summary.get("chunks_reviewed", 0))
    col4.metric("Total Comments", summary.get("total_comments", 0))
    col5, col6, col7 = st.columns(3)
    col5.metric("Parse Errors", summary.get("parse_errors", 0))
    col6.metric("High Confidence", summary.get("high_confidence_comments", 0))
    col7.metric("Low Confidence", summary.get("low_confidence_comments", 0))

def render_comments(comments, min_confidence, severity_filter, category_filter):
    if not comments:
        st.success("No review comments were generated for the selected chunks.")
        return
    if not severity_filter:
        st.warning("Please select at least one severity.")
        return
    if not category_filter:
        st.warning("Please select at least one category.")
        return
    df = pd.DataFrame(comments)
    required_columns = ["confidence", "severity", "category"]
    for column in required_columns:
        if column not in df.columns:
            st.error(f"Missing column in review result: {column}")
            return
    filtered_df = df[
        (df["confidence"] >= min_confidence)
        & (df["severity"].isin(severity_filter))
        & (df["category"].isin(category_filter))
    ]
    tab1, tab2, tab3 = st.tabs(["📝 Review Comments", "⚠️ Verify This", "📄 Raw Data"])
    with tab1:
        st.subheader("Review Comments")
        if filtered_df.empty:
            st.info("No comments match the selected filters.")
            return
        for _, row in filtered_df.iterrows():
            needs_verification = row.get("needs_verification", False)
            verify_label = " | VERIFY THIS" if needs_verification else ""
            title = (
                f"{str(row['severity']).upper()} | {row['category']} | "
                f"{row['file_path']}:{row['line']} | "
                f"{row['confidence']}%{verify_label}"
            )
            with st.expander(title):
                st.write(f"**Symbol:** `{row['symbol_name']}`")
                st.write(f"**Comment:** {row['comment']}")
                suggestion = row.get("suggestion", "")
                if suggestion:
                    st.write(f"**Suggestion:** {suggestion}")
                else:
                    st.write("**Suggestion:** No specific suggestion returned.")
    with tab2:
        st.subheader("Verify This")
        verify_df = filtered_df[
            (filtered_df["needs_verification"] == True)
            | (filtered_df["confidence"] < 70)
        ]
        if verify_df.empty:
            st.success("No comments need manual verification.")
        else:
            st.warning(
                "These comments have lower confidence or may depend on missing project context. "
                "Please verify them before applying changes."
            )
            for _, row in verify_df.iterrows():
                with st.expander(
                    f"VERIFY THIS | {row['file_path']}:{row['line']} | {row['confidence']}%"
                ):
                    st.write(f"**Symbol:** `{row['symbol_name']}`")
                    st.write(f"**Severity:** {row['severity']}")
                    st.write(f"**Category:** {row['category']}")
                    st.write(f"**Comment:** {row['comment']}")
                    suggestion = row.get("suggestion", "")
                    if suggestion:
                        st.write(f"**Suggestion:** {suggestion}")
                    else:
                        st.write("**Suggestion:** No specific suggestion returned.")
    with tab3:
        st.subheader("Raw Review Data")
        st.dataframe(filtered_df, use_container_width=True)

    st.divider()

    st.subheader("Download Report")

    markdown_report = comments_to_markdown(result)
    json_report = json.dumps(result["comments"], indent=2)

    col_download_1, col_download_2 = st.columns(2)

    with col_download_1:
        st.download_button(
            label="Download Markdown Report",
            data=markdown_report,
            file_name="ai_code_review_report.md",
            mime="text/markdown",
        )

    with col_download_2:
        st.download_button(
            label="Download JSON Report",
            data=json_report,
            file_name="ai_code_review_report.json",
            mime="application/json",
        )
    

load_secrets_for_deployment()
render_header()

repo_url, max_chunks, min_confidence, severity_filter, category_filter, run_button = render_sidebar()
st.info("Enter a public GitHub repository URL from the sidebar and click **Run Code Review**.")

if run_button:
    if not repo_url.strip():
        st.error("Please enter a GitHub repository URL.")
        st.stop()
    if not os.getenv("GEMINI_API_KEY"):
        st.error(
            "GEMINI_API_KEY not found. Add it to `.env` locally or Streamlit secrets after deployment.")
        st.stop()
    if not severity_filter:
        st.warning("Please select at least one severity.")
        st.stop()
    if not category_filter:
        st.warning("Please select at least one category.")
        st.stop()
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        status_text.info("Cloning repository and running review pipeline...")
        progress_bar.progress(20)
        result = run_code_review_pipeline(
            repo_url=repo_url,
            max_chunks=max_chunks,
        )
        progress_bar.progress(100)
        status_text.success("Code review completed successfully.")
        st.session_state["review_result"] = result

    except Exception as error:
        progress_bar.empty()
        status_text.empty()
        st.error(f"Pipeline failed: {error}")
        st.stop()

if "review_result" in st.session_state:
    result = st.session_state["review_result"]
    st.divider()
    summary = result.get("summary", {})
    comments = result.get("comments", [])
    render_summary(summary)
    st.divider()
    render_comments(
        comments=comments,
        min_confidence=min_confidence,
        severity_filter=severity_filter,
        category_filter=category_filter,
    )