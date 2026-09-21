import json
import math
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

import tiktoken # Tiktoken is a fast, byte pair encoding (BPE) tokenizer - helps estimate token costs etc

from config import (
    WIKI_DIR, RAW_DIR, RAW_SOURCES_DIR, CATALOG_FILE, TOP_K_SEARCH,
    MAX_TOKENS_PER_PAGE, MAX_CHUNK_TOKENS, CHUNK_OVERLAP_TOKENS,
    RAW_CACHE_DIR, R2_RAW_PREFIX,
    R2_ENDPOINT_URL, R2_BUCKET, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY,
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
    backlinks: List[str] = field(default_factory=list)  # precomputed in catalog.json
    sections: List[str] = field(default_factory=list)  # AIP section refs (e.g., GEN 3.1)

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
                backlinks=e.get("backlinks", []),
                sections=e.get("sections", []),
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

        # Use precomputed backlinks from catalog (fast O(1) lookup)
        if entry.backlinks:
            for bl in entry.backlinks:
                if bl not in linked:
                    linked.append(bl)
        else:
            # Fallback: scan files (slow, for catalogs built before backlink support)
            backlinks = self._get_backlinks(path if "." in path else path + ".md")
            for bl in backlinks:
                if bl not in linked:
                    linked.append(bl)

        return linked[:8]

    def _get_backlinks(self, filename: str) -> List[str]:
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

    @staticmethod
    def _normalize_raw_filename(filename: str) -> str:
        """Strip wiki-link brackets and raw/ path prefixes to a bare source name."""
        name = filename.strip()
        name = name.lstrip("[").rstrip("]").strip()
        # Handle [[raw/sources/foo]] leftover brackets
        while name.startswith("[") or name.endswith("]"):
            name = name.strip("[]").strip()
        for prefix in ("raw/sources/", "raw/", "sources/"):
            if name.lower().startswith(prefix):
                name = name[len(prefix):]
                break
        return name.lstrip("/")

    def _r2_configured(self) -> bool:
        return bool(R2_ENDPOINT_URL and R2_BUCKET and R2_ACCESS_KEY_ID and R2_SECRET_ACCESS_KEY)

    def _get_s3_client(self):
        """Lazy-init a reusable boto3 S3 client for R2."""
        if not self._r2_configured():
            return None
        if getattr(self, "_s3_client", None) is None:
            import boto3
            self._s3_client = boto3.client(
                "s3",
                endpoint_url=R2_ENDPOINT_URL,
                aws_access_key_id=R2_ACCESS_KEY_ID,
                aws_secret_access_key=R2_SECRET_ACCESS_KEY,
                region_name="auto",
            )
        return self._s3_client

    def _fetch_from_cloud(self, filename: str) -> Optional[Path]:
        """Download a raw source file from R2 object storage into a local cache."""
        s3 = self._get_s3_client()
        if s3 is None:
            return None

        key_name = self._normalize_raw_filename(filename)
        if not key_name:
            return None

        local_path = RAW_CACHE_DIR / key_name
        if local_path.exists() and local_path.stat().st_size > 0:
            return local_path

        object_keys = []
        for object_key in (key_name, f"{R2_RAW_PREFIX}{key_name}"):
            if object_key not in object_keys:
                object_keys.append(object_key)

        # Use string concat so multi-suffix names like *.toc.json stay intact
        tmp_path = Path(str(local_path) + ".partial")
        errors = []
        try:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            for object_key in object_keys:
                try:
                    s3.download_file(R2_BUCKET, object_key, str(tmp_path))
                    tmp_path.replace(local_path)
                    self._last_r2_error = ""
                    return local_path
                except Exception as e:
                    code = ""
                    response = getattr(e, "response", None)
                    if isinstance(response, dict):
                        code = response.get("Error", {}).get("Code", "")
                    errors.append(f"{object_key} ({code or type(e).__name__})")
                    try:
                        if tmp_path.exists():
                            tmp_path.unlink()
                    except OSError:
                        pass
                    # Auth/config errors will fail every key; missing keys should try the next path.
                    if code not in ("404", "NoSuchKey", "NotFound", ""):
                        break
        except Exception as e:
            errors.append(type(e).__name__)

        self._last_r2_error = "; ".join(errors) if errors else "unknown error"
        print(f"[R2 fetch failed for {key_name}: {self._last_r2_error}]")
        return None

    def _resolve_raw_path(self, filename: str) -> Optional[Path]:
        """Resolve a raw source filename to a local path: local disk first, then R2 cloud."""
        name = self._normalize_raw_filename(filename)
        candidates = [name]
        # Auto-detect extension when agent passes bare stem (e.g. AIP_17july2026)
        if "." not in Path(name).name:
            candidates = [name + ext for ext in (".pdf", ".md", ".txt")]

        # 1. Local disk (dev machine / git-tracked sources)
        for base_dir in (RAW_SOURCES_DIR, RAW_DIR):
            for cand in candidates:
                p = base_dir / cand
                if p.exists():
                    return p

        # 2. Already in cache from a prior R2 fetch
        for cand in candidates:
            cached = RAW_CACHE_DIR / cand
            if cached.exists() and cached.stat().st_size > 0:
                return cached

        # 3. R2 cloud (downloads to cache)
        for cand in candidates:
            p = self._fetch_from_cloud(cand)
            if p:
                return p

        return None

    def _resolve_toc_path(self, pdf_path: Path, filename: str) -> Optional[Path]:
        """Find the .toc.json sidecar beside the PDF, in local sources, or via R2."""
        toc_name = Path(self._normalize_raw_filename(filename)).stem + ".toc.json"
        # Path.with_suffix(".toc.json") on foo.pdf → foo.toc.json
        candidates = [
            pdf_path.with_name(toc_name),
            RAW_SOURCES_DIR / toc_name,
            RAW_DIR / toc_name,
            RAW_CACHE_DIR / toc_name,
        ]
        for cand in candidates:
            if cand.exists():
                return cand
        return self._fetch_from_cloud(toc_name)

    def read_raw_source(self, filename: str, max_tokens: int = 3000, search: str = "") -> str:
        target = self._resolve_raw_path(filename)
        if target is None:
            if not self._r2_configured():
                return (
                    f"[Raw source not found: {filename}. "
                    "R2 credentials are not configured on this server.]"
                )
            detail = getattr(self, "_last_r2_error", "") or "object was not in the bucket"
            return f"[Raw source not found: {filename}. Cloud fetch failed: {detail}]"

        suffix = target.suffix.lower()

        # If search term provided + PDF with TOC sidecar → direct page jump
        if search and suffix == ".pdf":
            toc_path = self._resolve_toc_path(target, filename)
            if toc_path and toc_path.exists():
                try:
                    toc = json.loads(toc_path.read_text(encoding="utf-8"))
                    # Find best TOC entry matching search term (fuzzy normalization)
                    search_lower = re.sub(r"[^a-z0-9]", "", search.lower())
                    best_entry = None
                    best_score = -1
                    for entry in toc.get("entries", []):
                        entry_stripped = re.sub(r"[^a-z0-9]", "", entry["title"].lower())
                        # Exact match always wins
                        if search_lower == entry_stripped:
                            best_entry = entry
                            break
                        # Prefer entries where search is a substring (more specific match)
                        if search_lower in entry_stripped:
                            score = len(search_lower) / len(entry_stripped)  # higher = more specific
                            if score > best_score:
                                best_score = score
                                best_entry = entry
                    if best_entry:
                        page_num = best_entry["page"]  # 1-indexed
                        import fitz
                        doc = fitz.open(str(target))
                        start = max(0, page_num - 3)  # 3 pages before
                        end = min(page_num + 4, doc.page_count)  # 4 pages after (~7-page window)
                        content_parts = []
                        for p in range(start, end):
                            content_parts.append(doc[p].get_text())
                        doc.close()
                        content = "\n\n".join(content_parts)
                        result = f"[Jumped to page {page_num} — matched '{best_entry['title']}']\n\n{content}"
                        return _token_trim(result, max_tokens)
                    # Search term not found in TOC
                    return (f"[Search term '{search}' not found in TOC index of {filename}. "
                            f"Try without search, or use a different term.]")
                except Exception as e:
                    print(f"[TOC jump failed: {e}]")
                    pass  # TOC read failed — fall through to default behavior

        if suffix == ".pdf":
            try:
                import fitz
                doc = fitz.open(str(target))
                content_parts = []
                tok_count = 0
                for page in doc:
                    text = page.get_text()
                    pt = count_tokens(text)
                    if tok_count + pt > max_tokens:
                        remaining = max_tokens - tok_count
                        if remaining > 0:
                            content_parts.append(_token_trim(text, remaining))
                        content_parts.append("\n\n[... PDF truncated — document is large ...]")
                        break
                    content_parts.append(text)
                    tok_count += pt
                doc.close()
                content = "\n\n".join(content_parts)
                return _token_trim(content, max_tokens)
            except Exception as e:
                return f"[Error reading raw PDF {filename}: {e}]"

        try:
            content = target.read_text(encoding="utf-8")
        except Exception as e:
            return f"[Error reading raw source {filename}: {e}]"
        return _token_trim(content, max_tokens)

    def resolve_page_path(self, title_or_link: str) -> Optional[str]:
        """Resolve a wiki-link title to an actual file path via fuzzy matching against catalog entries."""
        clean = title_or_link.strip().rstrip(".md")
        # Handle pipe syntax: [[Page Name|Display Text]]
        if "|" in clean:
            clean = clean.split("|")[0].strip()
        # Handle wikilink brackets
        clean = clean.lstrip("[[").rstrip("]]").strip()

        if not clean:
            return None

        # Exact title match
        clean_lower = clean.lower()
        for entry in self._entries_list:
            if entry.title.lower() == clean_lower:
                return entry.path

        # Exact path match (if already a valid path)
        if clean in self._catalog or f"{clean}.md" in self._catalog:
            return clean if clean in self._catalog else f"{clean}.md"

        # Check if query is a substring of any title
        for entry in self._entries_list:
            if clean_lower in entry.title.lower():
                return entry.path

        # Check if ALL query words appear in a title (order-independent)
        query_terms = clean_lower.split()
        if len(query_terms) > 1:
            for entry in self._entries_list:
                title_lower = entry.title.lower()
                if all(term in title_lower for term in query_terms):
                    return entry.path

        # Fuzzy: word-overlap score against titles
        query_words = set(clean_lower.split())
        if not query_words:
            return None

        best_score = 0.0
        best_path = None
        for entry in self._entries_list:
            title_words = set(entry.title.lower().split())
            overlap = len(query_words & title_words)
            score = overlap / len(query_words)
            if score > best_score and score >= 0.35:
                best_score = score
                best_path = entry.path

        return best_path

    def read_page_resolved(self, path_or_title: str, max_tokens: int = MAX_TOKENS_PER_PAGE) -> str:
        """Read a wiki page by path OR title. Auto-resolves titles to file paths."""
        content = self.read_page(path_or_title, max_tokens)
        if not content.startswith("[Page not found:"):
            return content

        resolved = self.resolve_page_path(path_or_title)
        if resolved:
            return f"[Resolved '{path_or_title}' → '{resolved}']\n\n" + self.read_page(resolved, max_tokens)

        # Show suggestions
        suggestions = []
        query_words = set(path_or_title.lower().split())
        if query_words:
            scored = []
            for entry in self._entries_list:
                title_words = set(entry.title.lower().split())
                overlap = len(query_words & title_words)
                if overlap > 0:
                    scored.append((overlap / len(query_words), entry))

            scored.sort(key=lambda x: -x[0])
            for _, entry in scored[:5]:
                suggestions.append(f"  - {entry.title} (`{entry.path}`)")

        suggestion_text = "\n".join(suggestions) if suggestions else "No similar pages found."
        return f"[Page not found: {path_or_title}]\nDid you mean:\n{suggestion_text}"

    def format_search_results(self, results: List[SearchResult]) -> str:
        if not results:
            return "No matching pages found in the wiki."

        lines = ["## Wiki Search Results\n"]
        for i, r in enumerate(results, 1):
            entry = r.entry
            section_tag = f" § {', '.join(entry.sections)}" if entry.sections else ""
            lines.append(
                f"{i}. **{entry.title}** `[{entry.type}]{section_tag}` _(score: {r.score:.3f})_\n"
                f"   Path: `{entry.path}`\n"
                f"   Summary: {entry.summary}\n"
                f"   Keywords: {', '.join(entry.keywords)}\n"
            )
        return "\n".join(lines)

    def search_and_format(self, query: str, top_k: int = TOP_K_SEARCH) -> str:
        results = self.hybrid_search(query, top_k)
        return self.format_search_results(results)
