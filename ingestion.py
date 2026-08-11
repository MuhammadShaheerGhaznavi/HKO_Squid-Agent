import json
import os
import re
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Literal, Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from dotenv import load_dotenv

# LangChain / LangGraph imports
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END

# Import the existing wiki tools from your scripts directory
from scripts.wiki_tool import LLMWikiIngester, CatalogManager, WIKI_DIR

load_dotenv()
deepseek_key = os.getenv('DEEPSEEK_API_KEY')

# =====================================================================
# 1. PYDANTIC SCHEMAS (Structured LLM Output)
# =====================================================================

class ExtractedWikiNote(BaseModel):
    title: str = Field( ## Feild is used to fine-control attributes 
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
        description="Full markdown content for the note body. Encourage embedding [[wiki-links]] to related concepts." ## ARE WE LINKING RELATED CONCEPTS WITH EACH OTHER??
    )


class DocumentDecomposition(BaseModel): # Related to decomposing raw documents
    source_title: str = Field(description="Title of the raw source document.")
    summary: str = Field(description="Overall summary of the raw document.")
    notes: List[ExtractedWikiNote] = Field(
        description="List of extracted atomic wiki notes derived from the raw text."
    )


class DocumentSection(BaseModel): ## Understand this !!! **
    section_id: str = Field(
        default="",
        description="Unique short identifier, e.g. '5.1' or 'refinements-caching'. Derived from start_marker if empty."
    )
    title: str = Field(
        default="",
        description="The full section heading text. Derived from start_marker if empty."
    )
    level: int = Field(description="1 for top-level section, 2 for subsection within a parent section.")
    start_marker: str = Field(description="A ~50-80 character unique snippet from the beginning of this section (include the heading). Must be distinctive enough to locate via str.find() in the source text.")
    end_marker: str = Field(description="A ~50-80 character snippet from the beginning of the NEXT section in reading order. Use 'END_OF_DOC' for the last section.")
    page_start: int = Field(default=0, description="PDF page number where this section starts (1-indexed, from TOC). 0 = not a PDF section.")
    page_end: int = Field(default=0, description="PDF page number where NEXT section starts (1-indexed, from TOC). 0 = not a PDF section.")


class DocumentStructure(BaseModel):
    document_title: str = Field(
        default="",
        description="Overall document title. Derived from first section if empty."
    )
    sections: List[DocumentSection] = Field(min_length=1, description="All identified sections and subsections in reading order.")


class SectionExtraction(BaseModel): ## Like DocumentDecomposition class but for sections??
    notes: List[ExtractedWikiNote] = Field(description="Wiki notes extracted from this section or batch of sections.")


class MergedNote(BaseModel):
    title: str = Field(description="Title for the consolidated note.")
    type: Literal["concept", "entity", "procedure", "synthesis"] = Field(description="Category of the merged note.")
    summary: str = Field(description="1-2 sentence summary of the merged concept.")
    keywords: List[str] = Field(description="3-6 searchable keywords from the merged notes.")
    content_body: str = Field(
        default="",
        alias="content",
        description="Comprehensive markdown content merging all unique information from the input notes."
    )

    model_config = {"populate_by_name": True}


# =====================================================================
# 2. LANGGRAPH STATE DEFINITION
# =====================================================================

class IngestionState(TypedDict):
    raw_file_path: str
    source_id: str
    raw_content: str
    sections: Optional[List[DocumentSection]]
    decomposition: Optional[DocumentDecomposition]
    generated_files: List[str]
    toc: Optional[List[Dict[str, Any]]]  # Table of contents extracted from PDF


# =====================================================================
# 3. CONFIGURATION
# =====================================================================

SINGLE_PASS_THRESHOLD = 12000 ## If document under 12k chars, just use single pass LLM
LLM_SAMPLED_THRESHOLD = 60000  ## Documents above this get regex/TOC-based chapters, not LLM
BATCH_TARGET = 40000  ## chars per batch — increased from 10K for efficiency (DeepSeek = 128K context)
MAX_PARALLEL_BATCHES = 4  ## concurrent LLM calls for batch extraction
MAX_PARALLEL_MERGES = 4   ## concurrent LLM calls for note consolidation
PROGRESS_DIR = Path(__file__).parent / ".ingestion_progress"


# =====================================================================
# 4. GRAPH NODES
# =====================================================================

