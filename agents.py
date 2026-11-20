"""ResearchHive - 5 specialised agents (Planner, Researcher, Analyst, Fact-Checker, Writer)."""

import re
import time
import ollama
from duckduckgo_search import DDGS

MODEL = "gemma2:2b"


# ---------- Local AI Connection ----------

def llm(prompt: str, system: str, api_key=None, retries: int = 2) -> str:

    last = None

    for i in range(retries):
        try:

            response = ollama.chat(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                options={
                    "temperature": 0.4
                }
            )

            return response["message"]["content"].strip()

        except Exception as e:
            last = e
            time.sleep(2)

    raise RuntimeError(
        f"Ollama error. Make sure Ollama is running. Detail: {last}"
    )


# ---------- Web Search ----------

def web_search(query: str, k: int = 3):

    try:
        with DDGS() as d:

            return [
                {
                    "title": x.get("title", ""),
                    "url": x.get("href", ""),
                    "snippet": x.get("body", "")
                }
                for x in d.text(query, max_results=k)
            ]

    except Exception:
        return []


# ---------- Agent 1: Planner ----------

def planner(topic, n, key=None):

    out = llm(
        f"Topic: {topic}\nWrite exactly {n} focused research questions, one per line, numbered. No extra text.",
        "You are a Research Planner agent. You break a topic into clear, non-overlapping research questions."
    )

    qs = [
        re.sub(r"^\s*\d+[\.\)]\s*", "", line).strip()
        for line in out.splitlines()
        if line.strip()
    ]

    return qs[:n]


# ---------- Agent 2: Researcher ----------

def researcher(topic, questions, key=None, docs=None):

    sources = []
    blocks = []

    for name, doc_text in (docs or []):

        sources.append({
            "title": f"Uploaded: {name}",
            "url": "uploaded document",
            "snippet": doc_text[:3000]
        })

    for q in questions:

        for s in web_search(f"{topic} {q}", 3):

            if s["url"] not in [x["url"] for x in sources]:
                sources.append(s)

    for i, s in enumerate(sources, 1):

        blocks.append(
            f"[{i}] {s['title']} ({s['url']})\n{s['snippet']}"
        )

    context = "\n\n".join(blocks) or (
        "No web results found. Use general knowledge and say so."
    )

    notes = llm(
        f"Topic: {topic}\nQuestions:\n"
        + "\n".join(f"- {q}" for q in questions)
        + f"\n\nSources:\n{context}\n\n"
        "Answer each question in 2-4 bullet points. Cite sources as [number].",
        "You are a Researcher agent. Use ONLY the given sources when possible and cite them as [n]."
    )

    return notes, sources


# ---------- Agent 3: Analyst ----------

def analyst(topic, notes, key=None):

    return llm(
        f"Topic: {topic}\nResearch notes:\n{notes}\n\n"
        "Produce markdown with: ### Key Themes, ### Opportunities, ### Challenges, ### Trends.",
        "You are an Analyst agent. Find patterns and insights, stay faithful to the notes."
    )


# ---------- Agent 4: Fact-Checker ----------

def fact_checker(topic, notes, analysis, key=None):

    return llm(
        f"Notes:\n{notes}\n\nAnalysis:\n{analysis}\n\n"
        "Extract 5-7 important claims. Output ONLY a markdown table with columns: "
        "| Claim | Verdict (Supported / Partially / Unverified) | "
        "Confidence (High/Medium/Low) | Source [n] |",
        "You are a strict Fact-Checker agent. Mark a claim Unverified if sources do not clearly support it."
    )


# ---------- Agent 5: Writer ----------

def writer(topic, questions, notes, analysis, facts, sources, key=None):

    body = llm(
        f"Topic: {topic}\nQuestions: {questions}\nNotes:\n{notes}\n"
        f"Analysis:\n{analysis}\nFact-check:\n{facts}\n\n"
        "Write a professional research report in markdown with sections: "
        "# Title, ## Executive Summary, ## Background, ## Key Findings, "
        "## Analysis, ## Fact-Check Summary, ## Conclusion & Recommendations. "
        "Keep [n] citations.",
        "You are a Writer agent producing clear, academic-style reports."
    )

    refs = "\n".join(
        f"{i}. {s['title']} - {s['url']}"
        for i, s in enumerate(sources, 1)
    )

    return body + "\n\n## References\n" + (
        refs or "No external sources were retrieved."
    )
