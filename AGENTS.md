# CRITICAL RULES - MUST FOLLOW

## INTRODUCTION

Default structure:
- `raw/` holds the source documents
- `wiki/` holds compiled and source traceable knowledge notes
- `schema/` holds rules
  
Default workflow:
- Add source material to `raw/sources`
- Compile short reusable notes in `wiki/`
- Rebuild indexes and `wiki/index.md` ###
- Run lint and source checks
- Append `wiki/log.md`

## RESPONSES
- Keep responses concise and to the point - unless the user asks otherwise
  
## FRONT MATTER SCHEMA
- Every `.md` file inside `/wiki` must start with valid YAML front matter using this schema:
  ```yaml
  ---
  title: "Page Title"
  type: concept | entity | procedure | synthesis  # choose one
  summary: "Brief 1-2 sentence description."
  sources: "[[raw/sources/example-source]]"
  source_count:  # number of sources 
  last_updated: YYYY-MM-DD
  ---
- Do not create or edit Markdown files in `/wiki` without this front matter block.
  
## PLANNING MODE
- Always ask clarifying questions
- Use deep-dive sub-agents to assist with research
- Use deep-dive sub-agents to review the different aspects of your plan before presenting to the user

## CHANGE/EDIT MODE
- Never modify files inside `/raw`
- Wiki-linking: Use standard double-bracket wiki links [[page_name]] for interlinking concepts, entities, and procedures
- Query from `wiki/index.md` before opening broad context
- Keep compiled notes short, single-purpose, and source-traceable
- run build, lint, and source checks before commits
- Do Not invent citations or create unsupported claims
- Never implement features yourself, when possible use sub-agents!
- Main agent acts as a coordinator; delegate file-parsing or heavy drafting to sub-agents
- Use the best model for the task - premium models (DeepSeek V4 Pro) for complex tasks (like coding) and mid-tier models (e.g. DeepSeek V4 Flash) for simpler tasks like documentation
  