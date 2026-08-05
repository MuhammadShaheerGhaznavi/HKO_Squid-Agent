import json
import math
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

import tiktoken # Tiktoken is a fast, byte pair encoding (BPE) tokenizer - helps estimate token costs etc

from config import (
    WIKI_DIR, RAW_DIR, CATALOG_FILE, TOP_K_SEARCH,
    MAX_TOKENS_PER_PAGE, MAX_CHUNK_TOKENS, CHUNK_OVERLAP_TOKENS,
)

_tokenizer = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    return len(_tokenizer.encode(text))


def _token_trim(text: str, max_tokens: int) -> str:
    tokens = _tokenizer.encode(text)
    if len(tokens) <= max_tokens:
        return text
    return _tokenizer.decode(tokens[:max_tokens]) # truncating with tokens


@dataclass # what this
class CatalogEntry: # keep track of catalog entries
    path: str
    title: str
    type: str
    summary: str
    keywords: List[str]
    sources: List[str]
    wiki_links: List[str]
    last_updated: str

    @property # what this
    def searchable_text(self) -> str:
        return f"{self.title} {self.summary} {' '.join(self.keywords)}"


@dataclass
class SearchResult:
    entry: CatalogEntry
    score: float # relevance score
    snippet: Optional[str] = None
    content: Optional[str] = None


