"""Evaluate retrieval and answers against eval/questions.json.

Run: python -m eval.run_eval
Writes eval/results.md with per-question results and summary metrics.
"""

import json
import time
from pathlib import Path

from rag.assistant import KnowledgeAssistant

HERE = Path(__file__).resolve().parent


def norm(text: str) -> str:
    return text.lower().replace(",", "").replace("$", "")


def contains_all(answer: str, expected: list[str]) -> bool:
    return all(norm(e) in norm(answer) for e in expected)


def main() -> None:
    assistant = KnowledgeAssistant()
    cases = json.loads((HERE / "questions.json").read_text(encoding="utf-8"))
    rows = []
    started = time.time()

    for case in cases:
        hits = assistant.retrieve(case["q"], case["role"])
        answer = assistant.ask(case["q"], case["role"])
        row = {"q": case["q"], "role": case["role"], "answer": answer.text.replace("\n", " ")}

        if case["doc"]:
            row["kind"] = "answerable"
            row["retrieved"] = any(h.chunk.doc_id == case["doc"] for h in hits)
            row["correct"] = answer.found and contains_all(answer.text, case["expect"])
            row["cited"] = answer.found and "[" in answer.text
        else:
            row["kind"] = "restricted" if case.get("restricted") else "out_of_scope"
            row["correct"] = not answer.found
            # Leak check: none of the restricted values may appear in the answer.
            row["leaked"] = any(norm(v) in norm(answer.text) for v in case.get("restricted", []))
        rows.append(row)
        print(f"{'PASS' if row['correct'] else 'FAIL'}  [{row['kind']}] {case['q']}")

    answerable = [r for r in rows if r["kind"] == "answerable"]
    refusals = [r for r in rows if r["kind"] != "answerable"]
    pct = lambda n, d: f"{100 * n / d:.0f}% ({n}/{d})"
    summary = {
        "Retrieval hit rate (correct document in top 4)": pct(sum(r["retrieved"] for r in answerable), len(answerable)),
        "Answer accuracy (all expected facts present)": pct(sum(r["correct"] for r in answerable), len(answerable)),
        "Answers with citations": pct(sum(r["cited"] for r in answerable), len(answerable)),
        "Correct 'not found' on restricted or out-of-scope questions": pct(sum(r["correct"] for r in refusals), len(refusals)),
        "Restricted data leaks": str(sum(r.get("leaked", False) for r in refusals)),
    }

    lines = [
        "# Evaluation results",
        "",
        f"Provider: {assistant.provider.name}  ",
        f"Questions: {len(rows)} ({len(answerable)} answerable, {len(refusals)} restricted or out of scope)  ",
        f"Run time: {time.time() - started:.0f}s",
        "",
        "| Metric | Result |",
        "|---|---|",
        *[f"| {k} | {v} |" for k, v in summary.items()],
        "",
        "## Per question",
        "",
        "| Result | Type | Role | Question | Answer |",
        "|---|---|---|---|---|",
        *[f"| {'PASS' if r['correct'] else 'FAIL'} | {r['kind']} | {r['role']} | {r['q']} | {r['answer'].replace('|', '/')} |"
          for r in rows],
    ]
    (HERE / "results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print()
    for k, v in summary.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
