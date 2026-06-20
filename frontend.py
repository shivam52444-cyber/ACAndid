import streamlit as st
import tempfile
import os
from textwrap import dedent
from logger import setup_logger
setup_logger()

from app import run_pipeline


def render_html_block(html: str) -> None:
    st.markdown(dedent(html).strip(), unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="CandidateX — AI Evaluator",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── RESET & BASE ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: #08111E !important;
    color: #E8EDF5 !important;
    font-family: 'Inter', sans-serif;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { display: none; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0D1B2A; }
::-webkit-scrollbar-thumb { background: #00D4FF44; border-radius: 4px; }

/* ── INPUTS ── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: #0D1B2A !important;
    border: 1px solid #1E3050 !important;
    border-radius: 10px !important;
    color: #E8EDF5 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    padding: 12px 16px !important;
    transition: border-color 0.25s, box-shadow 0.25s;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: #00D4FF !important;
    box-shadow: 0 0 0 3px #00D4FF22 !important;
    outline: none !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder { color: #3A5070 !important; }

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] {
    background: #0D1B2A !important;
    border: 1px dashed #1E3050 !important;
    border-radius: 10px !important;
    transition: border-color 0.25s;
}
[data-testid="stFileUploader"]:hover { border-color: #00D4FF88 !important; }
[data-testid="stFileUploader"] * { color: #7090B0 !important; }

/* ── LABELS ── */
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label,
[data-testid="stFileUploader"] label {
    color: #7EAED0 !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 1.2px !important;
    text-transform: uppercase !important;
    margin-bottom: 6px !important;
}

/* ── BUTTON ── */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #00D4FF, #0099DD) !important;
    color: #08111E !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    letter-spacing: 0.5px !important;
    padding: 14px 32px !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: opacity 0.2s, transform 0.15s, box-shadow 0.2s !important;
    box-shadow: 0 4px 20px #00D4FF33 !important;
}
[data-testid="stButton"] > button:hover {
    opacity: 0.92 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 28px #00D4FF55 !important;
}
[data-testid="stButton"] > button:active { transform: translateY(0) !important; }

/* ── SPINNER ── */
[data-testid="stSpinner"] { color: #00D4FF !important; }

/* ── PROGRESS BAR ── */
[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #00D4FF, #00E676) !important;
    border-radius: 4px !important;
    transition: width 0.6s cubic-bezier(0.4,0,0.2,1) !important;
}
[data-testid="stProgressBar"] > div {
    background: #1E2A3A !important;
    border-radius: 4px !important;
}

/* ── ALERTS ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    border-left-width: 3px !important;
    font-size: 13px !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HERO HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div style="
    background: linear-gradient(180deg, #0D1B2A 0%, #08111E 100%);
    border-bottom: 1px solid #1E3050;
    padding: 28px 48px 24px;
    display: flex;
    align-items: center;
    gap: 16px;
">
    <div style="
        width: 42px; height: 42px;
        background: linear-gradient(135deg, #00D4FF, #0066AA);
        border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 20px;
        box-shadow: 0 4px 16px #00D4FF44;
        flex-shrink: 0;
    ">⚡</div>
    <div>
        <div style="font-family:'JetBrains Mono',monospace; font-size:22px; font-weight:600; color:#E8EDF5; letter-spacing:-0.5px;">
            CandidateX
            <span style="color:#00D4FF;">.</span>
        </div>
        <div style="font-size:12px; color:#3A6080; letter-spacing:1px; text-transform:uppercase; margin-top:1px;">
            AI-Powered Resume &amp; GitHub Evaluator
        </div>
    </div>
    <div style="margin-left:auto; font-family:'JetBrains Mono',monospace; font-size:11px; color:#1E4060; letter-spacing:2px;">
        v2.0 · LIVE
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MAIN LAYOUT
# ─────────────────────────────────────────────
st.markdown('<div style="padding: 32px 48px;">', unsafe_allow_html=True)

left_col, gap_col, right_col = st.columns([5, 0.3, 6])

# ══════════════════════════════════════════════
# LEFT — INPUTS
# ══════════════════════════════════════════════
with left_col:
    st.markdown("""
    <div style="margin-bottom:24px;">
        <div style="font-size:11px; color:#3A6080; letter-spacing:2px; text-transform:uppercase; margin-bottom:6px;">
            01 / CANDIDATE INPUT
        </div>
        <div style="font-size:20px; font-weight:600; color:#E8EDF5;">
            Evaluate a candidate
        </div>
        <div style="font-size:13px; color:#4A7090; margin-top:6px; line-height:1.6;">
            Upload a résumé, paste a job description, and link a GitHub repo.<br>
            The AI will analyze code quality, documentation, and fit score.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Card wrapper
    st.markdown("""
    <div style="
        background: #0D1B2A;
        border: 1px solid #1A2E45;
        border-radius: 16px;
        padding: 28px;
    ">
    """, unsafe_allow_html=True)

    resume_file = st.file_uploader("Resume (PDF only)", type=["pdf"])

    st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)

    jd_text = st.text_area(
        "Job Description",
        height=180,
        placeholder="Paste the full job description here — the more detail, the better the match analysis..."
    )

    st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)

    repo_url = st.text_input(
        "GitHub Repository URL",
        placeholder="https://github.com/username/repo"
    )

    st.markdown('<div style="height:24px;"></div>', unsafe_allow_html=True)

    # Checklist
    checks = {
        "résumé": bool(resume_file),
        "job description": bool(jd_text and jd_text.strip()),
        "GitHub URL": bool(repo_url and repo_url.strip()),
    }
    check_html = ""
    for label, done in checks.items():
        color = "#00E676" if done else "#1E3A50"
        icon  = "✓" if done else "○"
        text_color = "#C0D8E8" if done else "#2E5070"
        check_html += f"""
        <div style="display:flex;align-items:center;gap:10px;padding:6px 0;">
            <span style="font-family:'JetBrains Mono',monospace;font-size:13px;color:{color};width:16px;">{icon}</span>
            <span style="font-size:13px;color:{text_color};">{label.title()} provided</span>
        </div>"""

    st.markdown(f"""
    <div style="
        background:#081420;
        border:1px solid #1A2E45;
        border-radius:10px;
        padding:14px 18px;
        margin-bottom:20px;
    ">{check_html}</div>
    """, unsafe_allow_html=True)

    evaluate_btn = st.button("⚡ Run Evaluation", disabled=not all(checks.values()))
    st.markdown('</div>', unsafe_allow_html=True)  # close card

# ══════════════════════════════════════════════
# RIGHT — RESULTS PANEL
# ══════════════════════════════════════════════
with right_col:
    st.markdown("""
    <div style="margin-bottom:24px;">
        <div style="font-size:11px; color:#3A6080; letter-spacing:2px; text-transform:uppercase; margin-bottom:6px;">
            02 / ANALYSIS OUTPUT
        </div>
        <div style="font-size:20px; font-weight:600; color:#E8EDF5;">
            Evaluation results
        </div>
        <div style="font-size:13px; color:#4A7090; margin-top:6px;">
            Results appear here after the pipeline completes.
        </div>
    </div>
    """, unsafe_allow_html=True)

    results_placeholder = st.empty()

    if not evaluate_btn:
        results_placeholder.markdown("""
        <div style="
            background: #0D1B2A;
            border: 1px dashed #1A2E45;
            border-radius: 16px;
            padding: 60px 40px;
            text-align: center;
            min-height: 480px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        ">
            <div style="font-size:48px; margin-bottom:16px; opacity:0.2;">📊</div>
            <div style="font-family:'JetBrains Mono',monospace; font-size:13px; color:#1E4060; letter-spacing:2px; text-transform:uppercase;">
                AWAITING EVALUATION
            </div>
            <div style="font-size:12px; color:#1A3050; margin-top:10px;">
                Fill in all fields and click Run Evaluation
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PIPELINE EXECUTION
# ─────────────────────────────────────────────
if evaluate_btn:
    with right_col:
        results_placeholder.empty()

        # ── Live progress terminal ──
        terminal = st.empty()
        prog_bar  = st.progress(0)
        log_lines = []

        def show_terminal(lines, step_label=""):
            log_html = "\n".join(
                f'<div style="margin:2px 0;"><span style="color:#3A6080;">[{i+1:02d}]</span> '
                f'<span style="color:#7EC8E3;">{ln}</span></div>'
                for i, ln in enumerate(lines)
            )
            terminal.markdown(f"""
            <div style="
                background:#040E18;
                border:1px solid #0D2030;
                border-radius:12px;
                padding:20px 24px;
                font-family:'JetBrains Mono',monospace;
                font-size:12px;
                line-height:1.7;
                min-height:140px;
            ">
                <div style="color:#1E4060;font-size:10px;letter-spacing:2px;margin-bottom:12px;">
                    ● PIPELINE LOG {'— ' + step_label if step_label else ''}
                </div>
                {log_html}
                <div style="color:#00D4FF;margin-top:8px;animation:blink 1s step-end infinite;">▋</div>
            </div>
            """, unsafe_allow_html=True)

        # Step 1
        log_lines.append("Saving resume to temp storage...")
        show_terminal(log_lines, "RESUME UPLOAD")
        prog_bar.progress(8)

        resume_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(resume_file.read())
                resume_path = tmp.name
            log_lines.append(f"✓ Resume saved → {os.path.basename(resume_path)}")

            # Step 2
            log_lines.append("Cloning GitHub repository (shallow, depth=1)...")
            show_terminal(log_lines, "CLONING REPO")
            prog_bar.progress(22)

            # Step 3
            log_lines.append("Building dependency graph...")
            show_terminal(log_lines, "STATIC ANALYSIS")
            prog_bar.progress(38)

            # Step 4
            log_lines.append("Chunking code files by function boundaries...")
            log_lines.append("Chunking documentation & config files...")
            show_terminal(log_lines, "CHUNKING")
            prog_bar.progress(52)

            # Step 5
            log_lines.append("Generating BAAI/MiniLM embeddings...")
            show_terminal(log_lines, "EMBEDDING")
            prog_bar.progress(66)

            # Step 6
            log_lines.append("Scoring chunks via cosine similarity...")
            log_lines.append("Scoring résumé via BM25 + cosine hybrid...")
            show_terminal(log_lines, "SCORING")
            prog_bar.progress(80)

            # Step 7
            log_lines.append("Calling LLaMA 3.3-70B via Groq for reasoning...")
            show_terminal(log_lines, "LLM EVALUATION")
            prog_bar.progress(90)

            # ── ACTUAL CALL ──
            result = run_pipeline(
                resume_path=resume_path,
                jd=jd_text,
                repo_url=repo_url
            )

            log_lines.append("✓ Pipeline completed successfully.")
            show_terminal(log_lines, "DONE")
            prog_bar.progress(100)

            # ── CLEAR TERMINAL ──
            terminal.empty()
            prog_bar.empty()

            # ─────────────────────────────────────────
            # RESULTS UI
            # ─────────────────────────────────────────
            final  = result["final_score"]
            resume = result["resume_score"]
            code   = result["code_score"]
            doc    = result["doc_score"]
            llm    = result["llm_score"]

            # score → color mapping
            def score_color(s):
                if s >= 0.7: return "#00E676"
                if s >= 0.45: return "#FFD600"
                return "#FF4D6D"

            def score_label(s):
                if s >= 0.7: return "STRONG"
                if s >= 0.45: return "MODERATE"
                return "WEAK"

            # ── FINAL SCORE HERO ──
            fc = score_color(final)
            fl = score_label(final)
            pct = int(final * 100)

            # SVG donut
            radius = 52
            circ   = 2 * 3.14159 * radius
            dash   = circ * final
            gap    = circ - dash

            st.markdown(f"""
            <div style="
                background: #0D1B2A;
                border: 1px solid #1A2E45;
                border-radius: 16px;
                padding: 28px 32px;
                margin-bottom: 16px;
                display: flex;
                align-items: center;
                gap: 32px;
            ">
                <!-- SVG RING -->
                <div style="flex-shrink:0;">
                <svg width="130" height="130" viewBox="0 0 130 130">
                    <defs>
                        <linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stop-color="{fc}"/>
                            <stop offset="100%" stop-color="{fc}88"/>
                        </linearGradient>
                    </defs>
                    <!-- track -->
                    <circle cx="65" cy="65" r="{radius}"
                        fill="none" stroke="#1A2E45" stroke-width="10"/>
                    <!-- progress -->
                    <circle cx="65" cy="65" r="{radius}"
                        fill="none"
                        stroke="url(#ringGrad)"
                        stroke-width="10"
                        stroke-linecap="round"
                        stroke-dasharray="{dash:.1f} {gap:.1f}"
                        stroke-dashoffset="{circ/4:.1f}"
                        transform="rotate(-90 65 65)"
                        style="filter:drop-shadow(0 0 6px {fc}88)"/>
                    <!-- label -->
                    <text x="65" y="58" text-anchor="middle"
                        font-family="JetBrains Mono, monospace"
                        font-size="22" font-weight="600" fill="{fc}">{pct}</text>
                    <text x="65" y="74" text-anchor="middle"
                        font-family="Inter, sans-serif"
                        font-size="9" fill="#3A6080" letter-spacing="2">OVERALL</text>
                </svg>
                </div>
                <!-- TEXT -->
                <div>
                    <div style="font-size:11px;color:#3A6080;letter-spacing:2px;text-transform:uppercase;margin-bottom:6px;">
                        Final Evaluation Score
                    </div>
                    <div style="font-size:32px;font-weight:700;color:{fc};font-family:'JetBrains Mono',monospace;line-height:1;">
                        {final:.2f}
                        <span style="font-size:14px;color:#3A6080;font-weight:400;margin-left:6px;">/ 1.00</span>
                    </div>
                    <div style="
                        display:inline-block;
                        margin-top:10px;
                        background:{fc}22;
                        border:1px solid {fc}44;
                        color:{fc};
                        font-size:11px;
                        font-weight:700;
                        letter-spacing:2px;
                        padding:4px 12px;
                        border-radius:6px;
                    ">{fl} MATCH</div>
                    <div style="font-size:12px;color:#3A6080;margin-top:10px;">
                        Weighted across résumé · code · docs · LLM reasoning
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── SCORE BREAKDOWN BARS ──
            breakdown = [
                ("Résumé Match",     resume, "20%", "#00D4FF"),
                ("Code Similarity",  code,   "30%", "#BD00FF"),
                ("Doc Similarity",   doc,    "10%", "#FF8C00"),
                ("LLM Evaluation",   llm,    "40%", "#00E676"),
            ]

            bars_html = ""
            for label, val, weight, color in breakdown:
                pct_w = int(val * 100)
                bars_html += dedent(f"""
                    <div style="margin-bottom:16px;">
                        <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px;">
                            <span style="font-size:12px;color:#7090B0;">{label}</span>
                            <div style="display:flex;gap:12px;align-items:baseline;">
                                <span style="font-size:10px;color:#2A4060;letter-spacing:1px;">weight {weight}</span>
                                <span style="font-family:'JetBrains Mono',monospace;font-size:13px;font-weight:600;color:{color};">{val:.2f}</span>
                            </div>
                        </div>
                        <div style="background:#0A1828;border-radius:6px;height:7px;overflow:hidden;">
                            <div style="
                                width:{pct_w}%;
                                height:100%;
                                background:linear-gradient(90deg,{color},{color}88);
                                border-radius:6px;
                                box-shadow:0 0 8px {color}55;
                                transition:width 1s cubic-bezier(0.4,0,0.2,1);
                            "></div>
                        </div>
                    </div>
                """).strip()

            render_html_block(f"""
                <div style="
                    background:#0D1B2A;
                    border:1px solid #1A2E45;
                    border-radius:16px;
                    padding:24px 28px;
                    margin-bottom:16px;
                ">
                    <div style="font-size:11px;color:#3A6080;letter-spacing:2px;text-transform:uppercase;margin-bottom:18px;">
                        Score Breakdown
                    </div>
                    {bars_html}
                </div>
            """)

            # ── STRENGTHS & GAPS ──
            strengths = result.get("strengths", [])
            gaps      = result.get("gaps", [])

            def pill_list(items, color, icon):
                if not items:
                    return f'<div style="font-size:12px;color:#2A4060;font-style:italic;">None identified</div>'
                return "".join(
                    f'<div style="display:flex;align-items:flex-start;gap:10px;padding:8px 0;border-bottom:1px solid #0D2030;">'
                    f'<span style="color:{color};font-size:13px;flex-shrink:0;margin-top:1px;">{icon}</span>'
                    f'<span style="font-size:13px;color:#B0C8D8;line-height:1.5;">{item}</span>'
                    f'</div>'
                    for item in items
                )

            sg_html = f"""
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px;">
                <div style="
                    background:#0D1B2A;
                    border:1px solid #1A3030;
                    border-top:2px solid #00E676;
                    border-radius:16px;
                    padding:22px;
                ">
                    <div style="font-size:11px;color:#3A6060;letter-spacing:2px;text-transform:uppercase;margin-bottom:14px;">
                        ✦ Strengths ({len(strengths)})
                    </div>
                    {pill_list(strengths, '#00E676', '✓')}
                </div>
                <div style="
                    background:#0D1B2A;
                    border:1px solid #301A1A;
                    border-top:2px solid #FF4D6D;
                    border-radius:16px;
                    padding:22px;
                ">
                    <div style="font-size:11px;color:#604040;letter-spacing:2px;text-transform:uppercase;margin-bottom:14px;">
                        ⚠ Gaps ({len(gaps)})
                    </div>
                    {pill_list(gaps, '#FF4D6D', '✗')}
                </div>
            </div>
            """
            st.markdown(sg_html, unsafe_allow_html=True)

            # ── REASONING ──
            reasoning = result.get("reasoning", "")
            if reasoning:
                st.markdown(f"""
                <div style="
                    background:#040E18;
                    border:1px solid #0D2030;
                    border-left:3px solid #00D4FF;
                    border-radius:12px;
                    padding:20px 24px;
                ">
                    <div style="font-size:11px;color:#2A5070;letter-spacing:2px;text-transform:uppercase;margin-bottom:12px;">
                        🧠 LLM Reasoning
                    </div>
                    <div style="font-size:13px;color:#8AAABB;line-height:1.75;">
                        {reasoning}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        except Exception as e:
            terminal.empty()
            prog_bar.empty()
            st.markdown(f"""
            <div style="
                background:#180808;
                border:1px solid #401010;
                border-left:3px solid #FF4D6D;
                border-radius:12px;
                padding:20px 24px;
            ">
                <div style="font-size:11px;color:#602020;letter-spacing:2px;text-transform:uppercase;margin-bottom:10px;">
                    ✗ Pipeline Error
                </div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:13px;color:#FF7080;">
                    {str(e)}
                </div>
            </div>
            """, unsafe_allow_html=True)

        finally:
            if resume_path and os.path.exists(resume_path):
                os.remove(resume_path)

st.markdown('</div>', unsafe_allow_html=True)  # close main padding div
