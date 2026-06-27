import streamlit as st


def render(db):
    st.markdown('<p class="ee-eyebrow">Library</p>', unsafe_allow_html=True)

    if db.n_songs() == 0:
        st.markdown(
            """
            <div class="song-card">
                <div class="name">No songs indexed yet.</div>
                <div class="hashes dim">
                    Run <code>python build_database.py</code> after placing your
                    song files in <code>data/songs/</code>, then reload this app.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        '<p class="dim" style="margin-bottom:18px;">'
        'Song indexing is managed by the admin (<code>build_database.py</code>). '
        'Drop a clip in the Identify or Batch tab to test the library.</p>',
        unsafe_allow_html=True,
    )

    st.markdown(f'<p class="dim" style="letter-spacing:1px;">IN THE DATABASE &middot; {db.n_songs()} songs</p>',
                unsafe_allow_html=True)

    items = sorted(db.songs.items(), key=lambda kv: kv[1]["filename"].lower())
    cols_per_row = 5
    rows = [items[i:i + cols_per_row] for i in range(0, len(items), cols_per_row)]
    for row in rows:
        cols = st.columns(cols_per_row)
        for col, (song_id, meta) in zip(cols, row):
            title = meta["filename"].rsplit(".", 1)[0]
            with col:
                st.markdown(
                    f"""
                    <div class="song-card">
                        <div class="name">{title}</div>
                        <div class="hashes">{meta['n_hashes']:,} hashes</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
