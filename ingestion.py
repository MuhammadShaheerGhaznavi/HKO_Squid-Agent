import os
import sys
from pathlib import Path
from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from dotenv import load_dotenv

# LangChain / LangGraph imports
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END

# Import the existing wiki tools from your scripts directory
from scripts.wiki_tool import LLMWikiIngester, CatalogManager

load_dotenv()
deepseek_key = os.getenv('DEEPSEEK_API_KEY')

# =====================================================================
# 1. PYDANTIC SCHEMAS (Structured LLM Output)
# =====================================================================

class ExtractedWikiNote(BaseModel):
    title: str = Field(
        description="Clear, concise title of the atomic wiki note (e.g., 'Vector Indexing', 'GraphRAG Framework')."
    )
    type: Literal["concept", "entity", "procedure", "synthesis"] = Field(
        description="Category: 'concept' (core idea), 'entity' (tool/framework/person), 'procedure' (step-by-step guide), or 'synthesis' (higher-level comparison/overview)."
    )
    summary: str = Field(
        description="Brief 1-2 sentence description of this specific note."
    )
    keywords: List[str] = Field(
        default_factory=list,
        description="3-5 search keywords or tags for this entry."
    )
    content_body: str = Field(
        description="Full markdown content for the note body. Encourage embedding [[wiki-links]] to related concepts."
    )


class DocumentDecomposition(BaseModel):
    source_title: str = Field(description="Title of the raw source document.")
    summary: str = Field(description="Overall summary of the raw document.")
    notes: List[ExtractedWikiNote] = Field(
        description="List of extracted atomic wiki notes derived from the raw text."
    )


# =====================================================================
# 2. LANGGRAPH STATE DEFINITION
# =====================================================================

class IngestionState(TypedDict):
    raw_file_path: str
    source_id: str
    raw_content: str
    decomposition: Optional[DocumentDecomposition]
    generated_files: List[str]


# =====================================================================
# 3. GRAPH NODES
# =====================================================================

def read_raw_document(state: IngestionState) -> Dict[str, Any]:
    """Reads the raw source document from disk."""
    path = Path(state["raw_file_path"])
    if not path.exists():
        raise FileNotFoundError(f"Raw source file not found at: {path}")

    content = path.read_text(encoding="utf-8")
    source_id = path.stem  # e.g., 'example-doc' from 'raw/sources/example-doc.md'
    
    print(f"📄 Loaded source document: {path.name} ({len(content)} characters)")
    return {"raw_content": content, "source_id": source_id}


def extract_wiki_notes(state: IngestionState) -> Dict[str, Any]:
    """Prompts the LLM to break down the raw document into structured wiki notes."""
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")

    llm = ChatOpenAI(
        model="deepseek-chat",
        api_key=deepseek_key,
        base_url="https://api.deepseek.com/v1",
        temperature=0.2
    )

    # Force json_mode method for DeepSeek compatibility
    structured_llm = llm.with_structured_output(DocumentDecomposition, method="json_mode")

    system_prompt = """You are an expert knowledge management assistant building an Obsidian/Wiki-style knowledge base.
Your job is to analyze raw documents and break them down into modular, highly linked, atomic wiki notes.

You MUST respond strictly in valid JSON matching the required schema.

Rules:
1. Break complex documents into distinct notes categorized as:
   - 'concept': Core theoretical ideas, formulas, or principles.
   - 'entity': Specific tools, libraries, products, or frameworks.
   - 'procedure': Step-by-step instructions, workflows, or setup guides.
   - 'synthesis': Comparative analysis, high-level overviews, or architectural summaries.
2. Ensure each note is self-contained and atomic.
3. Use [[wiki-link]] syntax inside 'content_body' to connect related terms or concepts to other wiki pages.

JSON Schema format to follow:
{{
  "source_title": "Document Title",
  "summary": "Document Summary",
  "notes": [
    {{
      "title": "Note Title",
      "type": "concept|entity|procedure|synthesis",
      "summary": "1-2 sentence description",
      "keywords": ["keyword1", "keyword2"],
      "content_body": "Markdown text..."
    }}
  ]
}}
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Raw Document Title/ID: {source_id}\n\nContent:\n{content}")
    ])

    chain = prompt | structured_llm
    
    print("🤖 Processing raw document with LLM...")
    result: DocumentDecomposition = chain.invoke({
        "source_id": state["source_id"],
        "content": state["raw_content"]
    })

    print(f"✨ Extracted {len(result.notes)} distinct wiki notes.")
    return {"decomposition": result}


def write_wiki_files(state: IngestionState) -> Dict[str, Any]:
    """Writes all extracted wiki notes to their target folders inside wiki/."""
    decomposition = state["decomposition"]
    source_id = state["source_id"]
    source_link = f"[[raw/sources/{source_id}]]"

    created_paths = []

    for note in decomposition.notes:
        file_path = LLMWikiIngester.create_wiki_note_file(
            note_type=note.type,
            title=note.title,
            summary=note.summary,
            sources=[source_link],
            keywords=note.keywords,
            content_body=note.content_body
        )
        created_paths.append(str(file_path))

    return {"generated_files": created_paths}


def sync_wiki_catalog(state: IngestionState) -> Dict[str, Any]:
    """Updates catalog.json and rebuilds index.md using CatalogManager."""
    print("🔄 Synchronizing wiki catalog and index...")
    manager = CatalogManager()
    manager.sync_all()
    return {}


# =====================================================================
# 4. WORKFLOW GRAPH BUILDER
# =====================================================================

def build_ingestion_graph():
    workflow = StateGraph(IngestionState)

    # Add Nodes
    workflow.add_node("read_doc", read_raw_document)
    workflow.add_node("extract_notes", extract_wiki_notes)
    workflow.add_node("write_files", write_wiki_files)
    workflow.add_node("sync_catalog", sync_wiki_catalog)

    # Set Edges
    workflow.add_edge(START, "read_doc")
    workflow.add_edge("read_doc", "extract_notes")
    workflow.add_edge("extract_notes", "write_files")
    workflow.add_edge("write_files", "sync_catalog")
    workflow.add_edge("sync_catalog", END)

    return workflow.compile()


# =====================================================================
# 5. EXECUTION ENTRY POINT
# =====================================================================

if __name__ == "__main__":
    # Expect raw file path as command line argument, or use fallback example
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    else:
        # Example default path
        target_file = "raw/sources/sample.md"

    app = build_ingestion_graph()

    initial_state: IngestionState = {
        "raw_file_path": target_file,
        "source_id": "",
        "raw_content": "",
        "decomposition": None,
        "generated_files": []
    }

    try:
        app.invoke(initial_state)
        print("\n🎉 Ingestion complete!")
    except Exception as e:
        print(f"\n❌ Ingestion failed: {e}")