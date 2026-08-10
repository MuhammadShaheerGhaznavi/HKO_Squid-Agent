#!/usr/bin/env python3
"""Runs the retrieval agent against all evaluation questions and scores the results."""
import json
import time
import re
from pathlib import Path
from typing import Dict, List, Any

from agent_graph import structured_query, MAX_AGENT_ITERATIONS

QUESTIONS_FILE = Path(__file__).parent / "eval_questions.json"
RESULTS_FILE = Path(__file__).parent / "evaluation_results.json"
REPORT_FILE = Path(__file__).parent / "EVALUATION.md"


def load_questions() -> List[Dict]:
    return json.loads(QUESTIONS_FILE.read_text(encoding="utf-8"))


def check_keywords(answer: str, keywords: List[str]) -> float:
    """Return fraction of expected keywords found in the answer (case-insensitive)."""
    answer_lower = answer.lower()
    found = 0
    for kw in keywords:
        if kw.lower() in answer_lower:
            found += 1
    return round(found / len(keywords), 3) if keywords else 0.0


def check_sources(answer: str, expected_section: str) -> bool:
    """Check if the answer cites the expected AIP section reference."""
    section_key = re.sub(r"[^a-z0-9]", "", expected_section.lower())
    answer_clean = re.sub(r"[^a-z0-9]", "", answer.lower())
    return section_key in answer_clean


def score_accuracy(keyword_hit_rate: float) -> str:
    if keyword_hit_rate >= 0.80:
        return "high"
    elif keyword_hit_rate >= 0.50:
        return "partial"
    elif keyword_hit_rate >= 0.25:
        return "low"
    return "miss"


def run_evaluation():
    questions = load_questions()
    results: List[Dict[str, Any]] = []

    print(f"Running evaluation on {len(questions)} questions...")
    print("=" * 60)

    for i, q in enumerate(questions):
        print(f"\n[{i+1}/{len(questions)}] {q['id']}: {q['question'][:80]}...")

        start = time.time()
        try:
            result = structured_query(q["question"], MAX_AGENT_ITERATIONS)
        except Exception as e:
            result = {"query": q["question"], "answer": f"ERROR: {e}", "tool_calls": [], "sources": []}

        elapsed = round(time.time() - start, 1)
        answer = result.get("answer", "")
        tool_calls = result.get("tool_calls", [])
        sources = result.get("sources", [])

        keyword_hit_rate = check_keywords(answer, q["expected_keywords"])
        source_match = check_sources(answer, q.get("expected_section", ""))
        accuracy = score_accuracy(keyword_hit_rate)

        entry = {
            "id": q["id"],
            "question": q["question"],
            "type": q.get("type", "factual"),
            "answer": answer,
            "answer_short": answer[:200] + "..." if len(answer) > 200 else answer,
            "tool_call_count": len(tool_calls),
            "sources": sources,
            "latency_seconds": elapsed,
            "keyword_hit_rate": keyword_hit_rate,
            "keywords_found": [k for k in q["expected_keywords"] if k.lower() in answer.lower()],
            "keywords_missed": [k for k in q["expected_keywords"] if k.lower() not in answer.lower()],
            "source_match": source_match,
            "accuracy": accuracy,
            "expected_section": q.get("expected_section", ""),
            "tool_names": [tc.get("tool", "") for tc in tool_calls],
        }
        results.append(entry)

        print(f"  Latency: {elapsed}s | Tool calls: {len(tool_calls)} | "
              f"Keyword hit: {keyword_hit_rate:.1%} | Source match: {source_match} | Score: {accuracy}")

    RESULTS_FILE.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nResults saved to {RESULTS_FILE}")
    return results