def read_raw_document(state: IngestionState) -> Dict[str, Any]: # Handle .MD and .PDF files atm?
    """Reads the raw source document from disk. Supports .md, .txt, and .pdf files.
    For PDFs, also extracts the table of contents natively via PyMuPDF."""
    path = Path(state["raw_file_path"])
    if not path.exists():
        raise FileNotFoundError(f"Raw source file not found at: {path}")

    suffix = path.suffix.lower()
    source_id = path.stem
    toc: Optional[List[Dict[str, Any]]] = None

    if suffix == ".pdf":
        import fitz # module to read/extract data from PDF files
        doc = fitz.open(str(path))
        content = "\n\n".join(page.get_text() for page in doc)

        raw_toc = doc.get_toc(simple=False)  # returns list of (level, title, page, dest) tuples
        if raw_toc:
            toc = []
            for entry in raw_toc:
                toc.append({
                    "level": entry[0],
                    "title": entry[1].strip(),
                    "page": entry[2],
                })
            print(f"📑 Extracted PDF TOC: {len(toc)} entries (levels: {set(e['level'] for e in toc)})")

        page_count = doc.page_count
        doc.close()
        print(f"📄 Loaded PDF document: {path.name} ({len(content)} characters)")

        # Save TOC as sidecar for retrieval agent page-jump
        if toc:
            toc_path = path.with_suffix(".toc.json")
            toc_data = {
                "source": path.name,
                "total_pages": page_count,
                "entries": toc,
            }
            toc_path.write_text(json.dumps(toc_data, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"📑 Saved TOC sidecar: {toc_path.name} ({len(toc)} entries)")
    else:
        content = path.read_text(encoding="utf-8")
        print(f"📄 Loaded source document: {path.name} ({len(content)} characters)")

    return {"raw_content": content, "source_id": source_id, "toc": toc}


def _create_llm():
    """Helper to create the DeepSeek LLM instance with structured output."""
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    return ChatOpenAI(
        model="deepseek-chat",
        api_key=deepseek_key,
        base_url="https://api.deepseek.com/v1",
        temperature=0.2
    )


def _find_marker(text: str, marker: str, start: int = 0) -> int:  ## UNDERSTAND THIS!! **
    """Fuzzy-find a marker in text, handling PDF line-break and whitespace variations."""
    if not marker:
        return -1

    def _normalize(s: str) -> str:
        return re.sub(r"\s+", " ", s.replace("\n", " ").replace("\r", " ")).strip().lower()

    normalized_text = _normalize(text)
    normalized_marker = _normalize(marker)

    pos = normalized_text.find(normalized_marker, start)
    if pos >= 0:
        return pos

    marker_words = [w for w in normalized_marker.split() if len(w) > 2] # gets words in normalized_marker that are longer than 2 chars
    for length in [20, 12, 8, 5, 3]:
        if len(marker_words) >= length:
            candidate = " ".join(marker_words[:length])
            pos = normalized_text.find(candidate, start)
            if pos >= 0:
                return pos

    for word in reversed(marker_words):
        pos = normalized_text.find(word, start)
        if pos >= 0:
            return max(0, pos - 50)

    return -1


def _select_toc_depth(toc: List[Dict[str, Any]]) -> int:
    """Choose optimal TOC depth: finest level with >= 10 entries, else coarsest available."""
    if not toc:
        return 1
    levels = sorted(set(e["level"] for e in toc))
    counts = {lvl: sum(1 for e in toc if e["level"] == lvl) for lvl in levels}
    for lvl in sorted(levels, reverse=True):
        if counts[lvl] >= 10:
            print(f"📑 TOC depth: using level-{lvl} ({counts[lvl]} entries) over level-{min(levels)} ({counts[min(levels)]} entries).")
            return lvl
    return max(levels)


def _extract_sections_from_toc(toc: List[Dict[str, Any]], total_pages: int) -> List[DocumentSection]:
    """Build DocumentSection list from PyMuPDF TOC using page ranges (deterministic, no marker matching).
    Selects optimal TOC depth automatically."""
    if len(toc) < 2:
        return []

    depth = _select_toc_depth(toc)
    filtered = [t for t in toc if t["level"] == depth]

    # If chosen depth has < 2 entries, fall back to coarser
    if len(filtered) < 2:
        for alt_depth in sorted(set(e["level"] for e in toc)):
            filtered = [t for t in toc if t["level"] == alt_depth]
            if len(filtered) >= 2:
                depth = alt_depth
                break

    if len(filtered) < 2:
        return []

    sections: List[DocumentSection] = []
    for i, entry in enumerate(filtered):
        title = entry["title"]
        section_id = re.sub(r"[^\w\-_]", "-", title.lower()).strip("-")[:40]
        page_start = entry["page"]  # 1-indexed from PyMuPDF

        if i < len(filtered) - 1:
            page_end = filtered[i + 1]["page"]
        else:
            page_end = total_pages + 1  # extends to end of document

        # Keep markers as fallback for non-PDF documents, derive from title
        start_marker = title
        end_marker = filtered[i + 1]["title"] if i < len(filtered) - 1 else "END_OF_DOC"

        sections.append(DocumentSection(
            section_id=section_id or f"section-{i+1}",
            title=title,
            level=depth,
            start_marker=start_marker,
            end_marker=end_marker,
            page_start=page_start,
            page_end=page_end,
        ))

    return sections


def _extract_sections_from_regex(content: str) -> List[DocumentSection]:
    """Regex-based chapter/section detection as fallback when TOC is unavailable."""
    patterns = [
        # Numbered: "1. Section Name", "1.1 Subsection", "Chapter 1"
        r'^[#]{0,3}\s*(?:Chapter\s+)?(\d+(?:\.\d+)*)\s+[A-Z].+$',
        # ALL CAPS line followed by content (common in government/legal docs)
        r'^([A-Z][A-Z\s\-]{10,})$',
        # Roman numeral: "I. Introduction"
        r'^(?=[MDCLXVI]+\.\s)[MDCLXVI]+\.\s+[A-Z].+$',
    ]

    lines = content.split("\n")
    headings: List[Tuple[int, str]] = []

    for idx, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or len(stripped) < 4:
            continue

        for pattern in patterns:
            if re.match(pattern, stripped):
                headings.append((idx, stripped))
                break

    if len(headings) < 3:
        return []

    sections = []
    for i, (line_idx, title) in enumerate(headings):
        section_id = re.sub(r"[^\w\-_]", "-", title.lower()).strip("-")[:40]
        start_marker = title

        if i < len(headings) - 1:
            end_marker = headings[i + 1][1]
        else:
            end_marker = "END_OF_DOC"

        sections.append(DocumentSection(
            section_id=section_id or f"section-{i+1}",
            title=title,
            level=1,
            start_marker=start_marker,
            end_marker=end_marker,
        ))

    return sections


def _extract_sections_from_llm(content: str, source_id: str) -> List[DocumentSection]:
    """LLM-based structure analysis as last resort for medium-sized documents.
    For very large documents, samples the document instead of sending full content."""
    llm = _create_llm()
    structured_llm = llm.with_structured_output(DocumentStructure, method="json_mode") ## parses the raw string (json) directly into an instance of DocumentStructure

    # For large docs, sample: first 15K + last 10K chars + page numbers to reduce tokens
    if len(content) > LLM_SAMPLED_THRESHOLD:
        sample = content[:15000] + "\n\n[... middle of document omitted ...]\n\n" + content[-10000:]
        print(f"📐 Document is large ({len(content)} chars); sending {len(sample)}-char sample for structure analysis.")
        doc_content = sample
    else:
        doc_content = content

    system_prompt = """You are a document structure analyzer. Your job is to identify TOP-LEVEL CHAPTERS (not subsections) so each can be processed individually for knowledge extraction.

Rules:
1. Identify ONLY top-level chapters/sections (e.g., "1 Introduction", "4 Implementation", "6 Refinements", "8 Real Applications"). Do NOT break out internal subsections like "5.1 Tablet Location" or "Locality groups" within a chapter.
2. Each section's start_marker and end_marker should span the ENTIRE chapter content, including all of its subsections. Use the chapter heading as start_marker and the NEXT chapter heading as end_marker.
3. For each section output ALL fields: section_id, title, level, start_marker, end_marker. Set level=1 for all chapters.
4. section_id: short kebab-case identifier like "introduction", "implementation", "refinements".
5. title: the chapter heading text (e.g., "4 Implementation").
6. start_marker: unique ~60-char snippet from the beginning of the chapter. Must be verbatim from the document.
7. end_marker: unique ~60-char snippet from the beginning of the NEXT chapter. Use "END_OF_DOC" for the last chapter.
8. Also output the top-level document_title field with the document's main title.
9. Include ALL substantive chapters (Introduction through Conclusions/Acknowledgements).

Output pure JSON matching the schema exactly. Do not omit any fields."""

    human_message = f"Document title/ID: {source_id}\n\nDocument content:\n{doc_content}"
    prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{human_message}")
        ])

    chain = prompt | structured_llm ## Understand this chaining and pipeline **
    result: DocumentStructure = chain.invoke({
        "human_message": human_message
    })

    for i, s in enumerate(result.sections):
        if not s.title: ## how we get the title? **
            lines = [l for l in s.start_marker.split("\n") if l.strip()]
            s.title = lines[1].strip() if len(lines) > 1 else (lines[0].strip() if lines else f"Section {i+1}")
        if not s.section_id:
            s.section_id = re.sub(r"[^\w\-_]", "-", s.title.lower()).strip("-")[:40] or f"section-{i+1}"

    if not result.document_title and result.sections:
        first_lines = result.sections[0].start_marker.split("\n")
        result.document_title = first_lines[0].strip() if first_lines else source_id

    print(f"📑 LLM identified {len(result.sections)} chapters in '{result.document_title}'.")
    return result.sections


