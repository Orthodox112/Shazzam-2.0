"""
ui_style.py
===========
Shared CSS + small UI helper components.

Light theme, desktop-first layout: a warm paper background, deep-slate
text, and a deep teal accent (darkened from the original dark-theme teal
so it stays legible on a light background). Headings and data/numeric
values use a monospace face (the "lab notebook" identity from the
original design); body copy uses a clean grotesque sans for comfortable
reading at desktop widths. Content is capped at a max-width so wide
desktop layout doesn't stretch text edge-to-edge on large monitors.
"""
import streamlit as st

TEAL = "#0E7C70"          # deep teal accent -- legible on white, unlike #2DD4BF
TEAL_DIM = "#0B5F56"
TEAL_TINT = "#E4F2EF"     # very light teal wash for fills/highlights
BG = "#F0B31A"            # warm paper, not stark white
PANEL = "#FFFFFF"
PANEL_BORDER = "#E2DDD0"
TEXT = "#22302C"          # deep slate, not pure black
TEXT_DIM = "#73807B"
AMBER = "#B6791A"         # accent for "runner-up" style highlight numbers

FONT_DISPLAY = "'JetBrains Mono', 'IBM Plex Mono', ui-monospace, monospace"
FONT_BODY = "'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif"

MAX_WIDTH_PX = 1180


