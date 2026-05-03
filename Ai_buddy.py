import streamlit as st
import pdfplumber
from groq import Groq
import json
import tempfile
import os
import re

# ══════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════
st.set_page_config(
    page_title="ExamAI — Smart Exam Strategist",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════
#  CUSTOM CSS — Glassmorphism Orange/Dark Theme
# ══════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Background ── */
.stApp { background-color: #0d1117; color: #e6edf3; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background-color: #161b22;
    border-right: 1px solid #30363d;
}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] label { color: #8b949e; font-size: 0.82rem; }

/* ── Headings ── */
h1 { color: #e6edf3 !important; font-weight: 700 !important; }
h2 { color: #e6edf3 !important; font-weight: 600 !important; }
h3 { color: #c9d1d9 !important; font-weight: 600 !important; }

/* ── Glass Card ── */
.card {
    background: rgba(22,27,34,0.85);
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
    backdrop-filter: blur(8px);
}
.card-orange {
    background: rgba(22,27,34,0.85);
    border: 1px solid rgba(251,140,0,0.35);
    border-left: 3px solid #fb8c00;
    border-radius: 0 12px 12px 0;
    padding: 16px 20px;
    margin-bottom: 12px;
    backdrop-filter: blur(8px);
}
.card-blue {
    background: rgba(22,27,34,0.85);
    border: 1px solid #388bfd40;
    border-left: 3px solid #388bfd;
    border-radius: 0 12px 12px 0;
    padding: 16px 20px;
    margin-bottom: 12px;
}
.card-green {
    background: rgba(22,27,34,0.85);
    border: 1px solid rgba(63,185,80,0.35);
    border-left: 3px solid #3fb950;
    border-radius: 0 12px 12px 0;
    padding: 16px 20px;
    margin-bottom: 12px;
}
.card-red {
    background: rgba(22,27,34,0.85);
    border: 1px solid rgba(248,81,73,0.35);
    border-left: 3px solid #f85149;
    border-radius: 0 12px 12px 0;
    padding: 16px 20px;
    margin-bottom: 12px;
}

/* ── Stat boxes ── */
.stat-box {
    background: rgba(22,27,34,0.85);
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 18px 10px;
    text-align: center;
    backdrop-filter: blur(8px);
}
.stat-number { font-size: 1.9rem; font-weight: 700; color: #fb8c00; }
.stat-label  { font-size: 0.78rem; color: #8b949e; margin-top: 2px; }

/* ── Priority Score Badge ── */
.score-critical { background: #f85149; color: #fff; padding: 2px 10px; border-radius: 20px; font-size:0.78rem; font-weight:700; }
.score-high     { background: #fb8c00; color: #fff; padding: 2px 10px; border-radius: 20px; font-size:0.78rem; font-weight:700; }
.score-medium   { background: #388bfd; color: #fff; padding: 2px 10px; border-radius: 20px; font-size:0.78rem; font-weight:700; }
.score-low      { background: #484f58; color: #e6edf3; padding: 2px 10px; border-radius: 20px; font-size:0.78rem; font-weight:700; }

/* ── Topic Table ── */
.topic-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 14px;
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 8px;
    margin-bottom: 6px;
}
.topic-name { flex: 1; color: #e6edf3; font-size: 0.9rem; font-weight: 500; }
.topic-bar-wrap { flex: 2; background: #21262d; border-radius: 4px; height: 8px; }
.topic-bar { height: 8px; border-radius: 4px; background: linear-gradient(90deg, #fb8c00, #f85149); }
.topic-score { color: #fb8c00; font-weight: 700; font-size: 0.9rem; min-width: 40px; text-align:right; }

/* ── Buttons ── */
.stButton > button {
    background: #fb8c00;
    color: #0d1117;
    font-weight: 700;
    border: 1px solid #fb8c00;
    border-radius: 8px;
    padding: 0.5em 1.6em;
    font-size: 0.95rem;
    width: 100%;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: #ef6c00;
    border-color: #ef6c00;
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(251,140,0,0.25);
}

/* ── Inputs ── */
.stTextInput input, .stTextArea textarea {
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 8px;
    color: #e6edf3;
    font-family: 'Inter', sans-serif;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #fb8c00;
    box-shadow: 0 0 0 3px rgba(251,140,0,0.15);
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: rgba(22,27,34,0.85);
    border: 1px dashed #30363d;
    border-radius: 10px;
    padding: 6px;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid #30363d;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #8b949e;
    border: none;
    padding: 8px 20px;
    font-size: 0.88rem;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    color: #fb8c00 !important;
    border-bottom: 2px solid #fb8c00 !important;
}

hr { border-color: #21262d; }

/* ── Result box ── */
.result-box {
    background: rgba(22,27,34,0.85);
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 28px 32px;
    line-height: 1.85;
    font-size: 0.95rem;
    color: #e6edf3;
    backdrop-filter: blur(8px);
}

/* ── Insight Pill ── */
.insight-pill {
    display: inline-block;
    background: rgba(251,140,0,0.12);
    border: 1px solid rgba(251,140,0,0.4);
    color: #fb8c00;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.8rem;
    font-weight: 600;
    margin: 3px;
}
.gap-pill {
    display: inline-block;
    background: rgba(248,81,73,0.12);
    border: 1px solid rgba(248,81,73,0.4);
    color: #f85149;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.8rem;
    font-weight: 600;
    margin: 3px;
}

/* ── Wf step ── */
.wf-step {
    background: rgba(22,27,34,0.85);
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 14px 10px;
    text-align: center;
    font-size: 0.82rem;
    color: #8b949e;
}
.wf-step b { color: #e6edf3; display: block; margin: 4px 0 2px; font-size: 0.88rem; }
.wf-arrow { display:flex; align-items:center; justify-content:center; color:#30363d; font-size:1.4rem; }

/* ── Badge ── */
.badge {
    display: inline-block;
    background: #21262d;
    border: 1px solid #30363d;
    color: #8b949e;
    border-radius: 6px;
    padding: 3px 12px;
    font-size: 0.8rem;
    font-weight: 500;
    margin: 3px;
}

/* ── Chat ── */
.chat-wrap {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 20px;
    max-height: 500px;
    overflow-y: auto;
    margin-bottom: 14px;
}
.msg-user { display: flex; justify-content: flex-end; margin-bottom: 14px; }
.msg-user-bubble {
    background: #fb8c00;
    color: #0d1117;
    border-radius: 16px 16px 4px 16px;
    padding: 10px 16px;
    max-width: 68%;
    font-size: 0.9rem;
    line-height: 1.5;
    font-weight: 500;
}
.msg-ai { display: flex; gap: 10px; margin-bottom: 14px; align-items: flex-start; }
.msg-ai-avatar {
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 50%;
    width: 34px; height: 34px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.9rem; flex-shrink: 0;
}
.msg-ai-bubble {
    background: #21262d;
    border: 1px solid #30363d;
    color: #e6edf3;
    border-radius: 4px 16px 16px 16px;
    padding: 10px 16px;
    max-width: 76%;
    font-size: 0.9rem;
    line-height: 1.65;
}
.context-bar {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 0.82rem;
    color: #8b949e;
    margin-bottom: 14px;
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    align-items: center;
}
.context-dot { color: #fb8c00; font-size: 0.7rem; }

/* ── Question card ── */
.question-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 10px;
}
.question-num {
    display: inline-block;
    background: rgba(251,140,0,0.15);
    color: #fb8c00;
    border-radius: 50%;
    width: 24px; height: 24px;
    text-align: center;
    line-height: 24px;
    font-size: 0.78rem;
    font-weight: 700;
    margin-right: 8px;
    flex-shrink: 0;
}
.empty-chat {
    text-align: center;
    color: #484f58;
    padding: 30px 20px;
    font-size: 0.9rem;
}
.chip {
    display: inline-block;
    background: #21262d;
    border: 1px solid #30363d;
    color: #8b949e;
    border-radius: 20px;
    padding: 5px 13px;
    font-size: 0.8rem;
    margin: 3px;
    cursor: pointer;
}
.chip:hover { border-color: #fb8c00; color: #fb8c00; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════
defaults = {
    "chat_messages": [],
    "extracted_text": "",
    "source_label": "",
    "past_papers_texts": [],   # list of {"name": str, "text": str, "pages": int}
    "syllabus_text": "",
    "syllabus_name": "",
    "strategy_results": None,  # parsed JSON from Groq
    "strategy_done": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🔑 API Key")
    groq_api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
    st.markdown(
        "<a href='https://console.groq.com' target='_blank' "
        "style='font-size:0.8rem;color:#fb8c00;'>Get free key →</a>",
        unsafe_allow_html=True,
    )
    st.divider()

    st.markdown("### ⚙️ Settings")
    model_choice = st.selectbox(
        "Model",
        ["llama-3.3-70b-versatile", "llama3-70b-8192", "mixtral-8x7b-32768"],
        index=0,
    )
    study_days = st.slider("Study plan (days)", 3, 7, 5)
    top_n_topics = st.slider("Practice questions for top N topics", 2, 6, 3)
    st.divider()

    if st.button("🗑️ Clear All"):
        for k, v in defaults.items():
            st.session_state[k] = v
        st.rerun()

    st.markdown("""
    <div style='font-size:0.78rem; color:#484f58; margin-top:8px;'>
    <b style='color:#8b949e;'>Tips</b><br>
    • Upload 3+ past papers for best insights<br>
    • Include a syllabus PDF for gap analysis<br>
    • Digital PDFs extract better than scans<br>
    • Check Practice Mode for exam questions
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════
st.markdown("<br>", unsafe_allow_html=True)
col_h, _ = st.columns([3, 1])
with col_h:
    st.markdown("""
    <div>
        <h1 style='font-size:2.2rem; margin:0;'>🎯 Smart Exam Strategist</h1>
        <p style='color:#8b949e; margin:6px 0 0 0; font-size:1rem;'>
            Upload past papers + syllabus — AI finds gaps, scores topics, and builds your exam strategy.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Dynamic stats
n_papers = len(st.session_state.past_papers_texts)
has_syllabus = bool(st.session_state.syllabus_text)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="stat-box"><div class="stat-number">{n_papers}</div><div class="stat-label">Past Papers Loaded</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="stat-box"><div class="stat-number">{"✓" if has_syllabus else "—"}</div><div class="stat-label">Syllabus Loaded</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="stat-box"><div class="stat-number">{study_days}</div><div class="stat-label">Day Study Sprint</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="stat-box"><div class="stat-number">AI</div><div class="stat-label">Groq LLaMA Powered</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════
#  WORKFLOW STEPS
# ══════════════════════════════════════════════════
st.markdown("#### How it works")
w = st.columns([2, .4, 2, .4, 2, .4, 2, .4, 2])
steps = [
    ("📥", "Upload", "Past Papers + Syllabus"),
    ("🔍", "Extract", "Text from all PDFs"),
    ("🧠", "Compare", "Papers vs Syllabus"),
    ("📊", "Score", "Topics 1-100 priority"),
    ("🎯", "Practice", "AI exam questions"),
]
arrows = [w[1], w[3], w[5], w[7]]
cols = [w[0], w[2], w[4], w[6], w[8]]
for i, (icon, title, sub) in enumerate(steps):
    with cols[i]:
        st.markdown(f'<div class="wf-step">{icon}<b>{title}</b>{sub}</div>', unsafe_allow_html=True)
    if i < len(arrows):
        with arrows[i]:
            st.markdown('<div class="wf-arrow">›</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════
#  MAIN TABS
# ══════════════════════════════════════════════════
tab_upload, tab_strategy, tab_practice, tab_chat = st.tabs([
    "📥  Upload Papers",
    "📊  Strategy Analysis",
    "🎯  Practice Mode",
    "💬  AI Chat",
])

# ══════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ══════════════════════════════════════════════════
def extract_pdf(file) -> tuple[str, int]:
    """Extract text from a PDF file object. Returns (text, page_count)."""
    pages_text = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                pages_text.append(t)
        return "\n".join(pages_text), len(pdf.pages)


def chunk_text(text: str, max_chars: int = 4000) -> str:
    """Return the first max_chars of text — fast, sufficient for topic extraction."""
    return text[:max_chars]


def build_strategy_prompt(syllabus: str, papers: list[dict], days: int, top_n: int) -> str:
    """Build the master prompt for Groq. Returns a prompt string."""
    # Compress each paper to a representative chunk
    paper_snippets = ""
    for i, p in enumerate(papers):
        snippet = chunk_text(p["text"], 3000)
        paper_snippets += f"\n\n--- PAST PAPER {i+1}: {p['name']} ---\n{snippet}"

    syllabus_chunk = chunk_text(syllabus, 4000) if syllabus else "No syllabus provided."

    prompt = f"""You are an expert Exam Strategist AI. Analyse the following syllabus and {len(papers)} past exam papers.

Return ONLY a valid JSON object — no markdown, no extra text, no code fences. The JSON must follow this exact schema:

{{
  "topics": [
    {{
      "name": "Topic Name",
      "frequency": <int 0-{len(papers)}>,
      "syllabus_weight": <int 1-10>,
      "priority_score": <int 1-100>,
      "trend": "Rising|Stable|Declining",
      "years_tag": "<e.g. '2022, 2023, 2024' or 'Never asked'>"
    }}
  ],
  "coverage_gaps": ["Topic A", "Topic B"],
  "high_yield_zones": ["Topic X", "Topic Y"],
  "key_insight": "One powerful sentence insight for the student.",
  "study_plan": [
    {{"day": 1, "focus": "Topic", "task": "What to do", "hours": 2}}
  ],
  "practice_questions": [
    {{
      "topic": "Topic Name",
      "questions": ["Q1 text", "Q2 text", "Q3 text"]
    }}
  ]
}}

Rules:
- Include 8-15 topics total (covering all major syllabus areas)
- priority_score = (frequency/{len(papers)} * 60) + (syllabus_weight/10 * 40), round to integer 1-100
- coverage_gaps = topics in syllabus but with frequency 0 (never asked in any past paper)
- high_yield_zones = topics with priority_score >= 75
- study_plan must have exactly {days} days; day {days} = mock test + revision
- practice_questions must cover the top {top_n} topics by priority_score, 3 questions each
- Questions should mimic the style/pattern seen in the past papers
- All questions should be specific and exam-realistic (not vague)

--- SYLLABUS ---
{syllabus_chunk}

--- PAST PAPERS ---
{paper_snippets}
"""
    return prompt


def run_strategy_analysis(
    syllabus: str,
    papers: list[dict],
    api_key: str,
    model: str,
    days: int,
    top_n: int,
) -> dict:
    """Send prompt to Groq, parse and return JSON result."""
    client = Groq(api_key=api_key)
    prompt = build_strategy_prompt(syllabus, papers, days, top_n)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a precise exam strategy AI. You always respond with valid JSON only. "
                    "No markdown, no explanation, no code blocks. Pure JSON."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=4096,
    )

    raw = response.choices[0].message.content.strip()
    # Strip accidental markdown fences
    raw = re.sub(r"^```[a-z]*\n?", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"```$", "", raw, flags=re.MULTILINE)
    return json.loads(raw.strip())


def priority_class(score: int) -> str:
    if score >= 80:
        return "score-critical"
    if score >= 60:
        return "score-high"
    if score >= 40:
        return "score-medium"
    return "score-low"


def priority_label(score: int) -> str:
    if score >= 80:
        return "🔴 Critical"
    if score >= 60:
        return "🟠 High"
    if score >= 40:
        return "🔵 Medium"
    return "⚪ Low"


def transcribe_audio_file(file_bytes: bytes, filename: str, api_key: str) -> str:
    client = Groq(api_key=api_key)
    ext = os.path.splitext(filename)[1].lower()
    supported = [".mp3", ".mp4", ".m4a", ".wav", ".webm", ".mpeg", ".mpga", ".mov", ".ogg"]
    if ext not in supported:
        ext = ".mp4"
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    try:
        with open(tmp_path, "rb") as f:
            result = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=(os.path.basename(tmp_path), f),
                response_format="text",
            )
        return result
    finally:
        os.unlink(tmp_path)


def chat_with_content(question: str, history: list, content: str, source_label: str, api_key: str, model: str) -> str:
    client = Groq(api_key=api_key)
    sys_msg = (
        f"You are a helpful AI study assistant. The student uploaded {source_label}.\n"
        "Use the content below as your primary knowledge base. Be concise, clear, and encouraging.\n"
        "If something isn't in the content, say so honestly.\n\nCONTENT:\n\"\"\"\n"
        f"{content[:10000]}\n\"\"\""
    )
    messages = [{"role": "system", "content": sys_msg}]
    for m in history:
        messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": question})
    r = client.chat.completions.create(model=model, messages=messages, temperature=0.6, max_tokens=900)
    return r.choices[0].message.content


# ══════════════════════════════════════════════════
#  TAB 1 — UPLOAD PAPERS
# ══════════════════════════════════════════════════
with tab_upload:
    st.markdown("#### 📄 Upload Past Exam Papers")
    st.markdown("<p style='color:#8b949e;font-size:0.88rem;margin-top:-10px;'>Upload 2–6 past papers for best accuracy. More papers = sharper insights.</p>", unsafe_allow_html=True)

    L, R = st.columns([3, 2])
    with L:
        past_paper_files = st.file_uploader(
            "Upload Past Papers (PDF)",
            type=["pdf"],
            accept_multiple_files=True,
            key="past_papers_upload",
            label_visibility="collapsed",
        )
    with R:
        st.markdown("""<div class='card' style='margin-top:0'>
        <div style='font-size:0.82rem;font-weight:600;color:#8b949e;margin-bottom:8px;'>BEST FOR</div>
        <div style='font-size:0.88rem;color:#c9d1d9;line-height:1.8;'>
        2022, 2023, 2024 exam papers<br>Board / University past papers<br>Multiple years = trend detection<br>3+ papers recommended
        </div></div>""", unsafe_allow_html=True)

    if past_paper_files:
        st.markdown(f"**{len(past_paper_files)} file(s) selected:**")
        for f in past_paper_files:
            st.markdown(f"&nbsp;&nbsp;📄 `{f.name}`")

    st.divider()

    st.markdown("#### 📋 Upload Syllabus PDF")
    st.markdown("<p style='color:#8b949e;font-size:0.88rem;margin-top:-10px;'>The syllabus lets AI find coverage gaps — topics never asked but on your curriculum.</p>", unsafe_allow_html=True)

    L2, R2 = st.columns([3, 2])
    with L2:
        syllabus_file = st.file_uploader(
            "Upload Syllabus (PDF)",
            type=["pdf"],
            key="syllabus_upload",
            label_visibility="collapsed",
        )
    with R2:
        st.markdown("""<div class='card' style='margin-top:0'>
        <div style='font-size:0.82rem;font-weight:600;color:#8b949e;margin-bottom:8px;'>OPTIONAL BUT RECOMMENDED</div>
        <div style='font-size:0.88rem;color:#c9d1d9;line-height:1.8;'>
        Official course syllabus<br>Subject specification document<br>Curriculum outline PDF<br>Unit / topic weightage sheet
        </div></div>""", unsafe_allow_html=True)

    if syllabus_file:
        st.success(f"✅  Syllabus: {syllabus_file.name}")

    st.markdown("<br>", unsafe_allow_html=True)

    # EXTRACT BUTTON
    _, bc_ext, _ = st.columns([1, 2, 1])
    with bc_ext:
        extract_btn = st.button("📥  Extract & Load All PDFs")

    if extract_btn:
        if not past_paper_files:
            st.error("Please upload at least one past paper PDF.")
            st.stop()

        # Extract past papers
        loaded = []
        with st.spinner("Extracting past papers…"):
            for f in past_paper_files:
                try:
                    text, pages = extract_pdf(f)
                    if text.strip():
                        loaded.append({"name": f.name, "text": text, "pages": pages})
                        st.success(f"✅ {f.name} — {pages} pages, {len(text.split()):,} words")
                    else:
                        st.warning(f"⚠️ {f.name} — no readable text found (scanned PDF?)")
                except Exception as e:
                    st.error(f"❌ {f.name}: {e}")

        st.session_state.past_papers_texts = loaded

        # Extract syllabus
        if syllabus_file:
            with st.spinner("Extracting syllabus…"):
                try:
                    syl_text, syl_pages = extract_pdf(syllabus_file)
                    st.session_state.syllabus_text = syl_text
                    st.session_state.syllabus_name = syllabus_file.name
                    st.success(f"✅ Syllabus: {syllabus_file.name} — {syl_pages} pages")
                except Exception as e:
                    st.error(f"Could not read syllabus: {e}")
        else:
            st.session_state.syllabus_text = ""
            st.session_state.syllabus_name = ""

        # Also merge into extracted_text for chat
        all_text = "\n\n".join(p["text"] for p in loaded)
        if st.session_state.syllabus_text:
            all_text = "SYLLABUS:\n" + st.session_state.syllabus_text + "\n\n" + all_text
        st.session_state.extracted_text = all_text
        st.session_state.source_label = f"{len(loaded)} past papers + syllabus"
        st.session_state.strategy_done = False  # reset so analysis reruns
        st.session_state.strategy_results = None

        if loaded:
            st.info(f"✅ {len(loaded)} paper(s) ready. Go to **📊 Strategy Analysis** tab to run AI analysis.")

    # Show current state
    if st.session_state.past_papers_texts:
        st.markdown("---")
        st.markdown("**📦 Currently Loaded:**")
        for p in st.session_state.past_papers_texts:
            st.markdown(f"&nbsp;&nbsp;📄 `{p['name']}` — {p['pages']} pages")
        if st.session_state.syllabus_name:
            st.markdown(f"&nbsp;&nbsp;📋 Syllabus: `{st.session_state.syllabus_name}`")

# ══════════════════════════════════════════════════
#  TAB 2 — STRATEGY ANALYSIS
# ══════════════════════════════════════════════════
with tab_strategy:
    if not st.session_state.past_papers_texts:
        st.markdown("""
        <div style='background:#161b22;border:1px dashed #30363d;border-radius:10px;
                    padding:36px;text-align:center;color:#484f58;'>
            📥 Upload your past papers in the <b style='color:#8b949e;'>Upload Papers</b> tab first.
        </div>
        """, unsafe_allow_html=True)
    else:
        _, bc_run, _ = st.columns([1, 2, 1])
        with bc_run:
            run_btn = st.button("🧠  Run AI Strategy Analysis")

        if run_btn:
            if not groq_api_key:
                st.error("Please add your Groq API key in the sidebar.")
                st.stop()
            with st.spinner("Groq AI is comparing papers vs syllabus — this takes ~15 seconds…"):
                try:
                    result = run_strategy_analysis(
                        syllabus=st.session_state.syllabus_text,
                        papers=st.session_state.past_papers_texts,
                        api_key=groq_api_key,
                        model=model_choice,
                        days=study_days,
                        top_n=top_n_topics,
                    )
                    st.session_state.strategy_results = result
                    st.session_state.strategy_done = True
                except json.JSONDecodeError as e:
                    st.error(f"AI returned malformed JSON. Try again or switch models. Details: {e}")
                    st.stop()
                except Exception as e:
                    err = str(e)
                    if "401" in err or "auth" in err.lower():
                        st.error("Invalid API key.")
                    elif "429" in err:
                        st.error("Rate limit — wait 30s and retry.")
                    elif "404" in err:
                        st.error("Model not found — try another in settings.")
                    else:
                        st.error(f"Error: {err}")
                    st.stop()

        if st.session_state.strategy_done and st.session_state.strategy_results:
            res = st.session_state.strategy_results
            topics = res.get("topics", [])
            gaps = res.get("coverage_gaps", [])
            high_yield = res.get("high_yield_zones", [])
            key_insight = res.get("key_insight", "")
            study_plan = res.get("study_plan", [])

            # ── Key Insight Banner ──
            if key_insight:
                st.markdown(f"""
                <div class='card-orange' style='margin-bottom:20px;'>
                    <span style='font-size:0.78rem;font-weight:700;color:#fb8c00;letter-spacing:1px;'>💡 KEY INSIGHT</span><br>
                    <span style='color:#e6edf3;font-size:0.95rem;'>{key_insight}</span>
                </div>
                """, unsafe_allow_html=True)

            # ── Summary stats ──
            n_critical = sum(1 for t in topics if t.get("priority_score", 0) >= 80)
            n_gaps = len(gaps)
            n_high = len(high_yield)
            s1, s2, s3, s4 = st.columns(4)
            with s1:
                st.markdown(f'<div class="stat-box"><div class="stat-number">{len(topics)}</div><div class="stat-label">Topics Mapped</div></div>', unsafe_allow_html=True)
            with s2:
                st.markdown(f'<div class="stat-box"><div class="stat-number" style="color:#f85149;">{n_critical}</div><div class="stat-label">🔴 Critical Topics</div></div>', unsafe_allow_html=True)
            with s3:
                st.markdown(f'<div class="stat-box"><div class="stat-number" style="color:#3fb950;">{n_high}</div><div class="stat-label">High-Yield Zones</div></div>', unsafe_allow_html=True)
            with s4:
                st.markdown(f'<div class="stat-box"><div class="stat-number" style="color:#f85149;">{n_gaps}</div><div class="stat-label">Coverage Gaps</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            col_left, col_right = st.columns([3, 2])

            with col_left:
                # ── Topic Frequency Chart ──
                st.markdown("#### 📊 Topic Priority Chart")
                if topics:
                    import pandas as pd
                    df = pd.DataFrame(topics).sort_values("priority_score", ascending=False)
                    chart_df = df.set_index("name")[["priority_score"]].rename(
                        columns={"priority_score": "Priority Score (1-100)"}
                    )
                    st.bar_chart(chart_df, color="#fb8c00", height=320)

                # ── Topic Frequency vs Syllabus Weight scatter ──
                st.markdown("#### 🗺️ Frequency vs Syllabus Weight")
                if topics:
                    freq_df = pd.DataFrame(topics)[["name", "frequency", "syllabus_weight"]].copy()
                    freq_df = freq_df.rename(columns={
                        "frequency": "Past Paper Frequency",
                        "syllabus_weight": "Syllabus Weight",
                    }).set_index("name")
                    st.scatter_chart(freq_df, x="Past Paper Frequency", y="Syllabus Weight", size=60, color="#fb8c00", height=280)

            with col_right:
                # ── High-Yield Zones ──
                st.markdown("#### 🔥 High-Yield Zones")
                if high_yield:
                    pills = " ".join(f'<span class="insight-pill">🔥 {t}</span>' for t in high_yield)
                    st.markdown(f"<div style='margin-bottom:16px;'>{pills}</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<p style='color:#8b949e;'>No high-yield zones detected.</p>", unsafe_allow_html=True)

                # ── Coverage Gaps ──
                st.markdown("#### 🕳️ Coverage Gaps")
                st.markdown("<p style='color:#8b949e;font-size:0.82rem;'>Topics in syllabus but never asked in past papers — potential surprise questions.</p>", unsafe_allow_html=True)
                if gaps:
                    pills = " ".join(f'<span class="gap-pill">⚠️ {t}</span>' for t in gaps)
                    st.markdown(f"<div style='margin-bottom:16px;'>{pills}</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<p style='color:#8b949e;'>No gaps detected — great syllabus coverage!</p>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Topic Scoring Table ──
            st.markdown("#### 🎖️ Topic Priority Scoring Engine")
            st.markdown("<p style='color:#8b949e;font-size:0.82rem;margin-top:-10px;'>Score = 60% past-paper frequency + 40% syllabus weightage. Study in descending order.</p>", unsafe_allow_html=True)

            sorted_topics = sorted(topics, key=lambda x: x.get("priority_score", 0), reverse=True)
            for t in sorted_topics:
                score = t.get("priority_score", 0)
                name = t.get("name", "Unknown")
                freq = t.get("frequency", 0)
                trend = t.get("trend", "Stable")
                years = t.get("years_tag", "")
                pclass = priority_class(score)
                plabel = priority_label(score)
                trend_icon = "📈" if trend == "Rising" else ("📉" if trend == "Declining" else "➡️")

                st.markdown(f"""
                <div class="topic-row">
                    <div class="topic-name">{name}
                        <div style='font-size:0.75rem;color:#484f58;margin-top:2px;'>
                            {trend_icon} {trend} &nbsp;·&nbsp; Asked {freq}× &nbsp;·&nbsp; {years}
                        </div>
                    </div>
                    <div class="topic-bar-wrap">
                        <div class="topic-bar" style="width:{score}%"></div>
                    </div>
                    <div class="topic-score">{score}</div>
                    <span class="{pclass}">{plabel}</span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Study Plan ──
            st.markdown(f"#### 📅 {study_days}-Day Study Sprint")
            if study_plan:
                cols_plan = st.columns(min(len(study_plan), 4))
                for i, day in enumerate(study_plan):
                    with cols_plan[i % 4]:
                        st.markdown(f"""
                        <div class='card' style='padding:14px 16px;min-height:120px;'>
                            <div style='color:#fb8c00;font-weight:700;font-size:0.82rem;'>DAY {day.get("day", i+1)}</div>
                            <div style='color:#e6edf3;font-weight:600;margin:4px 0;font-size:0.9rem;'>{day.get("focus","")}</div>
                            <div style='color:#8b949e;font-size:0.8rem;line-height:1.6;'>{day.get("task","")}</div>
                            <div style='color:#484f58;font-size:0.76rem;margin-top:6px;'>⏱ {day.get("hours",2)}h</div>
                        </div>
                        """, unsafe_allow_html=True)

            # ── Download JSON ──
            st.markdown("<br>", unsafe_allow_html=True)
            dl1, dl2, _ = st.columns([2, 2, 3])
            with dl1:
                st.download_button(
                    "⬇️ Download Strategy JSON",
                    data=json.dumps(res, indent=2),
                    file_name="exam_strategy.json",
                    mime="application/json",
                    use_container_width=True,
                )
            with dl2:
                # Build plain-text summary
                txt_lines = ["SMART EXAM STRATEGY\n" + "=" * 40 + "\n"]
                txt_lines.append(f"KEY INSIGHT: {key_insight}\n")
                txt_lines.append("\nTOPIC PRIORITY SCORES:\n")
                for t in sorted_topics:
                    txt_lines.append(f"  [{t.get('priority_score',0):>3}] {t.get('name','')} — {t.get('trend','')}")
                txt_lines.append("\nCOVERAGE GAPS:\n  " + ", ".join(gaps))
                txt_lines.append("\nHIGH-YIELD ZONES:\n  " + ", ".join(high_yield))
                st.download_button(
                    "⬇️ Download Summary .txt",
                    data="\n".join(txt_lines),
                    file_name="exam_strategy.txt",
                    mime="text/plain",
                    use_container_width=True,
                )

# ══════════════════════════════════════════════════
#  TAB 3 — PRACTICE MODE
# ══════════════════════════════════════════════════
with tab_practice:
    if not st.session_state.strategy_done or not st.session_state.strategy_results:
        st.markdown("""
        <div style='background:#161b22;border:1px dashed #30363d;border-radius:10px;
                    padding:36px;text-align:center;color:#484f58;'>
            🧠 Run <b style='color:#8b949e;'>Strategy Analysis</b> first — practice questions will appear here.
        </div>
        """, unsafe_allow_html=True)
    else:
        res = st.session_state.strategy_results
        pq_list = res.get("practice_questions", [])
        topics = res.get("topics", [])

        st.markdown("#### 🎯 Potential Exam Questions")
        st.markdown(
            "<p style='color:#8b949e;font-size:0.88rem;margin-top:-10px;'>"
            "AI-generated questions modelled on historical exam patterns. Use these for active recall practice.</p>",
            unsafe_allow_html=True,
        )

        if not pq_list:
            st.warning("No practice questions were generated. Try re-running the analysis.")
        else:
            for pq in pq_list:
                topic_name = pq.get("topic", "Unknown Topic")
                questions = pq.get("questions", [])

                # Find priority score for this topic
                score = next(
                    (t.get("priority_score", 0) for t in topics if t.get("name", "").lower() == topic_name.lower()),
                    0,
                )
                pclass = priority_class(score)
                plabel = priority_label(score)

                with st.expander(f"📌 {topic_name}  •  Score: {score}  {plabel}", expanded=(score >= 75)):
                    st.markdown(f'<span class="{pclass}" style="margin-bottom:12px;display:inline-block;">Priority: {score}/100</span>', unsafe_allow_html=True)
                    for i, q in enumerate(questions, 1):
                        st.markdown(f"""
                        <div class="question-card">
                            <div style='display:flex;align-items:flex-start;gap:10px;'>
                                <span class="question-num">{i}</span>
                                <span style='color:#e6edf3;font-size:0.92rem;line-height:1.65;'>{q}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    # Quick tip from high-yield or gap context
                    is_gap = topic_name in res.get("coverage_gaps", [])
                    is_hy = topic_name in res.get("high_yield_zones", [])
                    if is_hy:
                        st.markdown(
                            "<div class='card-orange' style='margin-top:10px;'>"
                            "<span style='font-size:0.82rem;'>🔥 <b>High-Yield Zone</b> — this topic appears frequently across past papers. Prioritise it!</span>"
                            "</div>",
                            unsafe_allow_html=True,
                        )
                    if is_gap:
                        st.markdown(
                            "<div class='card-red' style='margin-top:10px;'>"
                            "<span style='font-size:0.82rem;'>⚠️ <b>Coverage Gap</b> — rarely asked but on the syllabus. Could be a surprise question this year.</span>"
                            "</div>",
                            unsafe_allow_html=True,
                        )

        # ── Actionable Insight Box ──
        st.markdown("<br>", unsafe_allow_html=True)
        sorted_topics = sorted(topics, key=lambda x: x.get("priority_score", 0), reverse=True)
        if sorted_topics:
            top3 = [t["name"] for t in sorted_topics[:3]]
            st.markdown(f"""
            <div class='card-green'>
                <div style='font-size:0.78rem;font-weight:700;color:#3fb950;letter-spacing:1px;'>✅ ACTIONABLE EXAM STRATEGY</div>
                <div style='color:#e6edf3;margin-top:8px;font-size:0.92rem;line-height:1.7;'>
                    Focus <b>70% of your study time</b> on these 3 topics: 
                    <b style='color:#fb8c00;'>{", ".join(top3)}</b>.<br>
                    Use the practice questions above for active recall — don't just read, write out your answers.
                    Tackle coverage gaps in the final 2 days as a surprise-question buffer.
                </div>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════
#  TAB 4 — AI CHAT
# ══════════════════════════════════════════════════
with tab_chat:
    st.markdown("### 💬 Ask questions about your material")
    st.markdown("<p style='color:#8b949e;font-size:0.88rem;margin-top:-10px;'>Chat with AI that has full context of your uploaded content.</p>", unsafe_allow_html=True)

    if not st.session_state.extracted_text:
        st.markdown("""
        <div style='background:#161b22;border:1px dashed #30363d;border-radius:10px;
                    padding:28px;text-align:center;color:#484f58;'>
            Upload and extract your PDFs in the <b style='color:#8b949e;'>Upload Papers</b> tab first — then chat here.
        </div>
        """, unsafe_allow_html=True)
    else:
        wc = len(st.session_state.extracted_text.split())
        nc = len(st.session_state.chat_messages)
        st.markdown(f"""
        <div class='context-bar'>
            <span class='context-dot'>●</span> Context loaded: <b style='color:#c9d1d9;'>{st.session_state.source_label}</b>
            &nbsp;·&nbsp; {wc:,} words &nbsp;·&nbsp; {nc} messages
        </div>
        """, unsafe_allow_html=True)

        # Quick chips
        chip_labels = [
            "What are the most important topics?",
            "Give me 5 practice questions",
            "What are the coverage gaps?",
            "What should I study first?",
            "Create a 1-page cheat sheet",
            "Quiz me on the syllabus",
            "Memory tricks for key concepts",
            "What patterns repeat across papers?",
        ]
        st.markdown("<div style='margin-bottom:8px;font-size:0.82rem;color:#8b949e;'>Quick questions:</div>", unsafe_allow_html=True)
        chip_cols = st.columns(4)
        chip_trigger = None
        for i, label in enumerate(chip_labels):
            with chip_cols[i % 4]:
                if st.button(label, key=f"chip_{i}"):
                    chip_trigger = label

        # Chat history
        if st.session_state.chat_messages:
            html = '<div class="chat-wrap">'
            for m in st.session_state.chat_messages:
                if m["role"] == "user":
                    html += f'<div class="msg-user"><div class="msg-user-bubble">{m["content"]}</div></div>'
                else:
                    body = m["content"].replace("\n", "<br>")
                    html += f'<div class="msg-ai"><div class="msg-ai-avatar">🎯</div><div class="msg-ai-bubble">{body}</div></div>'
            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty-chat">No messages yet — ask a question or pick one above.</div>', unsafe_allow_html=True)

        with st.form("chat_form", clear_on_submit=True):
            ic, bc2 = st.columns([5, 1])
            with ic:
                user_q = st.text_input(
                    "Message",
                    placeholder="Ask anything about your study material…",
                    label_visibility="collapsed",
                )
            with bc2:
                sent = st.form_submit_button("Send", use_container_width=True)

        to_ask = chip_trigger or (user_q.strip() if sent and user_q.strip() else None)

        if to_ask:
            if not groq_api_key:
                st.error("Add your Groq API key in the sidebar.")
            else:
                st.session_state.chat_messages.append({"role": "user", "content": to_ask})
                with st.spinner("Thinking…"):
                    try:
                        reply = chat_with_content(
                            to_ask,
                            st.session_state.chat_messages[:-1],
                            st.session_state.extracted_text,
                            st.session_state.source_label,
                            groq_api_key,
                            model_choice,
                        )
                        st.session_state.chat_messages.append({"role": "assistant", "content": reply})
                    except Exception as e:
                        st.error(f"Chat error: {e}")
                st.rerun()

# ══════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════
st.divider()
st.markdown("""
<div style='text-align:center;color:#484f58;font-size:0.8rem;padding:8px 0 20px;'>
    Smart Exam Strategist &nbsp;·&nbsp; Powered by Groq LLaMA 3.3 + Whisper &nbsp;·&nbsp; Built with Streamlit
</div>
""", unsafe_allow_html=True)