def analyze_structure(state: IngestionState) -> Dict[str, Any]:
    """Phase 1: Identifies all sections in the document for targeted extraction.

    Strategy (in priority order):
    1. PDF TOC with adaptive depth + page ranges (deterministic, instant, no API cost)
    2. Regex-based heading detection (fast, no API cost)
    3. LLM with sampling for large docs (API call with reduced content)
    4. LLM full-pass for medium docs (API call with full content)
    5. Single-pass for short docs (< 12K chars)
    """
    content = state["raw_content"]
    source_id = state["source_id"]
    toc = state.get("toc")
    raw_path = state["raw_file_path"]

    if len(content) < SINGLE_PASS_THRESHOLD:
        print(f"📄 Document is short ({len(content)} chars); using single-pass extraction.")
        return {"sections": None}

    # Strategy 1: PDF TOC with page ranges (deterministic)
    if toc and raw_path.lower().endswith(".pdf"):
        try:
            import fitz
            doc = fitz.open(raw_path)
            total_pages = doc.page_count
            doc.close()
        except Exception:
            total_pages = 1000  # conservative fallback

        sections = _extract_sections_from_toc(toc, total_pages)
        if len(sections) >= 2:
            print(f"📑 PDF TOC (level-{sections[0].level if sections else '?'}): "
                  f"{len(sections)} chapters via page ranges.")
            for s in sections[:8]:
                print(f"  [{s.section_id}] pp.{s.page_start}-{s.page_end} {s.title}")
            if len(sections) > 8:
                print(f"  ... and {len(sections) - 8} more")
            return {"sections": sections}
        print("⚠️  PDF TOC had insufficient entries; trying regex...")

    # Strategy 2: Regex-based heading detection
    sections = _extract_sections_from_regex(content)
    if len(sections) >= 3:
        print(f"📑 Using regex headings: {len(sections)} chapters identified.")
        for s in sections:
            print(f"  [{s.section_id}] {s.title}")
        return {"sections": sections}
    print("⚠️  Regex detection found insufficient headings; falling back to LLM...")

    # Strategy 3/4: LLM (with sampling for large docs)
    sections = _extract_sections_from_llm(content, source_id)
    for s in sections:
        print(f"  [{s.section_id}] {s.title}")

    return {"sections": sections}