def inject_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {{
            font-family: {FONT_BODY};
        }}
        .stApp {{
            background-color: {BG};
            color: {TEXT};
        }}

        /* ---- desktop content width cap ---- */
        .block-container {{
            max-width: {MAX_WIDTH_PX}px;
            padding-top: 4rem;
            padding-left: 3rem;
            padding-right: 3rem;
            margin: 0 auto;
        }}

        /* ---- hide Streamlit's default top toolbar/header that overlaps content ---- */
        header[data-testid="stHeader"] {{
            background: transparent;
        }}
        #MainMenu {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}

        /* ---- header ---- */
        .ee-header {{
            display: flex;
            align-items: center;
            gap: 14px;
            margin-bottom: 0px;
        }}
        .ee-logo {{
            width: 52px; height: 52px;
            border-radius: 12px;
            background: linear-gradient(160deg, {TEAL_TINT}, #d7ece8);
            border: 1px solid {PANEL_BORDER};
            display: flex; align-items: center; justify-content: center;
            color: {TEAL}; font-size: 24px;
            font-family: {FONT_DISPLAY};
        }}
        .ee-title {{
            font-family: {FONT_DISPLAY};
            font-size: 34px; font-weight: 800; color: {TEXT}; margin: 0;
            letter-spacing: -0.5px;
        }}
        .ee-title span {{ color: {TEAL}; }}
        .ee-subtitle {{
            color: {TEXT_DIM}; font-size: 12px; letter-spacing: 2px;
            text-transform: uppercase; margin-top: 2px;
            font-family: {FONT_DISPLAY};
        }}
        .ee-tagline {{
            color: {TEXT_DIM}; font-size: 14.5px; margin: 10px 0 18px 0;
        }}

        /* ---- section eyebrow ---- */
        .ee-eyebrow {{
            color: {TEAL}; letter-spacing: 2px; font-size: 11px;
            text-transform: uppercase; margin-bottom: 2px;
            font-family: {FONT_DISPLAY}; font-weight: 600;
        }}

        /* ---- pipeline timing chips ---- */
        .chip-row {{ display: flex; gap: 10px; flex-wrap: wrap; margin: 14px 0; align-items: center; }}
        .chip {{
            background: {PANEL};
            border: 1px solid {PANEL_BORDER};
            border-radius: 10px;
            padding: 10px 16px;
            min-width: 116px;
            text-align: center;
            box-shadow: 0 1px 2px rgba(34,48,44,0.04);
        }}
        .chip .num {{
            color: {TEAL}; font-size: 11px; letter-spacing: 1px;
            font-family: {FONT_DISPLAY};
        }}
        .chip .label {{
            color: {TEXT_DIM}; font-size: 10px; letter-spacing: 1px;
            text-transform: uppercase; margin-top: 2px;
            font-family: {FONT_DISPLAY};
        }}
        .chip .value {{
            color: {TEXT}; font-size: 16px; font-weight: 700; margin-top: 4px;
            font-family: {FONT_DISPLAY};
        }}
        .chip .sub {{
            color: {TEXT_DIM}; font-size: 10px; margin-top: 2px;
        }}
        .chip-total {{
            margin-left: auto; align-self: center; color: {TEAL};
            font-size: 13px; font-family: {FONT_DISPLAY}; font-weight: 600;
        }}

        /* ---- match found panel ---- */
        .match-panel {{
            border: 1px solid {TEAL};
            background: linear-gradient(180deg, {TEAL_TINT}, #ffffff);
            border-radius: 14px;
            padding: 22px 26px;
            margin: 16px 0;
        }}
        .match-panel .tag {{
            color: {TEAL}; font-size: 11px; letter-spacing: 2px;
            text-transform: uppercase; font-family: {FONT_DISPLAY}; font-weight: 600;
        }}
        .match-panel .song {{
            font-family: {FONT_DISPLAY};
            font-size: 34px; font-weight: 800; color: {TEXT}; margin: 4px 0;
        }}
        .match-panel .meta {{
            color: {TEXT_DIM}; font-size: 13px;
        }}
        .match-panel .meta b {{ color: {AMBER}; }}
        .match-panel.no-match {{
            border-color: #C97A6B;
            background: linear-gradient(180deg, #FBEAE6, #ffffff);
        }}
        .match-panel.no-match .tag {{ color: #B5564A; }}

        /* ---- candidate score bars ---- */
        .cand-row {{
            display: flex; align-items: center; gap: 12px;
            padding: 6px 0; font-size: 13px;
        }}
        .cand-name {{ width: 220px; color: {TEXT}; flex-shrink: 0; }}
        .cand-bar-bg {{
            flex: 1; background: #ECE7DA; border-radius: 6px; height: 10px;
            overflow: hidden;
        }}
        .cand-bar-fill {{
            background: linear-gradient(90deg, {TEAL_DIM}, {TEAL});
            height: 100%;
        }}
        .cand-score {{
            width: 50px; text-align: right; color: {TEXT_DIM};
            font-family: {FONT_DISPLAY};
        }}

        /* ---- step header ---- */
        .step-block {{
            border-left: 2px solid {TEAL};
            padding-left: 16px;
            margin: 26px 0 14px 0;
        }}
        .step-eyebrow {{
            color: {TEAL}; font-size: 11px; letter-spacing: 2px;
            text-transform: uppercase; font-family: {FONT_DISPLAY}; font-weight: 600;
        }}
        .step-title {{ font-size: 19px; font-weight: 700; color: {TEXT}; margin: 2px 0 6px 0; }}
        .step-desc {{ color: {TEXT_DIM}; font-size: 13.5px; line-height: 1.6; }}
        .step-desc b {{ color: {TEAL}; }}

        /* ---- library grid cards ---- */
        .song-card {{
            background: {PANEL};
            border: 1px solid {PANEL_BORDER};
            border-radius: 10px;
            padding: 10px 12px;
            margin-bottom: 10px;
            box-shadow: 0 1px 2px rgba(34,48,44,0.04);
        }}
        .song-card .name {{ color: {TEXT}; font-size: 13px; font-weight: 600; }}
        .song-card .hashes {{
            color: {TEAL}; font-size: 11px; margin-top: 2px;
            font-family: {FONT_DISPLAY};
        }}

        /* ---- misc ---- */
        .dim {{ color: {TEXT_DIM}; }}
        .teal {{ color: {TEAL}; }}
        code {{ color: {TEAL_DIM} !important; background: {TEAL_TINT} !important; }}

        section[data-testid="stSidebar"] {{ display: none; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def header():
    st.markdown(
        f"""
        <div class="ee-header">
            <div class="ee-logo">&#9834;</div>
            <div>
                <p class="ee-title">EE<span>200</span>: Audio Fingerprinting</p>
                <p class="ee-subtitle">Signals, Systems &amp; Networks</p>
            </div>
        </div>
        <p class="ee-tagline">Index a library of songs as spectrogram fingerprints, then identify any short clip against it.</p>
        """,
        unsafe_allow_html=True,
    )


def timing_chips(timings_ms: dict, extra_subs: dict | None = None):
    """Render the 5-stage pipeline timing chips like the demo video:
    Spectrogram / Constellation / Hashing / DB Lookup / Scoring."""
    extra_subs = extra_subs or {}
    stages = [
        ("1", "spectrogram", "SPECTROGRAM"),
        ("2", "constellation", "CONSTELLATION"),
        ("3", "hashing", "HASHING"),
        ("4", "db_lookup", "DB LOOKUP"),
        ("5", "scoring", "SCORING"),
    ]
    total = sum(timings_ms.get(k, 0) for _, k, _ in stages)
    chips_html = ""
    for num, key, label in stages:
        val = timings_ms.get(key, 0)
        sub = extra_subs.get(key, "")
        chips_html += f"""
        <div class="chip">
            <div class="num">&#9312;{num}</div>
            <div class="label">{label}</div>
            <div class="value">{val:.0f} ms</div>
            <div class="sub">{sub}</div>
        </div>
        """
    st.markdown(
        f'<div class="chip-row">{chips_html}<div class="chip-total">total {total:.0f} ms</div></div>',
        unsafe_allow_html=True,
    )


def match_panel(song_name: str, score: int, runner_up_ratio: float, is_match: bool):
    if is_match:
        ratio_str = "&#8734;" if runner_up_ratio == float("inf") else f"{runner_up_ratio:.0f}&times;"
        st.markdown(
            f"""
            <div class="match-panel">
                <div class="tag">&#9679; Match Found</div>
                <div class="song">{song_name}</div>
                <div class="meta">cluster score <b>{score}</b> &middot; {ratio_str} the runner-up</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="match-panel no-match">
                <div class="tag">&#9679; No Confident Match</div>
                <div class="song">none</div>
                <div class="meta">best candidate scored only <b>{score}</b> votes &mdash; below the confidence threshold</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def candidate_scores(scores: list[tuple[str, int]], top_n: int = 5):
    if not scores:
        st.markdown('<p class="dim">No candidate songs received any votes.</p>', unsafe_allow_html=True)
        return
    top = scores[:top_n]
    max_score = max(s for _, s in top) or 1
    rows_html = ""
    for name, score in top:
        pct = max(2, int(100 * score / max_score))
        rows_html += f"""
        <div class="cand-row">
            <div class="cand-name">{name}</div>
            <div class="cand-bar-bg"><div class="cand-bar-fill" style="width:{pct}%"></div></div>
            <div class="cand-score">{score}</div>
        </div>
        """
    st.markdown(rows_html, unsafe_allow_html=True)


def step_block(eyebrow: str, title: str, desc_html: str):
    st.markdown(
        f"""
        <div class="step-block">
            <div class="step-eyebrow">{eyebrow}</div>
            <div class="step-title">{title}</div>
            <div class="step-desc">{desc_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
