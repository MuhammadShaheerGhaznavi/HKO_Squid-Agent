from typing import List, Any, Optional

from fastapi import FastAPI, Query
from pydantic import BaseModel

from agent_graph import structured_query, MAX_AGENT_ITERATIONS
from scripts.wiki_retriever import WikiRetriever

app = FastAPI(title="LLM Wiki Query API", version="1.0.0")
_retriever = WikiRetriever()


class ToolCallRecord(BaseModel):
    tool: str
    result_preview: str


class QueryRequest(BaseModel):
    query: str
    max_iterations: int = MAX_AGENT_ITERATIONS


class QueryResponse(BaseModel):
    query: str
    answer: str
    tool_calls: List[ToolCallRecord] = []
    sources: List[str] = []


@app.post("/query", response_model=QueryResponse)
def query_agent(req: QueryRequest):
    """Ask a question. Returns the synthesized answer, tool calls made, and wiki pages read."""
    result = structured_query(req.query, req.max_iterations)
    return QueryResponse(
        query=result["query"],
        answer=result["answer"],
        tool_calls=[ToolCallRecord(**tc) for tc in result["tool_calls"]],
        sources=result["sources"],
    )


@app.get("/search")
def search_catalog(q: str = Query(..., description="Search query"), top_k: int = Query(10)):
    results = _retriever.hybrid_search(q, top_k)
    return {
        "query": q,
        "count": len(results),
        "results": [
            {
                "title": r.entry.title,
                "path": r.entry.path,
                "type": r.entry.type,
                "summary": r.entry.summary,
                "keywords": r.entry.keywords,
                "score": r.score,
            }
            for r in results
        ],
    }


@app.get("/pages/{path:path}")
def read_page(path: str):
    content = _retriever.read_page(path)
    return {"path": path, "content": content}


@app.get("/health")
def health():
    return {"status": "ok"}


def main():
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
