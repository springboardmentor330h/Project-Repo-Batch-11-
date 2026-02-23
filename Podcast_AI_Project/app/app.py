import streamlit as st
import json
import tempfile
import os
from pathlib import Path
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# -----------------------------
# CONFIG
# -----------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "results" / "segments_final.json"

PAGE_SIZE = 50

st.set_page_config(
    page_title="Podcast Transcript Navigation System",
    layout="wide"
)

# ── Custom CSS for premium look ──
st.markdown("""
<style>
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 12px 24px;
        font-weight: 600;
        font-size: 1.05rem;
    }

    /* Segment chips */
    .seg-chip {
        display: inline-block;
        padding: 6px 14px;
        margin: 3px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        cursor: pointer;
    }
    .seg-positive { background: #d4edda; color: #155724; }
    .seg-negative { background: #f8d7da; color: #721c24; }
    .seg-neutral  { background: #d1ecf1; color: #0c5460; }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# LOAD DATA
# -----------------------------

if not DATA_FILE.exists():
    st.error("❌ segments_final.json not found in results/")
    st.stop()

with open(DATA_FILE, "r", encoding="utf-8") as f:
    ALL_SEGMENTS = json.load(f)

# Fix data types and assign missing genre
for seg in ALL_SEGMENTS:
    seg["id"] = int(seg["id"])  # IDs are strings in JSON — convert to int
    if "genre" not in seg or not seg["genre"]:
        seg["genre"] = "genre1_education"

TOTAL_ALL = len(ALL_SEGMENTS)

# -----------------------------
# SESSION STATE INIT
# -----------------------------

if "selected_genre" not in st.session_state:
    st.session_state.selected_genre = "all"

if "timeline_page" not in st.session_state:
    st.session_state.timeline_page = 0

# -----------------------------
# SIDEBAR — GENRE FILTER
# -----------------------------

st.sidebar.title("🎯 Filters")

genres = sorted(set(seg["genre"] for seg in ALL_SEGMENTS))
genres.insert(0, "all")

selected_genre = st.sidebar.selectbox(
    "Choose Genre",
    genres,
    key="genre_filter"
)

# -----------------------------
# APPLY GENRE FILTER
# -----------------------------

if selected_genre == "all":
    segments = ALL_SEGMENTS
else:
    segments = [s for s in ALL_SEGMENTS if s["genre"] == selected_genre]

TOTAL = len(segments)

if TOTAL == 0:
    st.warning("No segments in this genre.")
    st.stop()

# -----------------------------
# BUILD SEGMENT DROPDOWN OPTIONS
# -----------------------------

segment_options = []
for seg in segments:
    title = seg.get("title", "")
    short = title[:40] + "..." if len(title) > 40 else title
    segment_options.append({
        "label": f"{seg['id']} - {short}",
        "id": seg["id"],
        "segment": seg
    })

# -----------------------------
# SIDEBAR — JUMP TO SEGMENT
# -----------------------------

st.sidebar.title("📍 Jump to Segment")

all_labels = [opt["label"] for opt in segment_options]

# If a timeline button was clicked, pre-set the selectbox value
if "clicked_seg" in st.session_state:
    clicked_id = st.session_state.clicked_seg
    del st.session_state.clicked_seg
    # Find the label for this segment ID
    for i, opt in enumerate(segment_options):
        if opt["id"] == clicked_id:
            st.session_state.seg_picker = all_labels[i]
            break

selected_option_label = st.sidebar.selectbox(
    "Segments",
    all_labels,
    key="seg_picker"
)

# Find the selected segment from the label
selected_segment_id = int(selected_option_label.split(" - ")[0])
selected_segment = next(
    (opt["segment"] for opt in segment_options if opt["id"] == selected_segment_id),
    segment_options[0]["segment"]
)

# Update timeline page based on selected segment
selected_index = next(
    (i for i, opt in enumerate(segment_options) if opt["id"] == selected_segment_id),
    0
)
st.session_state.timeline_page = selected_index // PAGE_SIZE


# =============================================================
# TABS
# =============================================================

st.title("🎧 Podcast Transcript Navigation System")

tab_browse, tab_upload = st.tabs(["📊 Genre Browser", "🎤 Upload & Analyze"])

# =============================================================
# TAB 1 — GENRE BROWSER
# =============================================================

with tab_browse:
    st.caption("Genre-aware topic navigation")

    st.info(f"📂 Active Genre: **{selected_genre}** | Segments: {TOTAL}")

    # -----------------------------
    # TIMELINE
    # -----------------------------

    st.subheader("🎯 Podcast Timeline")

    start = st.session_state.timeline_page * PAGE_SIZE
    end = min(start + PAGE_SIZE, TOTAL)

    st.caption(f"Showing segments {start+1}–{end} of {TOTAL}")

    nav1, nav2, nav3 = st.columns([1, 6, 1])

    with nav1:
        if st.button("⬅ Prev") and st.session_state.timeline_page > 0:
            new_start = (st.session_state.timeline_page - 1) * PAGE_SIZE
            st.session_state.clicked_seg = segment_options[new_start]["id"]
            st.rerun()

    with nav3:
        if st.button("Next ➡") and end < TOTAL:
            new_start = (st.session_state.timeline_page + 1) * PAGE_SIZE
            st.session_state.clicked_seg = segment_options[new_start]["id"]
            st.rerun()

    cols = st.columns(10)

    for idx, opt in enumerate(segment_options[start:end]):
        col = cols[idx % 10]
        seg = opt["segment"]

        sentiment = seg.get("sentiment", "neutral").lower()

        icon = (
            "🟢" if sentiment == "positive"
            else "🔴" if sentiment == "negative"
            else "🔵"
        )

        with col:
            if st.button(f"{icon} {seg['id']}", key=f"seg_{seg['id']}"):
                st.session_state.clicked_seg = seg["id"]
                st.rerun()

    st.divider()

    # -----------------------------
    # SEGMENT VIEW
    # -----------------------------

    st.subheader("📌 Segment")
    st.write(selected_segment.get("title", ""))

    # -----------------------------
    # SUMMARY
    # -----------------------------

    st.subheader("📝 Summary")

    summary = selected_segment.get("summary", "")
    if summary:
        st.success(summary)
    else:
        st.warning("Summary not available.")

    # -----------------------------
    # KEYWORDS
    # -----------------------------

    st.subheader("🔑 Keywords")

    keywords = selected_segment.get("keywords", "")
    if keywords:
        st.write(keywords)
    else:
        st.warning("Keywords not available.")

    # -----------------------------
    # WORD CLOUD
    # -----------------------------

    st.subheader("☁ Keyword Cloud")

    if keywords:
        wc = WordCloud(
            width=900,
            height=400,
            background_color="black",
            colormap="viridis"
        ).generate(keywords)

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("No keywords available for cloud.")

    # -----------------------------
    # SENTIMENT
    # -----------------------------

    st.subheader("😊 Sentiment")

    sent = selected_segment.get("sentiment", "neutral")
    score = selected_segment.get("sentiment_score", 0)

    if sent.lower() == "positive":
        st.success(f"{sent} ({score:.2f})")
    elif sent.lower() == "negative":
        st.error(f"{sent} ({score:.2f})")
    else:
        st.info(f"{sent} ({score:.2f})")

    # -----------------------------
    # TRANSCRIPT
    # -----------------------------

    st.subheader("📜 Transcript")
    st.write(selected_segment.get("text", ""))


# =============================================================
# TAB 2 — UPLOAD & ANALYZE
# =============================================================

with tab_upload:

    # ── Header ──
    st.markdown("""
    <div class="upload-header">
        <h2>🎤 Upload & Analyze Your Audio</h2>
        <p>Upload an audio file and watch the full NLP pipeline in action — from transcription to insights!</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Pipeline overview ──
    with st.expander("ℹ️ How it works — Pipeline Overview", expanded=False):
        st.markdown("""
        | Stage | Tool | Description |
        |-------|------|-------------|
        | 🎙️ **Transcription** | OpenAI Whisper | Converts your audio to text |
        | ✂️ **Sentence Splitting** | NLTK | Breaks text into individual sentences |
        | 🧠 **Topic Segmentation** | Sentence-Transformers | Groups sentences by topic similarity |
        | 📝 **Summarization** | BART (facebook/bart-large-cnn) | Generates concise summaries per segment |
        | 🔑 **Keyword Extraction** | KeyBERT | Finds the most relevant keywords |
        | 😊 **Sentiment Analysis** | TextBlob | Determines positive / neutral / negative tone |
        """)

    # ── File uploader ──
    uploaded_file = st.file_uploader(
        "Choose an audio file",
        type=["wav", "mp3", "m4a"],
        help="Supported formats: WAV, MP3, M4A. Recommended: under 5 minutes for faster processing."
    )

    # ── Session state for results ──
    if "upload_results" not in st.session_state:
        st.session_state.upload_results = None
    if "upload_selected_seg" not in st.session_state:
        st.session_state.upload_selected_seg = 0

    # ── Analyze button ──
    if uploaded_file is not None:
        st.audio(uploaded_file, format=f"audio/{uploaded_file.name.split('.')[-1]}")

        col_btn, col_info = st.columns([1, 3])
        with col_btn:
            analyze_clicked = st.button("🚀 Analyze Audio", type="primary", use_container_width=True)
        with col_info:
            st.caption("⏱️ Processing may take 2–5 minutes depending on audio length.")

        if analyze_clicked:
            # Save uploaded file to temp path
            suffix = "." + uploaded_file.name.split(".")[-1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name

            # Import pipeline
            from upload_analyzer import run_full_pipeline

            # Progress UI
            progress_bar = st.progress(0)
            status_text = st.empty()

            def progress_callback(stage, value):
                progress_bar.progress(min(value, 1.0))
                status_text.markdown(f"**{stage}**")

            # Run pipeline
            try:
                results = run_full_pipeline(tmp_path, progress_callback=progress_callback)
                st.session_state.upload_results = results
                st.session_state.upload_selected_seg = 0
                progress_bar.progress(1.0)
                status_text.markdown("**✅ Analysis complete!**")
            except Exception as e:
                st.error(f"❌ Error during analysis: {e}")
                import traceback
                st.code(traceback.format_exc())
            finally:
                # Clean up temp file
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

    # ── Display results ──
    results = st.session_state.upload_results

    if results is not None:
        segs = results["segments"]
        transcript = results["transcript"]
        total_segs = len(segs)

        st.divider()

        # ── METRICS ROW ──
        metric1, metric2, metric3, metric4 = st.columns(4)
        with metric1:
            st.metric("📄 Total Sentences", len(results.get("sentences", [])))
        with metric2:
            st.metric("🧩 Total Segments", total_segs)
        with metric3:
            pos_count = sum(1 for s in segs if s["sentiment"] == "Positive")
            st.metric("🟢 Positive Segments", pos_count)
        with metric4:
            neg_count = sum(1 for s in segs if s["sentiment"] == "Negative")
            st.metric("🔴 Negative Segments", neg_count)

        st.divider()

        # ── FULL TRANSCRIPT ──
        with st.expander("📜 Full Transcript", expanded=False):
            st.write(transcript)

        # ── SEGMENT TIMELINE ──
        st.subheader("🎯 Segment Timeline")
        st.caption("Click a segment to view its analysis. Colors indicate sentiment.")

        seg_cols = st.columns(min(10, total_segs))

        for idx, seg in enumerate(segs):
            col = seg_cols[idx % min(10, total_segs)]
            sent = seg["sentiment"].lower()
            icon = (
                "🟢" if sent == "positive"
                else "🔴" if sent == "negative"
                else "🔵"
            )
            with col:
                if st.button(f"{icon} {seg['id']}", key=f"upload_seg_{seg['id']}"):
                    st.session_state.upload_selected_seg = idx
                    st.rerun()

        st.divider()

        # ── SELECTED SEGMENT DETAIL ──
        sel_idx = st.session_state.upload_selected_seg
        if sel_idx >= total_segs:
            sel_idx = 0
        sel_seg = segs[sel_idx]

        st.subheader(f"📌 Segment {sel_seg['id']}")
        st.write(f"**{sel_seg['title']}**")

        detail_col1, detail_col2 = st.columns(2)

        with detail_col1:
            # Transcript
            st.markdown("##### 📜 Transcript")
            st.write(sel_seg["text"])

            # Summary
            st.markdown("##### 📝 Summary")
            if sel_seg["summary"]:
                st.success(sel_seg["summary"])
            else:
                st.warning("Summary not available.")

        with detail_col2:
            # Keywords
            st.markdown("##### 🔑 Keywords")
            kw = sel_seg.get("keywords", "")
            if kw:
                # Display as colored tags
                kw_list = [k.strip() for k in kw.split(",") if k.strip()]
                tag_html = " ".join(
                    [f'<span class="seg-chip seg-neutral">{k}</span>' for k in kw_list]
                )
                st.markdown(tag_html, unsafe_allow_html=True)
                st.write("")  # spacing
            else:
                st.warning("No keywords extracted.")

            # Sentiment
            st.markdown("##### 😊 Sentiment")
            sent_label = sel_seg["sentiment"]
            sent_score = sel_seg["sentiment_score"]
            if sent_label == "Positive":
                st.success(f"{sent_label} (score: {sent_score:.3f})")
            elif sent_label == "Negative":
                st.error(f"{sent_label} (score: {sent_score:.3f})")
            else:
                st.info(f"{sent_label} (score: {sent_score:.3f})")

            # Word Cloud for segment
            st.markdown("##### ☁️ Keyword Cloud")
            if kw:
                wc = WordCloud(
                    width=600,
                    height=300,
                    background_color="black",
                    colormap="plasma",
                    max_words=20,
                ).generate(kw)
                fig_seg, ax_seg = plt.subplots(figsize=(7, 3.5))
                ax_seg.imshow(wc, interpolation="bilinear")
                ax_seg.axis("off")
                st.pyplot(fig_seg)
                plt.close(fig_seg)
            else:
                st.info("No keywords for cloud.")

        st.divider()

        # ── OVERALL ANALYSIS ──
        st.subheader("📊 Overall Audio Analysis")

        overall_col1, overall_col2 = st.columns(2)

        with overall_col1:
            # Combined keyword cloud
            st.markdown("##### ☁️ Combined Keyword Cloud")
            all_keywords = " ".join([s.get("keywords", "") for s in segs])
            if all_keywords.strip():
                wc_all = WordCloud(
                    width=700,
                    height=350,
                    background_color="black",
                    colormap="viridis",
                    max_words=40,
                ).generate(all_keywords)
                fig_all, ax_all = plt.subplots(figsize=(8, 4))
                ax_all.imshow(wc_all, interpolation="bilinear")
                ax_all.axis("off")
                st.pyplot(fig_all)
                plt.close(fig_all)
            else:
                st.info("No keywords available.")

        with overall_col2:
            # Sentiment distribution pie chart
            st.markdown("##### 📈 Sentiment Distribution")
            pos = sum(1 for s in segs if s["sentiment"] == "Positive")
            neg = sum(1 for s in segs if s["sentiment"] == "Negative")
            neu = sum(1 for s in segs if s["sentiment"] == "Neutral")

            if pos + neg + neu > 0:
                fig_pie, ax_pie = plt.subplots(figsize=(5, 5))
                labels_pie = []
                sizes = []
                colors = []
                if pos > 0:
                    labels_pie.append(f"Positive ({pos})")
                    sizes.append(pos)
                    colors.append("#28a745")
                if neu > 0:
                    labels_pie.append(f"Neutral ({neu})")
                    sizes.append(neu)
                    colors.append("#17a2b8")
                if neg > 0:
                    labels_pie.append(f"Negative ({neg})")
                    sizes.append(neg)
                    colors.append("#dc3545")

                ax_pie.pie(
                    sizes,
                    labels=labels_pie,
                    colors=colors,
                    autopct="%1.0f%%",
                    startangle=90,
                    textprops={"fontsize": 12, "fontweight": "bold"},
                )
                ax_pie.set_title("Segment Sentiment Breakdown", fontsize=14, fontweight="bold")
                st.pyplot(fig_pie)
                plt.close(fig_pie)
            else:
                st.info("No sentiment data available.")