def extract_section_notes(state: IngestionState) -> Dict[str, Any]:  # processes wiki notes from the entire document
    """Phase 2: Extracts wiki notes from each section (or batch of small sections).
    Falls back to single-pass extraction if no sections available.
    Uses parallel batch processing for large documents."""
    sections = state.get("sections")
    content = state["raw_content"]
    source_id = state["source_id"]
    raw_file_path = state.get("raw_file_path", "")

    if sections is None:
        return _extract_single_pass(content, source_id)

    batches = _build_section_batches(sections, content, raw_file_path)

    if not batches:
        print("⚠️  No sections could be located; falling back to single-pass extraction.")
        return _extract_single_pass(content, source_id)

    print(f"🤖 Processing {len(sections)} sections in {len(batches)} batch(es) "
          f"[parallel workers={MAX_PARALLEL_BATCHES}]...")

    all_notes: List[ExtractedWikiNote] = []
    progress_data = _load_progress(source_id)
    completed_batches = set(progress_data.get("completed_batches", []))

    # Check for resume: skip already-completed batches
    pending_batches = [(idx, batch) for idx, batch in enumerate(batches)
                       if idx not in completed_batches]

    if len(completed_batches) > 0:
        print(f"🔄 Resuming: {len(completed_batches)} batches already done, {len(pending_batches)} remaining.")
        for idx in completed_batches:
            batch_notes = progress_data.get("batch_results", {}).get(str(idx), [])
            all_notes.extend([ExtractedWikiNote(**n) for n in batch_notes])

    if pending_batches:
        def _process_single_batch(idx: int, batch: List[tuple]) -> Tuple[int, List[Dict], Optional[str]]:
            batch_text = "\n\n".join(
                f"### Section: {s.title}\n{t}" for s, t in batch
            )
            try:
                notes = _extract_from_batch(batch_text, source_id) # sends back wiki notes extracted from the batch
                notes_dicts = [n.model_dump() for n in notes]
                return idx, notes_dicts, None
            except Exception as e:
                return idx, [], str(e)

        with ThreadPoolExecutor(max_workers=MAX_PARALLEL_BATCHES) as executor:
            futures = {
                executor.submit(_process_single_batch, idx, batch): idx
                for idx, batch in pending_batches
            }

            for future in as_completed(futures):
                idx = futures[future]
                try:
                    batch_idx, notes_dicts, error = future.result()
                except Exception as e:
                    print(f"  ⚠️  Batch {idx + 1} failed: {e}")
                    continue

                batch = batches[batch_idx]
                section_labels = ", ".join(s.title for s, _ in batch)

                if error:
                    print(f"  ⚠️  Batch {batch_idx + 1}/{len(batches)} [{section_labels}] failed: {error}")
                else:
                    notes = [ExtractedWikiNote(**nd) for nd in notes_dicts]
                    all_notes.extend(notes)
                    print(f"  Batch {batch_idx + 1}/{len(batches)} [{section_labels}]: {len(notes)} notes")

                # Save progress after each batch
                _save_progress(source_id, batch_idx, notes_dicts)

        # Clear progress file on success
        _clear_progress(source_id)

    decomposition = DocumentDecomposition(
        source_title=source_id,
        summary=f"Notes extracted from {len(sections)} sections across {len(batches)} batches.",
        notes=all_notes
    )

    print(f"✨ Total extracted: {len(all_notes)} wiki notes from {len(sections)} sections.")
    return {"decomposition": decomposition}


