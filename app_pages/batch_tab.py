import io
import csv
import streamlit as st

from fingerprint.audio_io import load_audio
from fingerprint.matcher import match_clip, predicted_label
from fingerprint import config


def _build_csv(rows):
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["filename", "prediction"])
    for filename, prediction in rows:
        writer.writerow([filename, prediction])
    return buf.getvalue()


def render(db):
    st.markdown('<p class="ee-eyebrow">Batch</p>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:22px; font-weight:700; margin:2px 0 10px 0;">Identify many clips at once</p>',
                unsafe_allow_html=True)

    st.markdown(
        '<p class="dim" style="font-size:13.5px; line-height:1.6;">'
        'Upload a set of query clips. Each is identified against the '
        '<b style="color:#E6F1EE;">currently indexed library</b>, '
        'and the results are written to a standardized <code>results.csv</code> with '
        'columns <code>filename, prediction</code>. The <code>prediction</code> is the matched '
        "track's filename without extension, or <code>none</code> when no candidate clears the "
        'confidence threshold.</p>',
        unsafe_allow_html=True,
    )

    if db.n_songs() == 0:
        st.warning("No songs are indexed yet. Run `python build_database.py` first.")
        return

    uploaded_files = st.file_uploader(
        "Upload",
        type=[e.lstrip(".") for e in config.SUPPORTED_EXTS],
        accept_multiple_files=True,
        help="200MB per file · WAV, MP3, FLAC, OGG, M4A",
        label_visibility="collapsed",
    )
    st.markdown(
        '<p class="dim" style="font-size:12px; margin-top:-12px;">200MB per file &middot; WAV, MP3, FLAC, OGG, M4A</p>',
        unsafe_allow_html=True,
    )

    if uploaded_files:
        chips = "".join(
            f'<span style="display:inline-flex; align-items:center; gap:6px; '
            f'background:#121817; border:1px solid #1E2A28; border-radius:8px; '
            f'padding:6px 12px; margin:4px; font-size:12px;">&#9834; {f.name} '
            f'<span class="dim">{f.size/1e6:.1f}MB</span></span>'
            for f in uploaded_files
        )
        st.markdown(chips, unsafe_allow_html=True)

    run = st.button("Run batch", type="primary", disabled=not uploaded_files)

    if run and uploaded_files:
        progress = st.progress(0.0, text=f"Identifying ... 0/{len(uploaded_files)}")
        rows = []
        display_rows = []
        for i, f in enumerate(uploaded_files):
            y, sr = load_audio(f)
            result = match_clip(y, sr, db)
            label = predicted_label(result, db)
            rows.append((f.name, label))
            display_name = db.songs[label]["filename"] if label != "none" else "none"
            display_rows.append({"file": f.name, "prediction": display_name})
            progress.progress(
                (i + 1) / len(uploaded_files),
                text=f"Identifying ... {i + 1}/{len(uploaded_files)}",
            )
        st.session_state["batch_rows"] = rows
        st.session_state["batch_display"] = display_rows
        progress.empty()

    if "batch_display" in st.session_state:
        st.markdown('<p class="ee-eyebrow" style="margin-top:24px;">Results</p>', unsafe_allow_html=True)
        rows = st.session_state["batch_display"]

        header_html = (
            '<div style="display:flex; font-size:11px; letter-spacing:1px; '
            'color:#7C8C89; padding:8px 4px; border-bottom:1px solid #1E2A28;">'
            '<div style="flex:1;">FILE</div><div style="flex:1;">PREDICTION</div></div>'
        )
        body_html = ""
        for r in rows:
            color = "#2DD4BF" if r["prediction"] != "none" else "#7C8C89"
            body_html += (
                f'<div style="display:flex; font-size:13px; padding:8px 4px; '
                f'border-bottom:1px solid #161e1c;">'
                f'<div style="flex:1; color:#E6F1EE;">{r["file"]}</div>'
                f'<div style="flex:1; color:{color};">{r["prediction"]}</div></div>'
            )
        st.markdown(header_html + body_html, unsafe_allow_html=True)

        n_matched = sum(1 for r in rows if r["prediction"] != "none")
        st.markdown(
            f'<p class="dim" style="margin-top:10px; font-size:12.5px;">'
            f'{n_matched}/{len(rows)} clips matched a track (rest: none).</p>',
            unsafe_allow_html=True,
        )

        csv_text = _build_csv(st.session_state["batch_rows"])
        st.download_button(
            "Download results.csv",
            data=csv_text,
            file_name="results.csv",
            mime="text/csv",
            type="primary",
        )
