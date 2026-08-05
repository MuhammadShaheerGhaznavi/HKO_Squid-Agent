import os
import re
import json
import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

try:
    import yaml
except ImportError:
    yaml = None

# Root paths relative to workspace
WORKSPACE_ROOT = Path(__file__).parent.parent.resolve()
WIKI_DIR = WORKSPACE_ROOT / "wiki"
RAW_SOURCES_DIR = WORKSPACE_ROOT / "raw" / "sources"
CATALOG_FILE = WIKI_DIR / "catalog.json"
INDEX_FILE = WIKI_DIR / "index.md"


class WikiNoteParser:
    """Parses markdown files containing '### Properties' blocks or YAML frontmatter."""

    @staticmethod
    def parse(file_path: Path) -> Tuple[Dict[str, Any], str, List[str]]:
        """
        Parses a Markdown note.

        Returns:
            (metadata_dict, body_content, extracted_wiki_links)
        """
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return {}, "", []

        metadata: Dict[str, Any] = {}
        body: str = content.strip()

        # 1. Try parsing explicit '### Properties' section
        props_pattern = r"###\s+Properties\s*\n(?P<props_raw>.*?)(?=\n##|\Z)"
        match = re.search(props_pattern, content, re.DOTALL)

        if match:
            raw_props = match.group("props_raw").strip() # returns the matched string
            metadata = WikiNoteParser._parse_yaml_str(raw_props)
            # Body is everything after the Properties block
            body = content[match.end("props_raw"):].strip() # macth.end() returns index of the first character after the 
                        # matched string ends
        else:
            # 2. Fallback to YAML Frontmatter (---)
            fm_pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
            fm_match = re.search(fm_pattern, content, re.DOTALL)
            if fm_match:
                raw_props, body = fm_match.group(1), fm_match.group(2)
                metadata = WikiNoteParser._parse_yaml_str(raw_props)

        # Extract all [[wiki-links]] present in the file
        wiki_links = list(set(re.findall(r"\[\[(.*?)\]\]", content)))

        return metadata, body, wiki_links

    @staticmethod
    def _parse_yaml_str(raw_str: str) -> Dict[str, Any]:
        if yaml:
            try:
                data = yaml.safe_load(raw_str)
                return data if isinstance(data, dict) else {}
            except Exception:
                pass
        return WikiNoteParser._fallback_parse_kv(raw_str)

    @staticmethod
    def _fallback_parse_kv(raw_str: str) -> Dict[str, Any]:
        data = {}
        for line in raw_str.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                key, val = line.split(":", 1)
                key = key.strip()
                if " #" in val:
                    val = val.split(" #")[0]
                val = val.strip().strip('"').strip("'")
                
                # Parse array notation like ["a", "b"]
                if val.startswith("[") and val.endswith("]"):
                    items = [i.strip().strip('"').strip("'") for i in val[1:-1].split(",") if i.strip()]
                    data[key] = items
                elif val.isdigit():
                    data[key] = int(val)
                else:
                    data[key] = val
        return data