def _extract_single_pass(content: str, source_id: str) -> Dict[str, Any]:
    """Original single-pass extraction for short documents or fallback."""
    llm = _create_llm()
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
4. Be thorough: extract every distinct concept, entity, procedure, and synthesis insight. Do not merge unrelated ideas into one note.

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
        ("human", "{human_message}")
    ])

    human_message = f"Raw Document Title/ID: {source_id}\n\nContent:\n{content}"

    chain = prompt | structured_llm
    print("🤖 Processing raw document with LLM (single-pass)...")
    result: DocumentDecomposition = chain.invoke({
        "human_message": human_message
    })

    print(f"✨ Extracted {len(result.notes)} distinct wiki notes.")
    return {"decomposition": result}


def _build_section_batches(sections: List[DocumentSection], text: str,
                         raw_file_path: str = "") -> List[List[tuple]]:
    """Splits document into section text chunks using markers, or page ranges for PDFs.
    Page-range extraction is deterministic — no fragile text matching needed."""
    has_page_ranges = sections and sections[0].page_start > 0 and raw_file_path.lower().endswith(".pdf")

    if has_page_ranges:
        return _build_batches_from_pages(sections, raw_file_path)

    # Standard marker-based extraction (for non-PDF or fallback)
    section_chunks = []

    for section in sections:
        start_pos = _find_marker(text, section.start_marker) # returns start index of the start marker in text
        if start_pos < 0:
            print(f"  ⚠️  Could not locate start marker for '{section.title}', skipping.")
            continue

        search_start = start_pos + len(section.start_marker)

        if section.end_marker == "END_OF_DOC":
            end_pos = len(text)
        else:
            end_pos = _find_marker(text, section.end_marker, search_start)
            if end_pos < 0:
                end_pos = len(text)

        chunk = text[start_pos:end_pos].strip() # chunk is just the actual string chunk
        if len(chunk) > 80: # if chunk smaller than 80 characters then ignore it
            section_chunks.append((section, chunk)) # appending tuple of section and chunk

    return _pack_section_chunks_into_batches(section_chunks)


