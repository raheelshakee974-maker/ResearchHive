
import os
import re
import time
import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS

MODEL = "openai/gpt-oss-20b"


def llm(prompt: str, system: str, api_key=None, retries: int = 2) -> str:
    key = api_key or os.getenv("GROQ_API_KEY")

    if not key:
        try:
            key = st.secrets.get("GROQ_API_KEY", "")
        except Exception:
            key = ""

    if not key:
        raise RuntimeError("GROQ_API_KEY is missing. Add it in Streamlit Secrets.")

    client = Groq(api_key=key)
    last = None

    for i in range(retries):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=2048
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            last = e
            time.sleep(2)

    raise RuntimeError(f"Groq API error: {last}")


def web_search(query, k=3):
    results = []

    try:
        with DDGS() as ddgs:
            items = ddgs.text(query, max_results=k)

            for item in items:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("href", ""),
                    "snippet": item.get("body", "")
                })

    except Exception:
        return []

    return results


def planner(topic, n, key=None):
    prompt = f"""
    Research Topic: {topic}

    Create {n} important research questions.
    Return only a numbered list.
    """

    result = llm(
        prompt,
        "You are an expert academic research planner.",
        key
    )

    questions = []

    for line in result.splitlines():
        line = re.sub(r"^\s*\d+[\.\)\-]\s*", "", line).strip()

        if line:
            questions.append(line)

    return questions[:n]


def researcher(topic, questions, key=None, docs=None):
    all_sources = []
    document_text = ""

    if docs:
        for doc in docs:
            if isinstance(doc, str):
                document_text += "\n" + doc
            else:
                document_text += "\n" + str(doc)

    search_queries = questions if questions else [topic]

    for question in search_queries:
        results = web_search(question, k=3)

        for result in results:
            if result["url"] and not any(
                s["url"] == result["url"] for s in all_sources
            ):
                all_sources.append(result)

    source_text = ""

    for i, source in enumerate(all_sources, 1):
        source_text += (
            f"\n[{i}] {source['title']}\n"
            f"URL: {source['url']}\n"
            f"Information: {source['snippet']}\n"
        )

    prompt = f"""
    Research Topic: {topic}

    Research Questions:
    {questions}

    Uploaded Documents:
    {document_text[:10000]}

    Web Research Sources:
    {source_text}

    Prepare detailed academic research notes.
    Use information from the supplied documents and sources.
    Add citations like [1], [2] where appropriate.
    Do not invent facts or references.
    """

    notes = llm(
        prompt,
        "You are an academic research assistant. Provide accurate, organized research notes.",
        key
    )

    return notes, all_sources


def analyst(topic, notes, key=None):
    prompt = f"""
    Topic: {topic}

    Research Notes:
    {notes}

    Analyze the research.
    Identify important findings, patterns, strengths,
    weaknesses, and conclusions.
    """

    return llm(
        prompt,
        "You are an expert academic research analyst.",
        key
    )


def fact_checker(topic, notes, analysis, key=None):
    prompt = f"""
    Topic: {topic}

    Research Notes:
    {notes}

    Analysis:
    {analysis}

    Check the claims for accuracy and consistency.
    Identify unsupported claims, possible errors,
    missing information, and limitations.
    Do not claim external verification unless evidence is available.
    """

    return llm(
        prompt,
        "You are a careful academic fact checker.",
        key
    )


def writer(topic, questions, notes, analysis, facts, sources, key=None):
    source_list = ""

    for i, source in enumerate(sources, 1):
        source_list += (
            f"\n[{i}] {source.get('title', '')} - "
            f"{source.get('url', '')}"
        )

    prompt = f"""
    Research Topic: {topic}

    Research Questions:
    {questions}

    Research Notes:
    {notes}

    Analysis:
    {analysis}

    Fact Checking:
    {facts}

    Sources:
    {source_list}

    Write a complete academic research report.
    Include:
    1. Title
    2. Introduction
    3. Main Discussion
    4. Analysis and Findings
    5. Limitations
    6. Conclusion
    7. References

    Use numbered citations matching the provided sources.
    Do not invent references.
    """

    return llm(
        prompt,
        "You are a professional academic research writer. Write clear, well-structured reports.",
        key
    )
