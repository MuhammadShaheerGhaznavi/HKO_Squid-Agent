import os
from pathlib import Path

# Try Streamlit secrets first (cloud deployment), fall back to .env (local)
try:
    import streamlit as st
    DEEPSEEK_API_KEY = st.secrets["DEEPSEEK_API_KEY"]
except Exception:
    from dotenv import load_dotenv
    load_dotenv()
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
LLM_MODEL = "deepseek-chat"

WORKSPACE_ROOT = Path(__file__).parent.resolve()
WIKI_DIR = WORKSPACE_ROOT / "wiki"
RAW_DIR = WORKSPACE_ROOT / "raw"
RAW_SOURCES_DIR = WORKSPACE_ROOT / "raw" / "sources"
CATALOG_FILE = WIKI_DIR / "catalog.json"

MAX_AGENT_ITERATIONS = 8
TOP_K_SEARCH = 10
MAX_TOKENS_PER_PAGE = 4000
MAX_CHUNK_TOKENS = 2500
CHUNK_OVERLAP_TOKENS = 400
TOKEN_BUDGET = 16000
LLM_MAX_OUTPUT_TOKENS = 2048
LLM_TEMPERATURE = 0.1
