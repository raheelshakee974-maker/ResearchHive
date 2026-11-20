import re
import streamlit as st
from fpdf import FPDF
import agents as A
import history as H

st.set_page_config(
    page_title="ResearchHive AI",
    page_icon="🐝",
    layout="wide"
)

# ---------- DESIGN ----------


st.markdown("""
<style>
.stApp { background:#0B1512; color:#E8F5EF; }
[data-testid="stSidebar"] { background:#101D18; border-right:1px solid #254437; }
[data-testid="stHeader"] { background:rgba(11,21,18,.88); }
.hero {
  background:linear-gradient(120deg,#10251C,#174B36,#087A52);
  padding:30px; border:1px solid #286348; border-radius:18px; margin-bottom:24px;
  box-shadow:0 12px 35px rgba(0,0,0,.18);
}
.hero h1 {color:#F0FFF6;font-size:38px;margin:0;font-weight:800;}
.hero p {color:#C5E8D4;font-size:15px;}
.card,.agent {
  background:#142820; border:1px solid #254638; border-radius:14px;
  padding:19px; margin-bottom:12px;
}
.card h3 {color:#6EE7B7;font-size:14px;}
.card h2 {color:#F0FFF6;font-size:27px;}
.small {color:#A7BDB0;font-size:13px;}
.agent {text-align:center; padding:15px 8px;}
.agent h4 {color:#6EE7B7;margin:5px;}
.stButton>button,.stDownloadButton>button {
  background:linear-gradient(120deg,#087A52,#10B981); color:#F0FFF6;
  border:1px solid #20B981; border-radius:9px; font-weight:650;
}
.stButton>button:hover,.stDownloadButton>button:hover {
  background:#059669; color:white; border:1px solid #34D399;
}
h1,h2,h3,h4 {color:#E8F5EF;}
[data-testid="stMetric"] {
  background:#142820; border:1px solid #254638; padding:16px; border-radius:12px;
}
[data-testid="stMetricLabel"] {color:#A7BDB0;}
[data-testid="stMetricValue"] {color:#F0FFF6;}
.stTextInput input,.stTextArea textarea,.stSelectbox div[data-baseweb="select"] {
  background:#142820; color:#E8F5EF;
}
a {color:#6EE7B7 !important;}
hr {border-color:#254638;}
</style>
""", unsafe_allow_html=True)



# ---------- SESSION STATE ----------

defaults = {
    "report": "",
    "qs": [],
    "notes": "",
    "analysis": "",
    "facts": "",
    "sources": [],
    "topic": "",
    "docs": [],
    "doc_summary": ""
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------- PDF READER ----------

def read_files(files):
    docs = []

    for f in files or []:
        try:
            if f.name.lower().endswith(".pdf"):
                from pypdf import PdfReader
                text = "\n".join(
                    p.extract_text() or ""
                    for p in PdfReader(f).pages
                )
            else:
                text = f.read().decode("utf-8", "ignore")

            if text.strip():
                docs.append((f.name, text))

        except Exception as e:
            st.warning(f"{f.name}: {e}")

    return docs


# ---------- PROFESSIONAL PDF ----------

def to_pdf(md):

    class ResearchPDF(FPDF):

        def footer(self):
            self.set_y(-15)
            self.set_font("Helvetica", "", 9)
            self.set_text_color(120, 120, 140)
            self.cell(
                0, 10,
                f"ResearchHive AI | Page {self.page_no()}",
                align="C"
            )

    pdf = ResearchPDF()
    pdf.set_auto_page_break(True, 18)

    # Cover page
    pdf.add_page()
    pdf.set_fill_color(24, 25, 75)
    pdf.rect(0, 0, 210, 297, "F")

    pdf.set_y(75)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 30)
    pdf.multi_cell(0, 16, "RESEARCHHIVE AI", align="C")

    pdf.ln(10)
    pdf.set_font("Helvetica", "", 16)
    pdf.multi_cell(0, 10, "AI-Powered Research Report", align="C")

    pdf.ln(20)
    pdf.set_font("Helvetica", "", 12)
    pdf.multi_cell(
        0, 9,
        "Generated using a five-agent local AI research system.",
        align="C"
    )

    pdf.add_page()

    for line in md.splitlines():

        t = re.sub(r"[*`|]", "", line).strip()

        t = t.encode("latin-1", "replace").decode("latin-1")

        if not t:
            pdf.ln(3)
            continue

        if line.startswith("# "):
            pdf.set_font("Helvetica", "B", 19)
            pdf.set_text_color(60, 45, 150)
            t = t[2:]

        elif line.startswith("## "):
            pdf.ln(3)
            pdf.set_font("Helvetica", "B", 15)
            pdf.set_text_color(65, 60, 170)
            t = t[3:]

        elif line.startswith("###"):
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(85, 65, 180)
            t = t.lstrip("# ")

        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(45, 45, 55)

        pdf.multi_cell(0, 7, t)

    return bytes(pdf.output())


