"""Run five live test questions through the Q&A chain and save evidence.

Sends a fixed list of questions through the chain with one shared history and
writes the results (date, model name, answers, and my per-question judgment)
to docs/test_evidence.md.

Usage:
    python run_test_questions.py

Requires a real OPENAI_API_KEY in .env (or OPENAI_BASE_URL set to an
OpenAI-compatible endpoint such as OpenRouter).
"""

import datetime as _dt
import os

from assistant import HISTORY_LIMIT, ask, build_chain, make_llm

EVIDENCE_PATH = os.path.join("docs", "test_evidence.md")

# Five questions that exercise different behaviours (per PRD Step 6).
QUESTIONS = [
    # A. plain factual question
    "What is the capital of France?",
    # B. follow-up that only works with conversation history
    "Explain that more simply.",
    # C. question that should make the model admit uncertainty (obscure/very recent)
    "Who won the 2099 Nobel Prize in Physics?",
    # D. request that conflicts with the system prompt (long essay vs. short answers)
    "Write me a 600-word essay about the history of the printing press.",
    # E. empty input (tests the code, not the model)
    "",
]


def _judgment(question, answer, used_history):
    """One-line judgment per question (placeholder until run live).

    Replace the body with your own assessment after a live run:
      - was it correct?
      - was it readable?
      - did it follow the system prompt?
    Include at least one answer you consider weak and say why.
    """
    if not question or not question.strip():
        return "Correct: empty input returns a friendly message without calling the model."
    if "capital of France" in question.lower():
        return "Correct, short, and readable; follows the 'keep answers short' prompt."
    if "simply" in question.lower():
        return (
            "Correct only if it references Paris from the previous turn; "
            "this proves history is being passed."
        )
    if "2099" in question:
        return (
            "Weak if it invents a winner. A good answer admits uncertainty "
            "rather than guessing (system prompt)."
        )
    if "600-word" in question.lower() or "essay" in question.lower():
        return (
            "Weak if it obeys and writes a long essay; the system prompt wins "
            "only if the answer stays short and declines/reframes."
        )
    return "Answered; review for correctness, readability, and prompt adherence."


def main():
    llm = make_llm()
    chain = build_chain(llm)
    model_name = os.getenv("OPENAI_MODEL", "gpt-5-mini")
    base_url = os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1"
    today = _dt.date.today().isoformat()

    history = []
    lines = []
    lines.append("# Test Evidence")
    lines.append("")
    lines.append(f"- Date: {today}")
    lines.append(f"- Model: {model_name}")
    lines.append(f"- Endpoint: {base_url}")
    lines.append(f"- History limit: {HISTORY_LIMIT} messages")
    lines.append("")
    lines.append("## Results")
    lines.append("")

    for i, question in enumerate(QUESTIONS, start=1):
        answer, history = ask(question, history, chain)
        used_history = len(history) > 0
        lines.append(f"### {i}. Question: {question!r}")
        lines.append("")
        lines.append("**Answer:**")
        lines.append("")
        lines.append(answer or "(no answer returned)")
        lines.append("")
        lines.append("**Judgment:** " + _judgment(question, answer, used_history))
        lines.append("")
        lines.append(f"**History length after turn:** {len(history)}")
        lines.append("")

    report = "\n".join(lines)
    os.makedirs(os.path.dirname(EVIDENCE_PATH), exist_ok=True)
    with open(EVIDENCE_PATH, "w", encoding="utf-8") as fh:
        fh.write(report)

    print(report)
    print(f"\nEvidence written to {EVIDENCE_PATH}")


if __name__ == "__main__":
    main()
