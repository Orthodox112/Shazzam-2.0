"""
app.py
======
Main Streamlit entry point. Run with:

    streamlit run app.py

Wires together the three tabs shown in the project demo:
  - Library  : browse the currently indexed song database (read-only)
  - Identify : upload/try one clip, see the full pipeline + match result
  - Batch    : upload many clips, download a results.csv

The fingerprint database is loaded once (cached) from data/db/fingerprints.json,
which build_database.py produces offline. The app itself never re-indexes
the library on startup -- this keeps page loads fast even with 50 songs.
"""
import streamlit as st

from fingerprint.database import FingerprintDB
from fingerprint import config
from app_pages import ui_style, library_tab, identify_tab, batch_tab

st.set_page_config(
    page_title="EE200: Audio Fingerprinting",
    page_icon="\U0001F3B5",
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_resource(show_spinner=False)
def get_database(path: str = config.DB_PATH_DEFAULT) -> FingerprintDB:
    return FingerprintDB.load(path)


def main():
    ui_style.inject_css()
    ui_style.header()

    db = get_database()

    tab_library, tab_identify, tab_batch = st.tabs(
        ["\u25C8 Library", "\u25CE Identify", "\u25A4 Batch"]
    )

    with tab_library:
        library_tab.render(db)
    with tab_identify:
        identify_tab.render(db)
    with tab_batch:
        batch_tab.render(db)

    if db.n_songs() == 0:
        st.info(
            "**No database found.** Place your 50 song files in `data/songs/` "
            "and run:\n\n```\npython build_database.py\n```\n\nthen restart this app.",
            icon="\u2139\ufe0f",
        )


if __name__ == "__main__":
    main()