# ---------- SIDEBAR ----------

with st.sidebar:

    st.markdown("## 🐝 ResearchHive")

    st.caption("AI Research Workspace")

    st.success("● Ollama Connected")
    st.caption("Local Model: Gemma 2:2B")

    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "🏠 Dashboard",
            "🔬 New Research",
            "📚 Documents & AI",
            "🕘 Research History"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown("### 🤖 AI AGENTS")

    agents = [
        "🧭 Planner",
        "🔎 Researcher",
        "📊 Analyst",
        "✅ Fact-Checker",
        "✍️ Writer"
    ]

    for agent in agents:
        st.caption(agent)

    st.divider()

    st.caption("Muhammad Raheel")
    st.caption("BSAI | Superior University")


# ---------- HEADER ----------

st.markdown("""
<div class="hero">
<h1>🐝 ResearchHive AI</h1>
<p>Your intelligent multi-agent research workspace</p>
<p>Planner → Researcher → Analyst → Fact-Checker → Writer</p>
</div>
""", unsafe_allow_html=True)


# ---------- DASHBOARD ----------

if page == "🏠 Dashboard":

    st.title("Welcome to ResearchHive")
    st.caption("Your AI-powered research command center.")

    S = st.session_state
    history_items = H.list_reports() or []

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("AI Agents", "5", help="Planner, Researcher, Analyst, Fact-Checker and Writer")
    c2.metric("Questions", len(S["qs"]))
    c3.metric("Sources", len(S["sources"]))
    c4.metric("Report Words", len(S["report"].split()) if S["report"] else 0)

    st.subheader("⚡ AI Agent Workflow")
    cols = st.columns(5)
    workflow = [
        ("🧭", "Planner"),
        ("🔎", "Researcher"),
        ("📊", "Analyst"),
        ("✅", "Fact-Checker"),
        ("✍️", "Writer")
    ]

    for col, (emoji, name) in zip(cols, workflow):
        with col:
            st.markdown(
                f"""
                <div class="agent">
                    <h2>{emoji}</h2>
                    <h4>{name}</h4>
                    <span class="small">AI Agent</span>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.divider()
    st.subheader("📈 Research Analytics")

    # Build the trend from saved reports, rather than inventing chart values.
    from collections import Counter
    from datetime import datetime

    daily_counts = Counter()
    for item in history_items:
        raw_date = str(item.get("date", "")).strip()
        parsed_date = None
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%b %d, %Y", "%Y-%m-%d %H:%M:%S"):
            try:
                parsed_date = datetime.strptime(raw_date, fmt).date()
                break
            except ValueError:
                continue
        if parsed_date:
            daily_counts[parsed_date] += 1

    chart_left, chart_right = st.columns([1.5, 1])

    with chart_left:
        st.markdown("#### Research Activity")
        if daily_counts:
            import pandas as pd
            trend = pd.DataFrame(
                [{"Date": day, "Reports": count} for day, count in sorted(daily_counts.items())]
            ).set_index("Date")
            st.line_chart(trend, color="#10B981", height=260)
            st.caption("Completed reports by saved date.")
        else:
            st.info("Your research trend will appear here after reports are saved with a recognizable date.")

    with chart_right:
        st.markdown("#### Workspace Overview")
        overview = {
            "Saved projects": len(history_items),
            "Current questions": len(S["qs"]),
            "Current sources": len(S["sources"]),
        }
        st.bar_chart(
            __import__("pandas").DataFrame(
                {"Count": list(overview.values())},
                index=list(overview.keys())
            ),
            color="#34D399",
            height=260
        )
        st.caption("Live counts from your saved projects and current session.")

    st.divider()
    left, right = st.columns([1.5, 1])

    with left:
        st.subheader("📄 Latest Research")
        if S["report"]:
            st.markdown(
                f"""
                <div class="card">
                    <h3>LAST COMPLETED PROJECT</h3>
                    <h2>{S['topic']}</h2>
                    <p class="small">Research report available</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button("Open Latest Report"):
                st.session_state["show_report"] = True
                st.rerun()
        else:
            st.info("No research report yet. Start your first research.")

    with right:
        st.subheader("🚀 Quick Actions")
        if st.button("Start New Research", use_container_width=True):
            st.session_state["show_report"] = False
            st.session_state["selected_page"] = "🔬 New Research"
            st.rerun()
        if st.button("Open Documents", use_container_width=True):
            st.session_state["selected_page"] = "📚 Documents & AI"
            st.rerun()

    if st.session_state.get("show_report") and S["report"]:
        st.divider()
        st.subheader("Latest Report")
        st.markdown(S["report"])



# ---------- NEW RESEARCH ----------

elif page == "🔬 New Research":

    st.title("🔬 New Research")
    st.caption("Let five specialized AI agents work on your topic.")

    topic = st.text_input(
        "Research Topic",
        placeholder="e.g. Impact of Artificial Intelligence on Education"
    )

    n = st.slider("Number of research questions", 3, 6, 4)

    files = st.file_uploader(
        "Upload PDF / TXT documents (optional)",
        type=["pdf", "txt"],
        accept_multiple_files=True,
        key="research_files"
    )

    if st.button(
        "🚀 Start AI Research",
        disabled=not topic.strip(),
        use_container_width=True
    ):

        try:

            bar = st.progress(0)

            st.subheader("Agent Execution")

            with st.status("🧭 Planner working...", expanded=True) as s:

                qs = A.planner(topic, n, None)
                s.update(label="🧭 Planner completed", state="complete")

            bar.progress(20)

            with st.status("🔎 Researcher working...", expanded=True) as s:

                docs = read_files(files)

                notes, sources = A.researcher(
                    topic, qs, None, docs
                )

                s.update(
                    label=f"🔎 Research completed | {len(sources)} sources",
                    state="complete"
                )

            bar.progress(40)

            with st.status("📊 Analyst working...", expanded=True) as s:

                analysis = A.analyst(topic, notes, None)
                s.update(label="📊 Analysis completed", state="complete")

            bar.progress(60)

            with st.status("✅ Fact-Checker working...", expanded=True) as s:

                facts = A.fact_checker(
                    topic, notes, analysis, None
                )

                s.update(label="✅ Fact-check completed", state="complete")

            bar.progress(80)

            with st.status("✍️ Writer working...", expanded=True) as s:

                report = A.writer(
                    topic, qs, notes, analysis, facts, sources, None
                )

                s.update(label="✍️ Report completed", state="complete")

            bar.progress(100)

            data = {
                "topic": topic,
                "qs": qs,
                "notes": notes,
                "analysis": analysis,
                "facts": facts,
                "sources": sources,
                "report": report
            }

            H.save_report(topic, data)

            st.session_state.update(data)
            st.session_state["show_report"] = False

            st.success("🎉 Research completed successfully!")

            st.balloons()

            st.rerun()

        except Exception as e:
            st.error(f"Research Error: {e}")


# ---------- DOCUMENTS & AI ----------

elif page == "📚 Documents & AI":

    st.title("📚 Documents & AI")
    st.caption("Upload documents and use local AI to understand them.")

    uploaded = st.file_uploader(
        "Upload PDF / TXT",
        type=["pdf", "txt"],
        accept_multiple_files=True,
        key="summary_files"
    )

    if st.button("📄 Summarize Documents", disabled=not uploaded):

        try:

            docs = read_files(uploaded)

            if not docs:
                st.warning("No readable document found.")

            else:

                with st.spinner("AI is reading your documents..."):

                    summaries = []

                    for name, content in docs:

                        summary = A.llm(
                            f"Document: {name}\n\n{content[:12000]}\n\n"
                            "Create a detailed summary with headings, "
                            "important points and conclusion.",
                            "You are an expert document summarizer."
                        )

                        summaries.append(
                            f"## {name}\n\n{summary}"
                        )

                    st.session_state["doc_summary"] = "\n\n".join(summaries)

        except Exception as e:
            st.error(str(e))

    if st.session_state["doc_summary"]:

        st.divider()
        st.subheader("📄 AI Document Summary")

        st.markdown(st.session_state["doc_summary"])

        st.download_button(
            "Download Summary",
            st.session_state["doc_summary"],
            "document_summary.md"
        )


    st.divider()

    st.subheader("💬 Ask AI About Your Report")

    if st.session_state["report"]:

        question = st.text_input(
            "Ask a question",
            placeholder="Explain the key findings..."
        )

        if st.button("Ask AI", disabled=not question.strip()):

            with st.spinner("AI is thinking..."):

                try:

                    answer = A.llm(
                        f"Research Report:\n{st.session_state['report'][:15000]}\n\n"
                        f"User Question: {question}\n"
                        "Answer clearly using the report.",
                        "You are a research assistant. Answer based on the provided report."
                    )

                    st.markdown("### AI Answer")
                    st.write(answer)

                except Exception as e:
                    st.error(str(e))

    else:
        st.info("Generate a research report first to use Report Chat.")


# ---------- RESEARCH HISTORY ----------

elif page == "🕘 Research History":

    st.title("🕘 Research History")
    st.caption("Access your previously saved research projects.")

    items = H.list_reports()

    if items:

        for item in items:

            with st.expander(
                f"📄 {item['topic']} | {item['date']}"
            ):

                c1, c2 = st.columns(2)

                if c1.button(
                    "Open Report",
                    key=f"open_{item['id']}"
                ):

                    loaded = H.load_report(item["id"])

                    if loaded:
                        st.session_state.update(loaded)
                        st.success("Report loaded successfully!")
                        st.rerun()

                if c2.button(
                    "Delete Report",
                    key=f"delete_{item['id']}"
                ):

                    H.delete_report(item["id"])
                    st.rerun()

    else:
        st.info("No saved research reports available.")


# ---------- REPORT EXPLORER ----------

if st.session_state["report"]:

    st.divider()

    st.subheader("📑 Research Report Explorer")

    tabs = st.tabs([
        "Final Report",
        "Research Plan",
        "Sources",
        "Analysis",
        "Fact Check"
    ])

    with tabs[0]:

        st.markdown(st.session_state["report"])

        c1, c2 = st.columns(2)

        c1.download_button(
            "⬇️ Download Markdown",
            st.session_state["report"],
            "research_report.md",
            "text/markdown"
        )

        c2.download_button(
            "⬇️ Download Professional PDF",
            to_pdf(st.session_state["report"]),
            "research_report.pdf",
            "application/pdf"
        )

    with tabs[1]:

        for i, q in enumerate(st.session_state["qs"], 1):
            st.write(f"**{i}.** {q}")

    with tabs[2]:

        sources = st.session_state["sources"]

        if sources:

            for i, source in enumerate(sources, 1):

                st.markdown(
                    f"""
                    <div class="card">
                    <h3>SOURCE {i}</h3>
                    <h4>{source['title']}</h4>
                    <p class="small">{source['snippet']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if source["url"].startswith("http"):
                    st.markdown(f"[Open Source]({source['url']})")

        else:
            st.info("No sources available.")

    with tabs[3]:
        st.markdown(st.session_state["analysis"])

    with tabs[4]:
        st.markdown(st.session_state["facts"])


st.markdown("---")
st.caption("🐝 ResearchHive AI | Powered by Ollama Local AI")