class WikiRetriever:
    def __init__(self, wiki_dir: Path = WIKI_DIR, catalog_path: Path = CATALOG_FILE):
        self.wiki_dir = Path(wiki_dir)
        self.catalog_path = Path(catalog_path)
        self._catalog: Dict[str, CatalogEntry] = {} # ig this grabs the entire catalog
        self._entries_list: List[CatalogEntry] = [] # this is all the entries??
        self._load_catalog()

    def _load_catalog(self):
        if not self.catalog_path.exists():
            self._catalog = {}
            self._entries_list = []
            return
        try:
            with open(self.catalog_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            self._catalog = {}
            self._entries_list = []
            return

        entries = data.get("entries", {})
        for path_str, e in entries.items():
            ce = CatalogEntry(
                path=e.get("path", path_str),
                title=e.get("title", ""),
                type=e.get("type", "concept"),
                summary=e.get("summary", ""),
                keywords=e.get("keywords", []),
                sources=e.get("sources", []),
                wiki_links=e.get("wiki_links", []),
                last_updated=e.get("last_updated", ""),
            )
            self._catalog[ce.path] = ce
        self._entries_list = list(self._catalog.values())

    def reload(self):
        self._load_catalog()

    def get_entry(self, path: str) -> Optional[CatalogEntry]:
        return self._catalog.get(path)

    def _tokenize(self, text: str) -> List[str]: # just splits the text??
        return text.lower().split()

    def _bm25_score_batch(
        self, query: str, documents: List[str], k1: float = 1.5, b: float = 0.75
    ) -> List[float]:
        if not documents:
            return []
            
        query_terms = self._tokenize(query)
        if not query_terms:
            return [0.0] * len(documents) 

        doc_tokens = [self._tokenize(d) for d in documents] # documents is wiki note title or the content
            # doc_tokens is a nested list of lists, where each list corresponds to that particular document
        N = len(documents)
        total_tokens = sum(len(t) for t in doc_tokens)
        avgdl = total_tokens / N if N else 0 # Abergae doc length
        unique_query_terms = set(query_terms)

        idf_cache: Dict[str, float] = {}
        for term in unique_query_terms:
            # Count how many documents contain this term
            df = sum(1 for dt in doc_tokens if term in dt)# how many times this word appeared in the docs
            # Standard BM25 IDF formula
            idf = math.log(1.0 + (N - df + 0.5) / (df + 0.5)) # how rare the word is in the whole datasset... common words like the have idf~0
            idf_cache[term] = idf
        
        scores = []
        for dt in doc_tokens:
            score = 0.0
            doc_len = len(dt)

            if doc_len > 0 and avgdl > 0:
                # Pre-calculate the denominator length normalization factor for this document
                len_norm = k1 * (1.0 - b + b * (doc_len / avgdl))
                
                for term in unique_query_terms:
                    tf = dt.count(term) # term frequency in doc
                    if tf > 0:
                        idf = idf_cache[term]
                        numerator = tf * (k1 + 1.0)
                        denominator = tf + len_norm
                        score += idf * (numerator / denominator)
            scores.append(score)
        return scores

    def search_catalog(self, query: str, top_k: int = TOP_K_SEARCH) -> List[SearchResult]:
        if not self._entries_list:
            return []
        texts = [e.searchable_text for e in self._entries_list]
        scores = self._bm25_score_batch(query, texts)
        scored = sorted(
            zip(self._entries_list, scores),
            key=lambda x: x[1],
            reverse=True,
        )
        return [
            SearchResult(entry=entry, score=round(score, 4))
            for entry, score in scored[:top_k]
            if score > 0
        ]
### understand below this
    def search_content(self, query: str, top_k: int = TOP_K_SEARCH) -> List[SearchResult]:
        try:
            result = subprocess.run(
                ["rg", "-i", "-l", query, str(self.wiki_dir)],
                capture_output=True, text=True, check=False, timeout=10,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

        matched_paths = [p.strip() for p in result.stdout.strip().split("\n") if p.strip()]
        results: List[SearchResult] = []

        for mp in matched_paths[:top_k * 2]:
            rel = str(Path(mp).relative_to(self.wiki_dir))
            entry = self._catalog.get(rel)
            if entry:
                results.append(SearchResult(entry=entry, score=0.0, snippet=None))

        if not results:
            return []

        texts = [r.entry.searchable_text for r in results]
        scores = self._bm25_score_batch(query, texts)
        for r, s in zip(results, scores):
            r.score = round(s, 4)

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    def hybrid_search(self, query: str, top_k: int = TOP_K_SEARCH) -> List[SearchResult]:
        catalog_results = self.search_catalog(query, top_k=top_k)
        content_results = self.search_content(query, top_k=top_k)

        seen = set()
        merged: List[SearchResult] = []
        for r in catalog_results:
            if r.entry.path not in seen:
                seen.add(r.entry.path)
                merged.append(r)

        for r in content_results:
            if r.entry.path not in seen:
                seen.add(r.entry.path)
                merged.append(r)

        merged.sort(key=lambda x: x.score, reverse=True)
        return merged[:top_k]

    def read_page(self, path: str, max_tokens: int = MAX_TOKENS_PER_PAGE) -> str:
        target = self.wiki_dir / path
        if not target.exists() and not path.endswith(".md"):
            target = self.wiki_dir / f"{path}.md"
        if not target.exists():
            return f"[Page not found: {path}]"

        try:
            content = target.read_text(encoding="utf-8")
        except Exception as e:
            return f"[Error reading {path}: {e}]"

        token_count = count_tokens(content)
        if token_count <= max_tokens:
            return content

        return self._chunk_and_score(content, path, max_tokens)

    def _chunk_and_score(self, content: str, path: str, max_tokens: int) -> str:
        tokens = _tokenizer.encode(content)
        chunks: List[str] = []
        i = 0
        while i < len(tokens):
            chunk = tokens[i: i + MAX_CHUNK_TOKENS]
            chunks.append(_tokenizer.decode(chunk))
            i += MAX_CHUNK_TOKENS - CHUNK_OVERLAP_TOKENS

        if len(chunks) == 1:
            return _token_trim(content, max_tokens)

        header = f"[Large page: {path} — {len(chunks)} sections, showing first {min(3, len(chunks))} most relevant sections]\n\n"
        sections = chunks[:3]
        combined = "\n\n---\n\n".join(sections)
        result = header + _token_trim(combined, max_tokens)

        page_tokens = count_tokens(result)
        if page_tokens > max_tokens:
            result = _token_trim(result, max_tokens)
            result += "\n\n[Truncated — page exceeds token limit. Use read_page(path, max_tokens=N) to read more.]"

        return result

    def get_related_pages(self, path: str) -> List[str]:
        entry = self._catalog.get(path)
        if not entry and not path.endswith(".md"):
            entry = self._catalog.get(f"{path}.md")

        if not entry:
            return []

        linked: List[str] = []
        if entry.wiki_links:
            for link in entry.wiki_links:
                if link.startswith("raw/"):
                    continue
                linked.append(link)

        backlinks = self._get_backlinks(path if "." in path else path + ".md")
        for bl in backlinks:
            if bl not in linked:
                linked.append(bl)

        return linked[:8]

    def _get_backlinks(self, filename: str) -> List[str]:
        import re
        clean = filename.replace(".md", "").strip()
        pattern = re.compile(rf"\[\[{re.escape(clean)}\]\]", re.IGNORECASE)
        backlinks = []
        for f in self.wiki_dir.rglob("*.md"):
            if f.name == filename:
                continue
            try:
                text = f.read_text(encoding="utf-8")
                if pattern.search(text):
                    backlinks.append(str(f.relative_to(self.wiki_dir)))
            except Exception:
                continue
        return backlinks

    def read_raw_source(self, filename: str, max_tokens: int = 3000) -> str:
        target = RAW_DIR / filename.lstrip("/")
        if not target.exists():
            return f"[Raw source not found: {filename}]"
        try:
            content = target.read_text(encoding="utf-8")
        except Exception as e:
            return f"[Error reading raw source {filename}: {e}]"
        return _token_trim(content, max_tokens)

    def format_search_results(self, results: List[SearchResult]) -> str:
        if not results:
            return "No matching pages found in the wiki."

        lines = ["## Wiki Search Results\n"]
        for i, r in enumerate(results, 1):
            entry = r.entry
            lines.append(
                f"{i}. **{entry.title}** `[{entry.type}]` _(score: {r.score:.3f})_\n"
                f"   Path: `{entry.path}`\n"
                f"   Summary: {entry.summary}\n"
                f"   Keywords: {', '.join(entry.keywords)}\n"
            )
        return "\n".join(lines)

    def search_and_format(self, query: str, top_k: int = TOP_K_SEARCH) -> str:
        results = self.hybrid_search(query, top_k)
        return self.format_search_results(results)