def _build_batches_from_pages(sections: List[DocumentSection], pdf_path: str) -> List[List[tuple]]:
    """Extract text by page ranges from the PDF (deterministic, no marker matching)."""
    import fitz
    doc = fitz.open(pdf_path)
    total = doc.page_count

    section_chunks: List[tuple] = []
    for section in sections:
        start = max(1, section.page_start) - 1  # convert 1-indexed to 0-indexed
        end = min(section.page_end - 1, total) if section.page_end > 0 else total

        if start >= total:
            print(f"  ⚠️  Section '{section.title}' page {section.page_start} beyond document end ({total} pages), skipping.")
            continue
        if end <= start:
            end = min(start + 1, total)

        text_parts = []
        for p in range(start, end):
            try:
                text_parts.append(doc[p].get_text())
            except Exception:
                pass

        chunk = "\n\n".join(text_parts).strip()
        if len(chunk) > 80:
            section_chunks.append((section, chunk))

    doc.close()
    return _pack_section_chunks_into_batches(section_chunks)


def _pack_section_chunks_into_batches(section_chunks: List[tuple]) -> List[List[tuple]]:
    """Group section chunks into batches not exceeding BATCH_TARGET characters."""
    batches = []
    current_batch = []
    current_chars = 0

    for section, chunk in section_chunks:
        chunk_len = len(chunk)

        if current_chars + chunk_len > BATCH_TARGET and current_batch: 
            # if current chars in batch + this chunk exceeds BATCH_TARGET chars then 'seal' the current batch and start a new one
            batches.append(current_batch)
            current_batch = []
            current_chars = 0

        current_batch.append((section, chunk))
        current_chars += chunk_len

    if current_batch:
        batches.append(current_batch)

    return batches