class CatalogManager:
    """Manages wiki/catalog.json and wiki/index.md."""

    def __init__(self, wiki_dir: Path = WIKI_DIR):
        self.wiki_dir = wiki_dir
        self.catalog_path = CATALOG_FILE
        self.index_path = INDEX_FILE

    def load_catalog(self) -> Dict[str, Any]: # loads/initializes catalog.json
        if self.catalog_path.exists() and self.catalog_path.stat().st_size > 0:
            try:
                with open(self.catalog_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load {self.catalog_path}: {e}")
        return {"last_updated": "", "entries": {}}

    def sync_all(self) -> Dict[str, Any]:
        """Scans the **entire wiki/ directory** and updates catalog.json and index.md idempotently."""
        catalog = self.load_catalog()
        entries = {}

        # Subdirectories corresponding to note types
        valid_dirs = ["concepts", "entities", "procedures", "synthesis"]
        
        for category in valid_dirs:
            cat_dir = self.wiki_dir / category
            if not cat_dir.exists():
                cat_dir.mkdir(parents=True, exist_ok=True)
                continue

            for md_file in cat_dir.glob("*.md"):
                rel_path = md_file.relative_to(self.wiki_dir).as_posix()
                metadata, body, links = WikiNoteParser.parse(md_file)

                # Standardize sources to list
                sources = metadata.get("sources", [])
                if isinstance(sources, str):
                    sources = [sources]

                keywords = metadata.get("keywords", [])
                if isinstance(keywords, str):
                    keywords = [k.strip() for k in keywords.split(",")]

                last_updated_val = metadata.get("last_updated", datetime.date.today().isoformat())
                if isinstance(last_updated_val, (datetime.date, datetime.datetime)):
                    last_updated_val = last_updated_val.isoformat()

                entries[rel_path] = { ## this is treating each md file as a separate key
                    "title": metadata.get("title", md_file.stem.replace("-", " ").title()),
                    "type": metadata.get("type", category[:-1] if category.endswith("s") else category),
                    "summary": metadata.get("summary", "No summary provided."),
                    "sources": sources,
                    "source_count": len(sources),
                    "keywords": keywords,
                    "wiki_links": links,
                    "last_updated": str(last_updated_val),
                    "path": rel_path
                }

        catalog["last_updated"] = datetime.datetime.now().isoformat()
        catalog["entries"] = entries

        # Precompute backlinks: for each entry, list other entries that wikilink to it
        entry_paths = {p: e.get("title", "") for p, e in entries.items()}
        backlinks_map: Dict[str, List[str]] = {p: [] for p in entries}
        for source_path, source_entry in entries.items():
            source_title = source_entry.get("title", "")
            for target_path, target_title in entry_paths.items():
                if target_path == source_path:
                    continue
                if target_title and (target_title in str(source_entry.get("wiki_links", []))
                                     or f"[[{target_title}]]" in str(source_entry.get("wiki_links", []))):
                    backlinks_map[target_path].append(source_path)
        for p, bl in backlinks_map.items():
            entries[p]["backlinks"] = bl

        # Save catalog.json
        with open(self.catalog_path, "w", encoding="utf-8") as f:
            json.dump(catalog, f, indent=2, ensure_ascii=False)
        print(f"✓ Catalog updated: {len(entries)} entries -> {self.catalog_path}")

        # Regenerate index.md
        self._rebuild_index_md(entries)
        return catalog

    def _rebuild_index_md(self, entries: Dict[str, Any]):
        """Rebuilds wiki/index.md cleanly grouped by category."""
        lines = [
            "# Wiki Knowledge Index",
            f"*Last Index Sync: {datetime.date.today().isoformat()}*",
            "\n"
        ]

        categories = ["concepts", "entities", "procedures", "synthesis"]
        
        for cat in categories:
            cat_entries = [e for e in entries.values() if e["path"].startswith(f"{cat}/")]
            lines.append(f"## {cat.title()}\n")
            
            if not cat_entries:
                lines.append("_No entries yet._\n")
                continue

            lines.append("| Title | Summary | Keywords | Last Updated |")
            lines.append("| :--- | :--- | :--- | :--- |")

            for item in sorted(cat_entries, key=lambda x: x["title"]):
                link_target = item["path"][:-3] if item["path"].endswith(".md") else item["path"]
                title_link = f"[[{link_target}\\|{item['title']}]]"
                kw_str = ", ".join([f"`{k}`" for k in item.get("keywords", [])])
                lines.append(f"| {title_link} | {item['summary']} | {kw_str} | {item['last_updated']} |")
            
            lines.append("\n")

        with open(self.index_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"✓ Index regenerated -> {self.index_path}")


class LLMWikiIngester:
    """Handles parsing raw documents and structuring generated wiki notes."""

    @staticmethod
    def create_wiki_note_file(
        note_type: str,
        title: str,
        summary: str,
        sources: List[str],
        content_body: str,
        keywords: Optional[List[str]] = None
    ) -> Path:
        """Helper to output formatted markdown note file with metadata properties block."""
        slug = re.sub(r"[^\w\-_]", "-", title.lower()).strip("-")
        if note_type == "entity":
            folder_name = "entities"
        elif note_type == "concept":
            folder_name = "concepts"
        elif note_type == "procedure":
            folder_name = "procedures"
        elif note_type == "synthesis":
            folder_name = "synthesis"
        else:
            folder_name = f"{note_type}s"


        target_dir = WIKI_DIR / folder_name
        target_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = target_dir / f"{slug}.md"
        sources_str = json.dumps(sources) if sources else "[]"
        keywords_str = json.dumps(keywords) if keywords else '[]'
        today = datetime.date.today().isoformat()

        formatted_content = f"""## Wiki-note

### Properties
title: "{title}"
type: {note_type}
summary: "{summary}"
sources: {sources_str}
source_count: {len(sources)}
keywords: {keywords_str}
last_updated: {today}

## Content
{content_body}
"""
        file_path.write_text(formatted_content, encoding="utf-8")
        print(f"✓ Created Wiki Note: {file_path.relative_to(WORKSPACE_ROOT)}")
        return file_path


if __name__ == "__main__":
    import sys

    manager = CatalogManager()

    if len(sys.argv) > 1 and sys.argv[1] == "sync":
        manager.sync_all()
    else:
        # Default behavior: run full index sync
        print("Running Wiki Catalog Synchronization...")
        manager.sync_all()