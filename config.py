import tempfile
from pathlib import Path

def _clean_secret(value) -> str:
    if value is None:
        return ""
    return str(value).strip().strip('"').strip("'")


def _key_usable(value: str) -> bool:
    # Example templates use "sk-..."; a real DeepSeek key is much longer.
    return bool(value) and value not in {"sk-...", "sk-"} and len(value) >= 20


def _env_file_values() -> dict:
    """Read .env directly. Streamlit copies secrets into os.environ, so getenv would keep the placeholder."""
    try:
        from dotenv import dotenv_values
        return dict(dotenv_values(Path(__file__).resolve().parent / ".env"))
    except Exception:
        return {}


# Try Streamlit secrets first (cloud deployment), fall back to .env (local)
_KEY_SOURCE = "unknown"
_KEY_LOAD_ERROR = ""
_SECRETS_KEY = ""
try:
    import streamlit as st
    _SECRETS_KEY = _clean_secret(st.secrets["DEEPSEEK_API_KEY"])
    R2_ENDPOINT_URL = st.secrets.get("R2_ENDPOINT_URL", "")
    R2_BUCKET = st.secrets.get("R2_BUCKET", "")
    R2_ACCESS_KEY_ID = st.secrets.get("R2_ACCESS_KEY_ID", "")
    R2_SECRET_ACCESS_KEY = st.secrets.get("R2_SECRET_ACCESS_KEY", "")
    _KEY_SOURCE = "streamlit_secrets"
except Exception as _e:
    _KEY_LOAD_ERROR = type(_e).__name__ + ":" + str(_e)[:120]
    _env = _env_file_values()
    _SECRETS_KEY = ""
    R2_ENDPOINT_URL = _env.get("R2_ENDPOINT_URL", "") or ""
    R2_BUCKET = _env.get("R2_BUCKET", "") or ""
    R2_ACCESS_KEY_ID = _env.get("R2_ACCESS_KEY_ID", "") or ""
    R2_SECRET_ACCESS_KEY = _env.get("R2_SECRET_ACCESS_KEY", "") or ""
    DEEPSEEK_API_KEY = _clean_secret(_env.get("DEEPSEEK_API_KEY"))
    _KEY_SOURCE = "dotenv"

if _KEY_SOURCE == "streamlit_secrets" and not _key_usable(_SECRETS_KEY):
    _env_key = _clean_secret(_env_file_values().get("DEEPSEEK_API_KEY"))
    if _key_usable(_env_key):
        DEEPSEEK_API_KEY = _env_key
        _KEY_SOURCE = "dotenv_fallback"
    else:
        DEEPSEEK_API_KEY = _SECRETS_KEY
elif _KEY_SOURCE == "streamlit_secrets":
    DEEPSEEK_API_KEY = _SECRETS_KEY

DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
LLM_MODEL = "deepseek-chat"

WORKSPACE_ROOT = Path(__file__).parent.resolve()
WIKI_DIR = WORKSPACE_ROOT / "wiki"
RAW_DIR = WORKSPACE_ROOT / "raw"
RAW_SOURCES_DIR = WORKSPACE_ROOT / "raw" / "sources"
CATALOG_FILE = WIKI_DIR / "catalog.json"
# Ephemeral on Streamlit Cloud; persistent enough within a session for PDF reuse
RAW_CACHE_DIR = Path(tempfile.gettempdir()) / "hko_squid" / "raw"
# Object key prefix inside the R2 bucket (upload + download must match)
R2_RAW_PREFIX = "raw/"

MAX_AGENT_ITERATIONS = 8
TOP_K_SEARCH = 10
MAX_TOKENS_PER_PAGE = 4000
MAX_CHUNK_TOKENS = 2500
CHUNK_OVERLAP_TOKENS = 400
TOKEN_BUDGET = 16000
LLM_MAX_OUTPUT_TOKENS = 2048
LLM_TEMPERATURE = 0.1