def _extract_from_batch(batch_text: str, source_id: str) -> List[ExtractedWikiNote]:
    """Extracts wiki notes from a single section batch using the LLM."""
    llm = _create_llm()
    structured_llm = llm.with_structured_output(SectionExtraction, method="json_mode") ## parses json output directly into an instance of SectionExtraction

    system_prompt = """You are an expert knowledge management assistant. You receive one or more complete chapters from a larger document. Extract comprehensive, self-contained wiki notes that cover the full concepts in the given chapters.

IMPORTANT: Output must be a JSON object with a "notes" array, like: {{"notes": [{{...}}, {{...}}]}}

Rules:
1. Extract comprehensive notes covering the KEY concepts in these chapters. Aim for 3-8 well-rounded notes per chapter — not one note per sub-topic.
2. COMBINE closely related sub-topics into a single rich note. For example:
   - Combine minor, merging, and major compaction into ONE "Compactions in Bigtable" note
   - Combine Scan Cache, Block Cache into ONE "Caching in Bigtable" note
   - Combine all API operations into ONE "Bigtable API" note with sub-detail
   - Do NOT create separate notes for each benchmark — combine them into a unified performance note
3. Each note must be self-contained but substantive. Content bodies should be 4-10 sentences with specific details, numbers, mechanisms, and examples from the text.
4. PRESERVE REFERENCE DATA: If the source contains tables, enumerated lists, country-specific regulations, numeric thresholds, location names, or specific requirements, you MUST include ALL the specific entries in the content_body. Do NOT collapse a list of 15 countries into 'varies by nationality' — list them. Do NOT replace exact numbers with 'certain thresholds' — state the numbers.
5. For each note provide:
   - title: clear, concise, not overly specific
   - type: 'concept', 'entity', 'procedure', or 'synthesis'
   - summary: brief 1-2 sentence description
   - keywords: 3-5 searchable tags
   - content_body: detailed markdown explanation with specific facts from the text, including all tables, thresholds, and enumerated data where present
6. Use [[wiki-link]] syntax for cross-references to related concepts.
7. Output pure JSON matching the schema exactly. Wrap all notes in a top-level "notes" array key."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{human_message}")
    ])

    human_message = f"Document ID: {source_id}\n\nSection(s) to process:\n{batch_text}"

    chain = prompt | structured_llm
    result: SectionExtraction = chain.invoke({
        "human_message": human_message
    })

    return result.notes if result and result.notes else []


def consolidate_notes(state: IngestionState) -> Dict[str, Any]:
    """Phase 3: Merges redundant/similar notes using title-similarity clustering and LLM consolidation.
    Uses parallel merge calls for efficiency with large note sets."""
    decomposition = state["decomposition"]
    notes = decomposition.notes
    if len(notes) < 5:
        return {}

    from difflib import SequenceMatcher

    def sim(a, b):
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    MERGE_THRESHOLD = 0.65

    clusters = []
    used = set()

    for i, note_a in enumerate(notes):
        if i in used:
            continue
        cluster = [i]
        used.add(i)
        for j, note_b in enumerate(notes):
            if j in used:
                continue
            if note_a.type == note_b.type and sim(note_a.title, note_b.title) > MERGE_THRESHOLD:
                # group two notes if they have the same type and the title match is > .65
                cluster.append(j)
                used.add(j)  # ensures a note is not assigned to multiple clusters
        clusters.append(cluster)

    mergeable = [(c, len(c)) for c in clusters if len(c) > 1] # get only clusters having 2 or more notes
    mergeable.sort(key=lambda x: -x[1]) # sort desc order of cluster len

    if not mergeable:
        print("ℹ️  No redundant notes found; skipping consolidation.")
        return {}

    total_mergeable = sum(c[1] for c in mergeable)
    print(f"🧹 Consolidating {len(mergeable)} cluster(s) of similar notes "
          f"({total_mergeable} notes total) [max {MAX_PARALLEL_MERGES} parallel]...")

    merged_notes: List[ExtractedWikiNote] = []
    merged_set = set()

    if len(mergeable) <= 2:
        # Sequential for small clusters
        for cluster, _ in mergeable:
            cluster_notes = [notes[i] for i in cluster]
            merged_set.update(cluster)
            merged = _merge_cluster(cluster_notes)
            if merged:
                merged_notes.append(merged)
                print(f"  ✓ Merged {len(cluster_notes)} notes → '{merged.title}'")
            else:
                merged_notes.extend(cluster_notes)
    else:
        # Parallel for many clusters
        cluster_data: List[Tuple[set, List[ExtractedWikiNote]]] = [
            (set(cluster), [notes[i] for i in cluster]) for cluster, _ in mergeable
        ]

        with ThreadPoolExecutor(max_workers=MAX_PARALLEL_MERGES) as executor:
            merge_futures = {
                executor.submit(_merge_cluster, cn): idx
                for idx, (cl_set, cn) in enumerate(cluster_data)
            }

            # Collect results in order of submission for deterministic output
            results_by_idx: Dict[int, Optional[ExtractedWikiNote]] = {}
            for future in as_completed(merge_futures):
                idx = merge_futures[future]
                try:
                    results_by_idx[idx] = future.result()
                except Exception as e:
                    print(f"  ⚠️  Merge {idx + 1} failed: {e}")
                    results_by_idx[idx] = None

            for idx, (cl_set, cn) in enumerate(cluster_data):
                merged = results_by_idx.get(idx)
                merged_set.update(cl_set)
                if merged:
                    merged_notes.append(merged)
                    print(f"  ✓ Merged {len(cn)} notes → '{merged.title}'")
                else:
                    merged_notes.extend(cn)

    kept_notes = [notes[i] for i in range(len(notes)) if i not in merged_set]
    all_notes = kept_notes + merged_notes

    decomposition.notes = all_notes
    print(f"✨ Consolidated: {len(notes)} → {len(all_notes)} notes ({len(notes) - len(all_notes)} removed).")
    return {"decomposition": decomposition}


def _merge_cluster(cluster_notes: List[ExtractedWikiNote]) -> Optional[ExtractedWikiNote]:
    """Asks the LLM to merge a cluster of similar notes into one comprehensive note."""
    if len(cluster_notes) < 2:
        return cluster_notes[0] if cluster_notes else None

    llm = _create_llm()
    structured_llm = llm.with_structured_output(MergedNote, method="json_mode")

    notes_text = "\n---\n".join(
        f"Title: {n.title}\nType: {n.type}\nKeywords: {', '.join(n.keywords)}\nContent: {n.content_body}"
        for n in cluster_notes
    )

    system_prompt = """You are merging similar wiki notes about the same topic into ONE comprehensive note.
The input notes were extracted from different sections of the same document. They overlap in content.
Your job: create a single merged note that preserves ALL unique information, removes redundancy, and is self-contained.

Rules:
1. Produce ONE merged note as a JSON object with fields: title, type, summary, keywords, content_body.
2. The content_body must be a comprehensive Markdown summary preserving all factual details, numbers, mechanisms, and examples from ALL input notes.
3. Choose the best title: use the clearest and most descriptive title from the inputs, or create a slightly broader one.
4. Choose the most appropriate type (concept/entity/procedure/synthesis).
5. Combine all keywords, deduplicate, keep the 4-6 most descriptive ones.
6. Do NOT invent new facts. Only use information present in the input notes.
7. Output pure JSON matching the schema exactly. Use the field name "content_body" (not "content")."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{human_message}")
    ])

    human_message = f"Merge these {len(cluster_notes)} similar notes into one:\n\n{notes_text}"

    chain = prompt | structured_llm
    try:
        result: MergedNote = chain.invoke({
            "human_message": human_message
        })
        return ExtractedWikiNote(
            title=result.title,
            type=result.type,
            summary=result.summary,
            keywords=result.keywords,
            content_body=result.content_body
        )
    except Exception as e:
        print(f"  ⚠️  Merge failed: {e}, keeping originals.")
        return None


