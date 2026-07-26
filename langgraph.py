from langchain.tools import tool
# import os
import subprocess
from pathlib import Path
import re

WIKI_DIR = './wiki'
RAW_DIR = './raw'

@tool
def search_wiki(query: str) -> str: # regex search for KEYWORDS across all md files in wiki
    try:
        result = subprocess.run( # subprocess is module used to run external commands - rg here 
                ## stands for ripgrep that is used to perfom fast regex queries
            ['rg', '-i','-n', '--max-count=3', query, WIKI_DIR],
            capture_output=True, text=True, check=False
        )
        if result.stdout: # output of the command
            return result.stdout[:3000]
        return f'No results found for the query {query}'
    except Exception as e:
        return f'Error: {str(e)}'

@tool
def read_page(fpath :str) -> str: # gets a file path and reads the entire file
    target = Path(WIKI_DIR) / fpath.lstrip('/') # Path is a Class providing way to managing file and directory paths
            # in this case target represents the entire path ./wiki/fpath
    if not target.exists():
        target = Path(WIKI_DIR) / f"{fpath.lstrip('/')}.md"
    if not target.exists():
        return f'Wiki page {fpath} does not exist at the path {f}'

    try:
        return target.read_text(encoding='utf-8') # method provided by pathlib.Path conviniently oprn
                                            # and read files
    except Exception as e:
        return f'Error handling the file: {e}'

@tool
def get_wiki_index(directory: str='')->str: # Returns all the .md files in a directory
    if directory == '':
        p = Path(WIKI_DIR)/'index.md'
        if p.exists():
            return p.read_text(encoding='utf8')
        return 'index.md not found'
    else:
        p = Path(WIKI_DIR)/directory.strip()

    if not p.exists():
        return f'{p} does not exist'
    files = [f.name for f in p.glob('*.md')]
    return f'files in {p} are \n' + '\n'.join(files)

@tool
def get_backlinks(filename:str) ->str: # returns backlinks
    # clean_name= filename.rstrip('.md')
    clean_name= filename.replace('md','').strip()
    pattern = re.compile(rf'\[\[{re.escape(clean_name)}\]\]', re.IGNORECASE)
    path = Path(WIKI_DIR)
    backlinks =[]
    for f in path.glob('*.md'):
        try:
            text = f.read_text(encoding='utf8')
            if pattern.search(text):
                rel_path = f.relative_to(WIKI_DIR)
                backlinks.append(rel_path)
        except Exception:
            continue
    if backlinks:
        return f'Pages having [[{filename}]] as backlinks: \n'+ '\n'.join(f'{b}' for b in backlinks)
    return f'No backlinks pointing to [[{filename}]]'

@tool
def read_raw_source(filename: str) -> str:
    target = Path(RAW_DIR) / filename.lstrip("/")
    if not target.exists():
        return f"Error: Raw source file '{filename}' not found in {RAW_DIR}."
    try:
        return target.read_text(encoding="utf-8")[:4000] # Read head excerpt
    except Exception as e:
        return f"Error opening raw file '{filename}': {str(e)}"



