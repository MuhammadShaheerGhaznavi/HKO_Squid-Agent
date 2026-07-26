import re
from pathlib import Path
from typing import Any, Dict, Tuple
import subprocess
import json

try:
    import yaml
except ImportError:
    yaml = None


def parse_markdown_file(file_path: Path) -> Tuple[Dict[str, Any], str, str]:
    """Parses markdown files (Source-note or Wiki-note templates).

    Extracts property metadata under '### Properties' and returning the note body.

    Returns:
        (metadata_dict, body_content, raw_properties_string)
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return {}, "", ""

    # Match ## <note-type>, followed by ### Properties, up to the next heading or EOF
    pattern = r"##\s+(?P<note_type>[\w-]+)[\s\S]*?###\s+Properties\s*\n(?P<properties_raw>.*?)(?=\n##|\Z)"
    match = re.search(pattern, content)

    if not match:
        # Fallback if file doesn't follow the structured template
        return {}, content.strip(), ""

    note_type = match.group("note_type").strip()
    fm_raw = match.group("properties_raw").strip()

    metadata: Dict[str, Any] = {"note_type": note_type}

    # Parse YAML properties block
    if fm_raw:
        if yaml:
            try:
                parsed_yaml = yaml.safe_load(fm_raw)
                if isinstance(parsed_yaml, dict):
                    metadata.update(parsed_yaml)
            except Exception as parse_err:
                print(f"YAML parse error in {file_path}: {parse_err}")
        else:
            metadata.update(_fallback_parse_yaml(fm_raw))

    # Extract body content (everything after the Properties section)
    properties_end_idx = match.end("properties_raw")
    body = content[properties_end_idx:].strip()

    # Extract explicit '## Content' section if it exists (common in source-notes)
    content_match = re.search(r"##\s+Content\s*\n(.*)$", body, re.DOTALL)
    if content_match:
        metadata["content_body"] = content_match.group(1).strip()

    return metadata, body, fm_raw


def _fallback_parse_yaml(raw_str: str) -> Dict[str, Any]:
    """Basic fallback parser for properties if PyYAML is not installed."""
    data = {}
    current_list_key = None

    for line in raw_str.splitlines():
        line_str = line.strip()

        if not line_str or line_str.startswith("#"):
            continue

        # Handle list items (e.g., tags)
        if line_str.startswith("- ") and current_list_key:
            item = line_str[2:].strip().strip('"').strip("'")
            data[current_list_key].append(item)
            continue

        if ":" in line_str:
            key, val = line_str.split(":", 1)
            key = key.strip()

            # Remove inline YAML comments (e.g., `# choose one`)
            if " #" in val:
                val = val.split(" #")[0]

            val = val.strip().strip('"').strip("'")

            if not val:
                data[key] = []
                current_list_key = key
            else:
                current_list_key = None
                if val.lower() == "true":
                    data[key] = True
                elif val.lower() == "false":
                    data[key] = False
                elif val.isdigit():
                    data[key] = int(val)
                else:
                    data[key] = val

    return data

def build_index():

    status = subprocess.run(['git status'],capture_output=True, text=True,check=False)
    if status.stdout:
        # 