def write_wiki_files(state: IngestionState) -> Dict[str, Any]:
    """Writes all extracted wiki notes to their target folders inside wiki/.
    Skips notes that already exist to avoid duplicates."""
    decomposition = state["decomposition"]
    source_id = state["source_id"]
    source_link = f"[[raw/sources/{source_id}]]"

    created_paths = []
    skipped_count = 0

    type_folder_map = {
        "concept": "concepts",
        "entity": "entities",
        "procedure": "procedures",
        "synthesis": "synthesis",
    }

    for note in decomposition.notes:
        slug = re.sub(r"[^\w\-_]", "-", note.title.lower()).strip("-") # A slug is a web- and filesystem-safe version of a human-readable title used for file naming.
        folder = type_folder_map.get(note.type, f"{note.type}s")
        target_path = WIKI_DIR / folder / f"{slug}.md"

        if target_path.exists(): # target_path is a Path object
            print(f"⏭  Skipped (already exists): {folder}/{slug}.md")
            skipped_count += 1
            continue

        file_path = LLMWikiIngester.create_wiki_note_file(
            note_type=note.type,
            title=note.title,
            summary=note.summary,
            sources=[source_link],
            keywords=note.keywords,
            content_body=note.content_body
        )
        created_paths.append(str(file_path))

    print(f"✓ Created {len(created_paths)} new notes, skipped {skipped_count} existing.")
    return {"generated_files": created_paths}


def sync_wiki_catalog(state: IngestionState) -> Dict[str, Any]:
    """Updates catalog.json and rebuilds index.md using CatalogManager."""
    print("🔄 Synchronizing wiki catalog and index...")
    manager = CatalogManager()
    manager.sync_all()
    return {}


# =====================================================================
# 5. PROGRESS TRACKING (Resume support)
# =====================================================================

def _progress_path(source_id: str) -> Path:
    PROGRESS_DIR.mkdir(parents=True, exist_ok=True)
    return PROGRESS_DIR / f"{source_id}.json"


def _load_progress(source_id: str) -> Dict[str, Any]:
    path = _progress_path(source_id)
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    return {"completed_batches": [], "batch_results": {}}


def _save_progress(source_id: str, batch_idx: int, notes_dicts: List[Dict]):
    progress = _load_progress(source_id)
    completed = set(progress.get("completed_batches", []))
    completed.add(batch_idx)
    progress["completed_batches"] = sorted(completed)
    progress["batch_results"] = progress.get("batch_results", {})
    progress["batch_results"][str(batch_idx)] = notes_dicts
    progress["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
    _progress_path(source_id).write_text(json.dumps(progress, indent=2), encoding="utf-8")


def _clear_progress(source_id: str):
    path = _progress_path(source_id)
    if path.exists():
        path.unlink()


# =====================================================================
# 6. WORKFLOW GRAPH BUILDER
# =====================================================================

def build_ingestion_graph():
    workflow = StateGraph(IngestionState)

    workflow.add_node("read_doc", read_raw_document)
    workflow.add_node("analyze_structure", analyze_structure)
    workflow.add_node("extract_notes", extract_section_notes)
    workflow.add_node("consolidate", consolidate_notes)
    workflow.add_node("write_files", write_wiki_files)
    workflow.add_node("sync_catalog", sync_wiki_catalog)

    workflow.add_edge(START, "read_doc")
    workflow.add_edge("read_doc", "analyze_structure")
    workflow.add_edge("analyze_structure", "extract_notes")
    workflow.add_edge("extract_notes", "consolidate")
    workflow.add_edge("consolidate", "write_files")
    workflow.add_edge("write_files", "sync_catalog")
    workflow.add_edge("sync_catalog", END)

    return workflow.compile()


# =====================================================================
# 7. EXECUTION ENTRY POINT
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
        "sections": None,
        "decomposition": None,
        "generated_files": [],
        "toc": None,
    }

    try:
        app.invoke(initial_state)
        print("\n🎉 Ingestion complete!")
    except Exception as e:
        print(f"\n❌ Ingestion failed: {e}")
        import traceback
        traceback.print_exc()
