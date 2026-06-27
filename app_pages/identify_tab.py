import os
import glob
import streamlit as st

from fingerprint.audio_io import load_audio
from fingerprint.matcher import match_clip, predicted_label
from fingerprint import config
from app_pages import ui_style, plots


SAMPLES_DIR = "data/samples"


def _list_samples():
    if not os.path.isdir(SAMPLES_DIR):
        return []
    files = []
    for ext in config.SUPPORTED_EXTS:
        files.extend(glob.glob(os.path.join(SAMPLES_DIR, f"*{ext}")))
    return sorted(files)


def _run_identification(y, sr, db, use_single_peaks=False):
    with st.spinner("Fingerprinting clip and searching the database..."):
        result = match_clip(y, sr, db, use_single_peaks=use_single_peaks)
    return result


def _render_result(result, db, use_single_peaks=False):
    label = predicted_label(result, db)
    display_name = (
        db.songs[label]["filename"].rsplit(".", 1)[0] if label != "none" else "none"
    )

    # # ---- Step 0: pipeline timing chips -----------------------------------
    fp = result.fingerprint
    query_hashes = fp.single_peak_hashes if use_single_peaks else fp.hashes
    lookup_index = db.single_index if use_single_peaks else db.index
    #extra_subs = {
    #     "spectrogram": f"{fp.shape[0]}×{fp.shape[1]}" if fp.shape else "",
    #     "constellation": f"{len(fp.peaks)} peaks",
    #     "hashing": f"{len(query_hashes):,} hashes",
    #     "db_lookup": f"{db.n_songs()} tracks",
    #     "scoring": f"offset {result.best_offset}" if result.best_offset is not None else "",
    # }
    #ui_style.timing_chips(result.timings_ms, extra_subs)

    # ---- MATCH FOUND / no match panel -------------------------------------
    ui_style.match_panel(
        display_name, result.best_score, result.runner_up_ratio, result.is_match
    )

    # ---- candidate scores ---------------------------------------------
    st.markdown('<p class="ee-eyebrow" style="margin-top:18px;">Candidate Scores</p>', unsafe_allow_html=True)
    ui_style.candidate_scores(result.candidate_scores, top_n=5)

    # ---- Step 1: spectrogram -> constellation ---------------------------
    ui_style.step_block(
        "Step 1 &middot; Feature Extraction",
        "From spectrogram to constellation",
        f"The clip was converted into a time-frequency map (left); brighter means "
        f"louder at that frequency and moment. From that rich image, only the "
        f"<b>{len(fp.peaks)} most prominent peaks</b> were kept (right). Discarding "
        f"amplitude and phase makes the fingerprint robust to EQ, volume changes, and mild noise.",
    )
    c1, c2 = st.columns(2)
    with c1:
        st.pyplot(plots.plot_spectrogram(fp.freq_axis, fp.time_axis, fp.S_db, title="query spectrogram"),
                   use_container_width=True)
    with c2:
        st.pyplot(plots.plot_constellation(fp.peaks_hz_sec, n_peaks=len(fp.peaks)),
                   use_container_width=True)

    # ---- Step 2: database search / offset histogram ----------------------
    if result.best_song_id is not None:
        best_hist = {}
        # Recompute just the winning song's histogram for plotting
        # (matcher already discarded per-offset detail to keep memory low,
        # so we rebuild it cheaply here from the same query hashes).
        for hash_key, q_time in query_hashes:
            postings = lookup_index.get(hash_key)
            if not postings:
                continue
            for song_id, db_time in postings:
                if song_id != result.best_song_id:
                    continue
                offset = db_time - q_time
                best_hist[offset] = best_hist.get(offset, 0) + 1

        winner_meta = db.songs.get(result.best_song_id, {})
        ui_style.step_block(
            "Step 2 &middot; Database Search",
            "Where in the song?",
            f"The <b>{result.n_hashes_matched_total:,} fingerprint hashes</b> "
            f"looked up against every indexed track. Below is the full offset "
            f"histogram for the top candidate: each bar is a (song, time-gap) "
            f"that received at least one vote. The highlighted bar is exactly "
            f"where the query clip sits inside the candidate song.",
        )
        st.pyplot(
            plots.plot_offset_histogram(best_hist, best_offset=result.best_offset),
            use_container_width=True,
        )
    st.markdown("<br>", unsafe_allow_html=True)


def render(db):
    st.markdown('<p class="ee-eyebrow">Search</p>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:22px; font-weight:700; margin:2px 0 14px 0;">Identify a clip</p>',
                unsafe_allow_html=True)

    if db.n_songs() == 0:
        st.warning(
            "No songs are indexed yet. Run `python build_database.py` first, "
            "then reload this app."
        )
        return

    uploaded = st.file_uploader(
        "Upload",
        type=[e.lstrip(".") for e in config.SUPPORTED_EXTS],
        help="200MB per file · WAV, MP3, FLAC, OGG, M4A",
        label_visibility="collapsed",
    )
    st.markdown(
        '<p class="dim" style="font-size:12px; margin-top:-12px;">200MB per file &middot; WAV, MP3, FLAC, OGG, M4A</p>',
        unsafe_allow_html=True,
    )

    chosen_path = None
    samples = _list_samples()
    if samples:
        st.markdown('<p class="dim" style="letter-spacing:1px; margin-top:18px;">OR TRY A SAMPLE</p>',
                    unsafe_allow_html=True)
        for path in samples:
            name = os.path.splitext(os.path.basename(path))[0]
            c1, c2, c3 = st.columns([2, 7, 1.2])
            with c1:
                st.markdown(f'<div style="padding-top:10px;">{name}</div>', unsafe_allow_html=True)
            with c2:
                st.audio(path)
            with c3:
                if st.button("Try", key=f"try_{name}"):
                    chosen_path = path

    run_clicked = st.button("Identify", type="primary") if uploaded else False

    # Optional: single-peak vs. pair-hash comparison toggle (Q3A experiment)
    with st.expander("Advanced: single peaks vs. paired hashes"):
        use_single = st.checkbox(
            "Match using single-peak hashes instead of paired hashes",
            value=False,
            help="Reproduces the Q3A comparison: single peaks collide far more "
                 "often across unrelated songs, so matches are far less decisive.",
        )

    source = None
    if chosen_path:
        source = chosen_path
    elif run_clicked and uploaded:
        source = uploaded

    if source is not None:
        y, sr = load_audio(source)
        result = _run_identification(y, sr, db, use_single_peaks=use_single)
        st.session_state["last_result"] = result
        st.session_state["last_use_single"] = use_single
        _render_result(result, db, use_single_peaks=use_single)
    elif "last_result" in st.session_state:
        _render_result(
            st.session_state["last_result"],
            db,
            use_single_peaks=st.session_state.get("last_use_single", False),
        )