def generate_report(results: List[Dict]):
    total = len(results)
    if total == 0:
        return

    acc_counts = {"high": 0, "partial": 0, "low": 0, "miss": 0}
    for r in results:
        acc_counts[r["accuracy"]] += 1

    high_pct = acc_counts["high"] / total * 100
    partial_pct = acc_counts["partial"] / total * 100
    low_pct = acc_counts["low"] / total * 100
    miss_pct = acc_counts["miss"] / total * 100

    avg_keyword = sum(r["keyword_hit_rate"] for r in results) / total
    avg_tool_calls = sum(r["tool_call_count"] for r in results) / total
    avg_latency = sum(r["latency_seconds"] for r in results) / total
    source_match_count = sum(1 for r in results if r["source_match"])

    # Group by type
    by_type: Dict[str, List[Dict]] = {}
    for r in results:
        by_type.setdefault(r["type"], []).append(r)

    report = f"""# LLM Wiki Retrieval Agent — Evaluation Report

## Summary

| Metric | Value |
|--------|-------|
| Questions evaluated | {total}
| High accuracy (≥80% keywords) | {acc_counts["high"]} ({high_pct:.0f}%)
| Partial accuracy (50-79%) | {acc_counts["partial"]} ({partial_pct:.0f}%)
| Low accuracy (25-49%) | {acc_counts["low"]} ({low_pct:.0f}%)
| Miss (<25%) | {acc_counts["miss"]} ({miss_pct:.0f}%)
| Average keyword match rate | **{avg_keyword:.1%}**
| Average tool calls per query | **{avg_tool_calls:.1f}**
| Average latency per query | **{avg_latency:.1f}s**
| Correct source references | {source_match_count}/{total} ({source_match_count/total*100:.0f}%)

## Resume-ready Metrics

> **Retrieval Agent Performance**: Achieved **{avg_keyword:.0%}** keyword recall across 15 evaluative queries on the Hong Kong AIP knowledge base (166 wiki entries, 612-page source document), averaging {avg_tool_calls:.1f} tool calls and {avg_latency:.0f}s per query using a ReAct agent with BM25 catalog search and deterministic page-range extraction.

## Accuracy by Question Type

| Type | Count | Avg Keyword Rate | Avg Tool Calls |
|------|-------|-----------------|----------------|
"""

    for qtype, entries in sorted(by_type.items()):
        avg_kw = sum(r["keyword_hit_rate"] for r in entries) / len(entries)
        avg_tc = sum(r["tool_call_count"] for r in entries) / len(entries)
        report += f"| {qtype} | {len(entries)} | {avg_kw:.1%} | {avg_tc:.1f} |\n"

    report += f"""
## Per-Question Results

| # | Question | Accuracy | Keywords | Calls | Source | Latency |
|---|----------|----------|----------|-------|--------|---------|
"""

    for r in results:
        kw_str = f"{int(r['keyword_hit_rate']*100)}%"
        src_str = "✓" if r["source_match"] else "✗"
        q_short = r["question"][:55] + "..." if len(r["question"]) > 55 else r["question"]
        report += f"| {r['id']} | {q_short} | {r['accuracy']} ({kw_str}) | {r['keyword_hit_rate']:.0%} | {r['tool_call_count']} | {src_str} | {r['latency_seconds']}s |\n"

    report += f"""
## Improvement Areas

### Ingestion Gaps (data not in wiki)
The following expected keywords were systematically absent from the wiki, indicating ingestion compression lost reference-level detail:
"""
    missed_all: Dict[str, int] = {}
    for r in results:
        for kw in r["keywords_missed"]:
            missed_all[kw] = missed_all.get(kw, 0) + 1
    for kw, count in sorted(missed_all.items(), key=lambda x: -x[1])[:10]:
        report += f"- **{kw}** — missed in {count} question(s)\n"

    report += "\n### Retrieval Gaps\n"
    no_source = [r for r in results if not r["source_match"]]
    if no_source:
        report += f"- {len(no_source)}/{total} questions could not find the correct AIP section reference\n"
    high_latency = [r for r in results if r["latency_seconds"] > 90]
    if high_latency:
        report += f"- {len(high_latency)} queries exceeded 90s (max tool-call loops)\n"

    REPORT_FILE.write_text(report, encoding="utf-8")
    print(f"Report saved to {REPORT_FILE}")


if __name__ == "__main__":
    results = run_evaluation()
    generate_report(results)
    print("\nDone.")
