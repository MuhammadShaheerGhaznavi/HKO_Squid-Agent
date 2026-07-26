# CRITICAL RULES - MUST FOLLOW

## RESPONSES
- Keep responses concise and to the point - unless the user asks otherwise
  
## FRONT MATTER SCHEMA
- Every `.md` file inside `/wiki` must start with valid YAML front matter using this schema:
  ```yaml
  ---
  title: "Page Title"
  type: concept | entity | procedure | synthesis  # choose one
  tags: [tag1, tag2]
  last_updated: YYYY-MM-DD
  summary: "Brief 1-2 sentence description."
  ---
- Do not create or edit Markdown files without this front matter block.
  
## PLANNING MODE
- Always ask clarifying questions
- Never assume design, tech stack or features
- Use deep-dive sub-agents to assist with research
- Use deep-dive sub-agents to review the different aspects of your plan before presenting to the user

## CHANGE/EDIT MODE
- Never modify files inside `/raw`
- Wiki-linking: Use standard double-bracket wiki links [[page_name]] for interlinking concepts, entities, and procedures
- Never implement features yourself, when possible use sub-agents!
- Main agent acts as a coordinator; delegate file-parsing or heavy drafting to sub-agents
- Identify changes from the plan that can be implemented in parallel, and use subagents to implement the features efficiently 
- Use the best model for the task - premium models (DeepSeek V4 Pro) for complex tasks (like coding) and mid-tier models (e.g. DeepSeek V4 Flash) for simpler tasks like documentation
  