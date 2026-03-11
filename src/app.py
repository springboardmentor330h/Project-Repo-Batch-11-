"""
AudioInsight — Full Pipeline Streamlit App
==========================================
End-to-end AI podcast analysis pipeline:
  1. Audio Upload / URL Download
  2. Audio Preprocessing  (audio_preprocessing.py)
  3. Whisper Transcription (transcribe.py)
  4. Transcript Cleaning  (trancript_cleaner.py)
  5. TextTiling Segmentation (algorithim2.py)
  6. Keywords & Evaluation  (evaluate.py)
  7. Analytics & Visualisation (analytics.py)

Run:  streamlit run app.py
"""

import streamlit as st
import sys, os, json, tempfile, traceback
from pathlib import Path

# ── PAGE CONFIG (must be first) ───────────────────────────────────────────────
st.set_page_config(
    page_title="AudioInsight",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── STYLES ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@300;400;500&display=swap');

html, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }

/* ── HERO ──────────────────────────────── */
.hero {
  background: #ffffff;
  border-bottom: 1px solid #e5e5e7;
  padding: 4rem 1rem 3.5rem;
  margin-bottom: 2.5rem;
  text-align: center;
}
.hero-tag {
  display: inline-block;
  font-size: .72rem;
  font-weight: 600;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: #6e6e73;
  margin-bottom: 1.1rem;
}
.hero-title {
  font-size: 3.8rem;
  font-weight: 800;
  letter-spacing: -.03em;
  color: #1d1d1f;
  line-height: 1.05;
  margin: 0 auto .9rem;
  max-width: 680px;
}
.hero-title em {
  font-style: normal;
  background: linear-gradient(90deg, #0071e3 0%, #5e5ce6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero-desc {
  font-size: 1.05rem;
  color: #6e6e73;
  font-weight: 400;
  max-width: 500px;
  line-height: 1.65;
  margin: 0 auto 1.6rem;
}
.hero-chips {
  display: flex; gap: .45rem; flex-wrap: wrap;
  justify-content: center;
}
.step-chip {
  font-family: 'JetBrains Mono', monospace;
  font-size: .62rem;
  font-weight: 500;
  letter-spacing: .04em;
  padding: .3rem .75rem;
  border-radius: 20px;
  border: 1px solid #d2d2d7;
  color: #6e6e73;
  background: #f5f5f7;
}

/* ── HOW IT WORKS ───────────────────────── */
.how-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.1rem 1.2rem;
  height: 100%;
}
.how-num   { font-family: 'JetBrains Mono', monospace; font-size: .65rem; color: #7c3aed; font-weight: 600; margin-bottom: .35rem; }
.how-title { font-weight: 600; font-size: .88rem; color: #0f172a; margin-bottom: .3rem; }
.how-desc  { font-size: .78rem; color: #64748b; line-height: 1.5; }

/* ── SETTING CARD ───────────────────────── */
.setting-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: .9rem 1rem;
  margin-bottom: .7rem;
}
.setting-label { font-weight: 600; font-size: .8rem; color: #334155; margin-bottom: .15rem; }
.setting-hint  { font-size: .72rem; color: #94a3b8; line-height: 1.4; margin-top: .25rem; }

/* ── PIPELINE STEPS ─────────────────────── */
.prog-step {
  display: flex; align-items: center; gap: .7rem;
  padding: .42rem .6rem;
  border-radius: 8px;
  margin-bottom: .25rem;
}
.prog-step.running { background: rgba(167,139,250,.08); }
.prog-step.done    { background: rgba(34,197,94,.06); }
.prog-step.error   { background: rgba(239,68,68,.06); }
.prog-dot  { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.prog-text { font-size: .78rem; font-weight: 500; color: #334155; }
.prog-sub  { font-family: 'JetBrains Mono', monospace; font-size: .58rem; color: #94a3b8; }

/* ── METRIC STRIP ───────────────────────── */
.mstrip { display: flex; gap: .65rem; flex-wrap: wrap; margin: 1.2rem 0; }
.mcard  {
  flex: 1; min-width: 100px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1rem 1.1rem;
  box-shadow: 0 1px 3px rgba(0,0,0,.04);
}
.mval { font-size: 1.6rem; font-weight: 700; color: #7c3aed; line-height: 1; }
.mlbl { font-family: 'JetBrains Mono', monospace; font-size: .55rem; letter-spacing: .1em; text-transform: uppercase; color: #94a3b8; margin-top: .3rem; }

/* ── TOPIC CARDS ────────────────────────── */
.tcard {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-left: 4px solid #7c3aed;
  border-radius: 12px;
  padding: 1.3rem 1.5rem;
  margin-bottom: .8rem;
  box-shadow: 0 1px 4px rgba(0,0,0,.04);
}
.tcard-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; margin-bottom: .6rem; }
.tcard-title { font-weight: 600; font-size: .95rem; color: #0f172a; }
.tcard-badge { font-family: 'JetBrains Mono', monospace; font-size: .6rem; padding: .2rem .55rem; border-radius: 20px; color: #fff; white-space: nowrap; flex-shrink: 0; }
.tcard-time  { font-family: 'JetBrains Mono', monospace; font-size: .65rem; color: #7c3aed; margin-bottom: .5rem; }
.tcard-summary { font-size: .85rem; line-height: 1.7; color: #475569; margin-bottom: .7rem; }
.kw-row { display: flex; flex-wrap: wrap; gap: .3rem; }
.kw { font-family: 'JetBrains Mono', monospace; font-size: .62rem; padding: .18rem .55rem; background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 20px; color: #475569; }

/* ── TRANSCRIPT ─────────────────────────── */
.ts-wrap { max-height: 580px; overflow-y: auto; border: 1px solid #e2e8f0; border-radius: 12px; background: #fff; padding: 1.2rem 1.4rem; }
.ts-divider { font-family: 'JetBrains Mono', monospace; font-size: .6rem; letter-spacing: .14em; text-transform: uppercase; padding: .45rem .6rem; border-radius: 6px; margin: 1rem 0 .4rem; display: inline-block; }
.ts-line { padding: .38rem 0; border-bottom: 1px solid #f1f5f9; font-size: .85rem; line-height: 1.65; color: #334155; }
.ts-time { font-family: 'JetBrains Mono', monospace; font-size: .6rem; color: #7c3aed; margin-right: .5rem; font-weight: 500; }

/* ── SECTION HEADING ────────────────────── */
.sec-head { font-size: 1.1rem; font-weight: 700; color: #0f172a; margin-bottom: 1rem; padding-bottom: .4rem; border-bottom: 2px solid #7c3aed; display: inline-block; }

/* ── SEARCH ─────────────────────────────── */
.search-hit { background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: .7rem 1rem; margin-bottom: .4rem; font-size: .85rem; line-height: 1.6; color: #334155; }
.empty-state { text-align: center; padding: 3rem 2rem; color: #94a3b8; }
.empty-icon  { font-size: 3rem; margin-bottom: .8rem; }
.empty-title { font-weight: 600; font-size: 1rem; color: #475569; margin-bottom: .4rem; }
.empty-desc  { font-size: .82rem; line-height: 1.6; }

/* ── DOWNLOAD CARDS ─────────────────────── */
.dl-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.2rem; text-align: center; margin-bottom: .5rem; }
.dl-icon  { font-size: 1.8rem; margin-bottom: .4rem; }
.dl-title { font-weight: 600; font-size: .88rem; color: #0f172a; margin-bottom: .2rem; }
.dl-desc  { font-size: .75rem; color: #94a3b8; margin-bottom: .8rem; }

/* ── BUTTON OVERRIDES ───────────────────── */
.stButton > button {
  background: #7c3aed !important; color: #fff !important;
  border: none !important; border-radius: 10px !important;
  font-family: 'Inter', sans-serif !important;
  font-weight: 600 !important; font-size: .85rem !important;
  padding: .6rem 1.3rem !important; transition: opacity .18s !important;
}
.stButton > button:hover { opacity: .88 !important; }
.stButton > button[kind="secondary"] { background: #f1f5f9 !important; color: #475569 !important; }
.stTabs [data-baseweb="tab"] { font-family: 'Inter', sans-serif !important; font-weight: 600 !important; font-size: .82rem !important; }
.stTabs [aria-selected="true"] { color: #7c3aed !important; }
div[data-testid="stMetricValue"] { color: #7c3aed !important; font-weight: 700 !important; }
</style>
""", unsafe_allow_html=True)

# ── IMPORTS ───────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

MISSING = []
def _try_import(mod, cls=None):
    try:
        m = __import__(mod)
        return getattr(m, cls) if cls else m
    except Exception as e:
        MISSING.append(f"{mod}{'.'+cls if cls else ''}: {e}")
        return None

AudioPreprocessor     = _try_import("audio_preprocessing", "AudioPreprocessor")
AudioTranscriber      = _try_import("transcribe",           "AudioTranscriber")
TranscriptCleaner     = _try_import("trancript_cleaner",    "TranscriptCleaner")
TextTilingSegmenter   = _try_import("algorithim2",          "TextTilingSegmenter")
SegmentationEvaluator = _try_import("evaluate",             "SegmentationEvaluator")
KeywordExtractor      = _try_import("evaluate",             "KeywordExtractor")
SummaryGenerator      = _try_import("evaluate",             "SummaryGenerator")
TranscriptAnalytics   = _try_import("analytics",            "TranscriptAnalytics")
URLDownloader         = _try_import("url_downloader",       "URLDownloader")

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
TOPIC_COLORS = [
    "#7c3aed","#2563eb","#059669","#d97706",
    "#dc2626","#0891b2","#9333ea","#16a34a",
]

PIPELINE_STEPS = [
    ("preprocess", "🔊 Preprocess Audio",      "Noise reduction & chunking"),
    ("transcribe",  "✍️  Transcribe",            "Whisper speech-to-text"),
    ("clean",       "🧹 Clean Transcript",      "Remove fillers & merge sentences"),
    ("segment",     "🗂️  Segment Topics",        "TextTiling NLP"),
    ("keywords",    "🔑 Keywords & Summaries",  "TF-IDF extraction"),
    ("analytics",   "📊 Analytics",             "Compute metrics"),
]

MODEL_INFO = {
    "tiny":   "⚡ Fastest · Great for testing",
    "base":   "✅ Recommended · Best balance of speed & accuracy",
    "small":  "🔍 Better accuracy · ~2× slower than base",
    "medium": "🎯 High accuracy · ~5× slower",
    "large":  "💎 Best quality · Very slow (needs good GPU)",
}

def fmt_time(sec):
    if sec is None: return "—"
    m, s = divmod(int(sec), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

def set_step(name, status, msg=""):
    st.session_state.step_status[name] = status
    st.session_state.step_msg[name]    = msg

def render_pipeline_status():
    dot_colors = {"pending":"#cbd5e1","running":"#a78bfa","done":"#22c55e","error":"#ef4444","skipped":"#cbd5e1"}
    html = ""
    for name, label, hint in PIPELINE_STEPS:
        s   = st.session_state.step_status.get(name, "pending")
        msg = st.session_state.step_msg.get(name, hint)
        dc  = dot_colors[s]
        cls = s if s in ("running","done","error") else ""
        html += (
            f"<div class='prog-step {cls}'>"
            f"<div class='prog-dot' style='background:{dc};'></div>"
            f"<div><div class='prog-text'>{label}</div>"
            f"<div class='prog-sub'>{msg}</div></div></div>"
        )
    return html

# ── SESSION STATE ─────────────────────────────────────────────────────────────
for k, v in {"result":None,"running":False,"step_status":{},"step_msg":{}}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── PIPELINE RUNNER ───────────────────────────────────────────────────────────
def run_pipeline(audio_bytes, filename, model_size, language, block_size,
                 prog_bar, stat_ph, sidebar_ph):
    R   = {}
    n   = len(PIPELINE_STEPS)
    idx = {name: i+1 for i,(name,_,_) in enumerate(PIPELINE_STEPS)}

    def upd(name, label, status, msg=""):
        set_step(name, status, msg)
        prog_bar.progress(min(idx[name]/n, 1.0))
        icon = {"running":"⏳","done":"✅","error":"❌"}.get(status,"")
        stat_ph.markdown(
            f"<div style='font-family:JetBrains Mono,monospace;font-size:.78rem;"
            f"color:#64748b;padding:.4rem .7rem;background:#f8fafc;"
            f"border-radius:8px;border:1px solid #e2e8f0;'>"
            f"{icon} <b>{label}</b>{' — '+msg if msg else ''}</div>",
            unsafe_allow_html=True,
        )
        sidebar_ph.markdown(render_pipeline_status(), unsafe_allow_html=True)

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        audio_path = tmp / filename
        audio_path.write_bytes(audio_bytes)

        # 1. PREPROCESS
        upd("preprocess","Preprocess Audio","running","Reducing noise & splitting into chunks…")
        try:
            pre      = AudioPreprocessor()
            proc_dir = tmp / "processed"
            pp       = pre.process_file(audio_path, proc_dir, create_chunks=True)
            if not pp or not pp.get("success"):
                raise RuntimeError(pp.get("error","failed") if pp else "None returned")
            chunks_dir  = proc_dir / "chunks"
            chunk_files = sorted(chunks_dir.glob("*.wav")) if chunks_dir.exists() else []
            if not chunk_files:
                full_dir    = proc_dir / "full"
                chunk_files = sorted(full_dir.glob("*.wav")) if full_dir.exists() else [audio_path]
            audio_dur = pp.get("processed_duration", pp.get("original_duration",0))
            R["audio_duration"] = audio_dur
            R["filename"]       = filename
            upd("preprocess","Preprocess Audio","done",f"{len(chunk_files)} chunks · {audio_dur:.0f}s")
        except Exception as e:
            upd("preprocess","Preprocess Audio","error",str(e)[:80])
            R["error"]=f"Preprocess: {e}"; R["traceback"]=traceback.format_exc(); return R

        # 2. TRANSCRIBE
        upd("transcribe","Transcribe","running",f"Whisper '{model_size}' on {len(chunk_files)} chunk(s)…")
        try:
            lang = None if language=="auto" else language
            tr   = AudioTranscriber(model_size=model_size, language=lang or "en")
            tr.load_model()
            meta_dir=proc_dir/"metadata"; chunk_meta={}
            if meta_dir.exists():
                for mf in meta_dir.glob("*.json"):
                    with open(mf) as f: md=json.load(f)
                    for cm in md.get("chunks",[]): chunk_meta[cm["chunk_id"]-1]=cm["start_time"]
            hop=pre.config["chunk_duration"]-pre.config["chunk_overlap"]
            all_segs=[]; seen=set()
            for ci,cp in enumerate(chunk_files):
                upd("transcribe","Transcribe","running",f"Chunk {ci+1} of {len(chunk_files)}…")
                res=tr.transcribe_file(cp)
                if not res["success"]: continue
                offset=chunk_meta.get(ci,ci*hop)
                for seg in res["segments"]:
                    key=seg["text"].strip()[:35]
                    if key in seen: continue
                    seen.add(key)
                    s=dict(seg); s["start"]=round(seg["start"]+offset,2); s["end"]=round(seg["end"]+offset,2)
                    all_segs.append(s)
            if not all_segs: raise RuntimeError("No segments produced")
            raw={"segments":all_segs,"metadata":{"model":model_size,"language":language}}
            raw_path=tmp/"raw.json"; raw_path.write_text(json.dumps(raw,indent=2))
            R["raw_transcript"]=raw; R["raw_path"]=str(raw_path)
            upd("transcribe","Transcribe","done",f"{len(all_segs)} segments transcribed")
        except Exception as e:
            upd("transcribe","Transcribe","error",str(e)[:80])
            R["error"]=f"Transcribe: {e}"; R["traceback"]=traceback.format_exc(); return R

        # 3. CLEAN
        upd("clean","Clean Transcript","running","Merging sentences & removing filler words…")
        try:
            cleaner=TranscriptCleaner(aggressive=False)
            cleaned_path=tmp/"cleaned.json"
            cl=cleaner.process_file(Path(R["raw_path"]),cleaned_path)
            if not cl.get("success"):
                sents=cleaner.merge_segments(all_segs)
                cleaned={"metadata":{"cleaned_sentences":len(sents)},"sentences":sents}
                cleaned_path.write_text(json.dumps(cleaned,indent=2))
            else:
                cleaned=json.loads(cleaned_path.read_text())
            R["cleaned"]=cleaned; R["cleaned_path"]=str(cleaned_path)
            upd("clean","Clean Transcript","done",f"{len(cleaned.get('sentences',[]))} sentences ready")
        except Exception as e:
            upd("clean","Clean Transcript","error",str(e)[:80])
            R["error"]=f"Clean: {e}"; R["traceback"]=traceback.format_exc(); return R

        # 4. SEGMENT
        upd("segment","Segment Topics","running",f"TextTiling with block size {block_size}…")
        try:
            sents=cleaned.get("sentences",[])
            if not sents: raise RuntimeError("No sentences to segment")
            seg_model=TextTilingSegmenter(block_size=block_size,smoothing_width=2)
            segs_list,_,cohesion=seg_model.segment_transcript(sents,threshold=None,min_distance=1)
            topics=[]
            for i,ss in enumerate(segs_list):
                if not ss: continue
                txt=" ".join(s.get("text","") for s in ss)
                try:    sentiment=seg_model.analyze_sentiment(txt)
                except: sentiment=0.0
                topics.append({
                    "topic_id":i+1,"label":seg_model.get_topic_label(txt),
                    "num_sentences":len(ss),"start_time":ss[0].get("start",0),
                    "end_time":ss[-1].get("end",0),
                    "duration":round(ss[-1].get("end",0)-ss[0].get("start",0),2),
                    "sentences":ss,"full_text":txt,"sentiment_score":sentiment,
                    "keywords":[],"summary":"",
                })
            cohesion_list=cohesion.tolist() if hasattr(cohesion,"tolist") else list(cohesion)
            R["topics_data"]={"topics":topics,"num_topics":len(topics),"cohesion_scores":cohesion_list}
            upd("segment","Segment Topics","done",f"{len(topics)} topic{'s' if len(topics)!=1 else ''} found")
        except Exception as e:
            upd("segment","Segment Topics","error",str(e)[:80])
            R["error"]=f"Segment: {e}"; R["traceback"]=traceback.format_exc(); return R

        # 5. KEYWORDS
        upd("keywords","Keywords & Summaries","running","Extracting TF-IDF keywords…")
        try:
            evaluator=SegmentationEvaluator(); extractor=KeywordExtractor(); summariser=SummaryGenerator()
            R["evaluation"]=evaluator.evaluate_segmentation(R["topics_data"])
            texts=[t["full_text"] for t in topics]
            all_kws=extractor.extract_keywords_tfidf(texts,top_n=6) if len(texts)>1 \
                    else [extractor.extract_keywords_frequency(t,top_n=6) for t in texts]
            for i,t in enumerate(topics):
                t["keywords"]=all_kws[i] if i<len(all_kws) else []
                t["summary"]=summariser.generate_summary(t["sentences"],t["keywords"])
            score=R["evaluation"].get("overall_score",0)
            upd("keywords","Keywords & Summaries","done",f"Quality score: {score:.1f}/10")
        except Exception as e:
            set_step("keywords","error",str(e)[:60])

        # 6. ANALYTICS
        upd("analytics","Analytics","running","Computing speaking & readability metrics…")
        try:
            an=TranscriptAnalytics()
            full_text=" ".join(s.get("text","") for s in cleaned.get("sentences",[]))
            try:
                R["analytics"]=an.calculate_all_metrics(cleaned,R["topics_data"])
            except Exception:
                R["analytics"]={
                    "basic":      an.calculate_basic_metrics(cleaned.get("sentences",[]),full_text),
                    "vocabulary": an.calculate_vocabulary_metrics(full_text),
                    "speaking":   an.calculate_speaking_metrics(cleaned.get("sentences",[])),
                    "readability":an.calculate_readability_metrics(full_text),
                    "topics":     an.calculate_topic_metrics(R["topics_data"].get("topics",[])),
                    "sentiment":  {"timeline":[],"avg_polarity":0,"polarity_std":0},
                }
            wpm=R["analytics"].get("speaking",{}).get("words_per_minute",0)
            upd("analytics","Analytics","done",f"{wpm:.0f} words per minute")
        except Exception as e:
            set_step("analytics","error",str(e)[:60]); R["analytics"]={}

        prog_bar.progress(1.0)
        stat_ph.markdown(
            "<div style='font-family:JetBrains Mono,monospace;font-size:.78rem;"
            "color:#16a34a;padding:.5rem .8rem;background:#f0fdf4;"
            "border-radius:8px;border:1px solid #bbf7d0;'>"
            "✅ Analysis complete! Scroll down to explore your results.</div>",
            unsafe_allow_html=True,
        )
        R["success"]=True
        return R


# ═══════════════════════════════════════════════════════════
# HERO HEADER
# ═══════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
  <div class="hero-tag">AI-Powered Podcast Analysis</div>
  <div class="hero-title"><em>AudioInsight</em></div>
  <div class="hero-desc">
    Upload any podcast and instantly get a full transcript,
    auto-detected topics, keywords, summaries and analytics.
  </div>
  <div class="hero-chips">
    <span class="step-chip">Whisper ASR</span>
    <span class="step-chip">TextTiling NLP</span>
    <span class="step-chip">TF-IDF Keywords</span>
    <span class="step-chip">Sentiment Analysis</span>
    <span class="step-chip">Analytics</span>
  </div>
</div>
""", unsafe_allow_html=True)

if MISSING:
    with st.expander(f"⚠️ {len(MISSING)} module(s) not found — click for details"):
        for m in MISSING: st.code(m)
        st.info("Place all .py pipeline files beside app.py, then run: `pip install -r requirements.txt`")

# ═══════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.caption("Adjust these before running the pipeline.")
    st.markdown("---")

    st.markdown('<div class="setting-card"><div class="setting-label">🤖 Whisper Model</div>',
                unsafe_allow_html=True)
    model_size = st.selectbox("model",["tiny","base","small","medium","large"],
                              index=1, label_visibility="collapsed")
    st.markdown(f'<div class="setting-hint">{MODEL_INFO.get(model_size,"")}</div></div>',
                unsafe_allow_html=True)

    st.markdown('<div class="setting-card"><div class="setting-label">🌍 Audio Language</div>',
                unsafe_allow_html=True)
    language = st.selectbox("lang",
        ["en","es","fr","de","it","pt","nl","ru","zh","ja","ko","hi","ar","auto"],
        index=0, label_visibility="collapsed")
    st.markdown('<div class="setting-hint">Choose <b>auto</b> if unsure — Whisper detects it automatically.</div></div>',
                unsafe_allow_html=True)

    st.markdown('<div class="setting-card"><div class="setting-label">📦 Topic Sensitivity</div>',
                unsafe_allow_html=True)
    block_size = st.slider("block", 3, 20, 5, label_visibility="collapsed")
    slabel = "High" if block_size<=5 else ("Medium" if block_size<=12 else "Low")
    shints = {
        "High":   "Finds more topics. Best for varied podcasts with many subjects.",
        "Medium": "Balanced. Good default for most content.",
        "Low":    "Finds fewer, broader topics. Best for focused single-subject talks.",
    }
    st.markdown(f'<div class="setting-hint"><b>{slabel} sensitivity</b> (block={block_size}) — {shints[slabel]}</div></div>',
                unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📋 Pipeline Progress")
    sidebar_status = st.empty()
    sidebar_status.markdown(render_pipeline_status(), unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# INPUT PANEL (shown only when no result yet)
# ═══════════════════════════════════════════════════════════
if not st.session_state.result:

    # How it works
    st.markdown("### 💡 How It Works")
    c1,c2,c3,c4 = st.columns(4)
    for col,(num,title,desc) in zip([c1,c2,c3,c4],[
        ("01","Upload Audio",      "Drop any MP3, WAV, M4A or FLAC file — we handle the rest."),
        ("02","AI Transcription",  "Whisper converts speech to text with accurate timestamps."),
        ("03","Topic Detection",   "TextTiling NLP automatically finds where topics change."),
        ("04","Insights & Export", "Get keywords, summaries, analytics and downloadable reports."),
    ]):
        with col:
            st.markdown(
                f'<div class="how-card"><div class="how-num">STEP {num}</div>'
                f'<div class="how-title">{title}</div>'
                f'<div class="how-desc">{desc}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📂 Add Your Audio")

    tab_up, tab_url = st.tabs(["📁 Upload File", "🔗 From URL"])

    # ── UPLOAD TAB ───────────────────────────────────────────────────────────
    with tab_up:
        up_file = st.file_uploader(
            "🎵 Drag & drop your podcast audio here  ·  MP3 · WAV · M4A · FLAC · OGG · WEBM",
            type=["mp3","wav","m4a","flac","ogg","webm"],
        )

        if up_file:
            st.markdown("<br>", unsafe_allow_html=True)
            ca, cb, cc = st.columns([3,1,1])
            with ca: st.audio(up_file)
            with cb: st.metric("📦 Size",   f"{up_file.size/1e6:.1f} MB")
            with cc: st.metric("🎵 Format", up_file.name.split(".")[-1].upper())

            st.markdown("<br>", unsafe_allow_html=True)

            with st.expander("⚙️ Review your settings before running", expanded=False):
                ra,rb,rc = st.columns(3)
                with ra: st.info(f"**Model:** {model_size}\n\n{MODEL_INFO.get(model_size,'')}")
                with rb: st.info(f"**Language:** {'Auto-detect' if language=='auto' else language.upper()}")
                with rc: st.info(f"**Topic Sensitivity:** {slabel}\n\nBlock size = {block_size}")

            if st.button("🚀  Analyse This Podcast", width="stretch", type="primary",
                         disabled=st.session_state.running):
                st.session_state.step_status={}; st.session_state.step_msg={}
                st.session_state.running=True
                st.markdown("---")
                st.markdown("### ⏳ Running Analysis Pipeline…")
                st.caption("This may take a few minutes depending on audio length and model size.")
                prog=st.progress(0); stat=st.empty()
                res=run_pipeline(
                    audio_bytes=up_file.getvalue(), filename=up_file.name,
                    model_size=model_size, language=language, block_size=block_size,
                    prog_bar=prog, stat_ph=stat, sidebar_ph=sidebar_status,
                )
                st.session_state.running=False
                if res.get("success"):
                    st.session_state.result=res; st.rerun()
                else:
                    st.error(f"❌ **Pipeline failed:** {res.get('error','Unknown error')}")
                    if res.get("traceback"):
                        with st.expander("🔍 Show technical error details"):
                            st.code(res["traceback"])
        else:
            st.markdown(
                "<div style='text-align:center;padding:2rem;color:#94a3b8;"
                "background:#f8fafc;border:2px dashed #e2e8f0;border-radius:12px;'>"
                "<div style='font-size:2rem;margin-bottom:.5rem;'>🎵</div>"
                "<div style='font-weight:600;color:#475569;margin-bottom:.3rem;'>No file uploaded yet</div>"
                "<div style='font-size:.82rem;'>Click or drag an audio file above to get started</div>"
                "</div>",
                unsafe_allow_html=True,
            )

    # ── URL TAB ───────────────────────────────────────────────────────────────
    with tab_url:
        if not URLDownloader:
            st.warning("⚠️ `url_downloader.py` not found. Place it beside `app.py` to enable this feature.")
        else:
            st.markdown("**Paste a direct link to an audio file:**")
            st.caption("Works with direct MP3/WAV/M4A links. Does not support Spotify, YouTube or other streaming platforms.")
            url_input = st.text_input("Audio URL",
                placeholder="https://example.com/episode.mp3", label_visibility="collapsed")
            if url_input:
                dl=URLDownloader(timeout=120)
                valid,err=dl.validate_url(url_input)
                if not valid:
                    st.error(f"❌ {err}")
                else:
                    st.success("✅ URL looks valid")
                    if st.button("⬇️  Download & Analyse", width="stretch", type="primary",
                                 disabled=st.session_state.running):
                        st.session_state.step_status={}; st.session_state.step_msg={}
                        st.session_state.running=True
                        prog=st.progress(0); stat=st.empty(); dl_ph=st.empty()
                        try:
                            from urllib.parse import urlparse
                            url_path=urlparse(url_input).path
                            filename=Path(url_path).name or "audio.mp3"
                            ext=Path(url_path).suffix.lower()
                            if ext not in URLDownloader.SUPPORTED_AUDIO_EXTENSIONS:
                                ext=".mp3"; filename=f"audio{ext}"
                            dl_ph.info("⬇️ Downloading audio…")
                            import tempfile as _tf
                            with _tf.TemporaryDirectory() as _td:
                                dl_path=Path(_td)/filename
                                def _cb(d,t):
                                    dl_ph.info(f"⬇️ {d/1e6:.1f}/{t/1e6:.1f} MB ({d/t:.0%})" if t>0 else f"⬇️ {d/1e6:.1f} MB…")
                                ok,dl_err=dl.download_with_retry(url_input,dl_path,retries=3,progress_callback=_cb)
                                dl_ph.empty()
                                if not ok: raise RuntimeError(dl_err)
                                audio_bytes=dl_path.read_bytes()
                            res=run_pipeline(
                                audio_bytes=audio_bytes, filename=filename,
                                model_size=model_size, language=language, block_size=block_size,
                                prog_bar=prog, stat_ph=stat, sidebar_ph=sidebar_status,
                            )
                        except Exception as e:
                            dl_ph.empty()
                            res={"error":f"Download failed: {e}","traceback":traceback.format_exc()}
                        st.session_state.running=False
                        if res.get("success"):
                            st.session_state.result=res; st.rerun()
                        else:
                            st.error(f"❌ {res.get('error','Failed')}")
                            if res.get("traceback"):
                                with st.expander("🔍 Error details"): st.code(res["traceback"])


# ═══════════════════════════════════════════════════════════
# RESULTS PANEL
# ═══════════════════════════════════════════════════════════
if st.session_state.result:
    import plotly.graph_objects as go
    import plotly.express as px

    D        = st.session_state.result
    topics   = D.get("topics_data",{}).get("topics",[])
    sents    = D.get("cleaned",{}).get("sentences",[])
    analytics= D.get("analytics",{})
    eval_res = D.get("evaluation",{})
    cohesion = D.get("topics_data",{}).get("cohesion_scores",[])
    basic    = analytics.get("basic",{})
    vocab    = analytics.get("vocabulary",{})
    speaking = analytics.get("speaking",{})
    dur      = D.get("audio_duration",0)

    # Result banner + clear button
    ba,bb = st.columns([7,1])
    with ba: st.success(f"✅ **{D.get('filename','')}** analysed successfully")
    with bb:
        if st.button("🗑  New File", width="stretch"):
            st.session_state.result=None
            st.session_state.step_status={}
            st.session_state.step_msg={}
            st.rerun()

    # Metric strip
    st.markdown(f"""
    <div class="mstrip">
      <div class="mcard"><div class="mval">{fmt_time(dur)}</div><div class="mlbl">⏱ Duration</div></div>
      <div class="mcard"><div class="mval">{len(topics)}</div><div class="mlbl">🗂 Topics</div></div>
      <div class="mcard"><div class="mval">{len(sents)}</div><div class="mlbl">📝 Sentences</div></div>
      <div class="mcard"><div class="mval">{basic.get('total_words',0):,}</div><div class="mlbl">💬 Words</div></div>
      <div class="mcard"><div class="mval">{speaking.get('words_per_minute',0):.0f}</div><div class="mlbl">🎙 WPM</div></div>
      <div class="mcard"><div class="mval">{vocab.get('vocabulary_diversity',0):.0%}</div><div class="mlbl">📖 Vocab Diversity</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Tabs
    t1,t2,t3,t4,t5 = st.tabs([
        "📄 Transcript","📚 Topics & Summaries","📈 Analytics","🔍 Search","📥 Download"
    ])

    # ══════════════════════════════════════
    # TAB 1 — TRANSCRIPT
    # ══════════════════════════════════════
    with t1:
        st.markdown('<div class="sec-head">Full Transcript</div>', unsafe_allow_html=True)

        if topics:
            st.markdown("**Topic guide — colour-coded sections below:**")
            chip_cols = st.columns(min(len(topics),6))
            for i,tp in enumerate(topics):
                c=TOPIC_COLORS[i%len(TOPIC_COLORS)]
                with chip_cols[i%len(chip_cols)]:
                    st.markdown(
                        f"<div style='background:{c};color:#fff;border-radius:8px;"
                        f"padding:.35rem .5rem;font-size:.68rem;font-weight:600;"
                        f"text-align:center;margin-bottom:.4rem;'>"
                        f"T{tp['topic_id']}<br>"
                        f"<span style='font-size:.58rem;opacity:.85;font-weight:400;'>{fmt_time(tp['start_time'])}</span>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
            st.markdown("<br>", unsafe_allow_html=True)

        sent_topic={}
        for tp in topics:
            for s in tp.get("sentences",[]): sent_topic[s.get("sentence_id")]=tp

        html=""; cur_tid=None
        for s in sents:
            tp=sent_topic.get(s.get("sentence_id"))
            if tp and tp["topic_id"]!=cur_tid:
                cur_tid=tp["topic_id"]
                c=TOPIC_COLORS[(cur_tid-1)%len(TOPIC_COLORS)]
                html+=(f"<div class='ts-divider' style='background:{c}18;color:{c};"
                       f"border-left:3px solid {c};'>Topic {cur_tid} — {tp['label']}</div>")
            html+=(f"<div class='ts-line'><span class='ts-time'>{fmt_time(s.get('start'))}</span>"
                   f"{s.get('text','')}</div>")

        st.markdown(f'<div class="ts-wrap">{html}</div>', unsafe_allow_html=True)
        st.caption(f"📝 {len(sents)} sentences · {basic.get('total_words',0):,} words · Scroll to read full transcript")

    # ══════════════════════════════════════
    # TAB 2 — TOPICS & SUMMARIES
    # ══════════════════════════════════════
    with t2:
        if eval_res:
            score=eval_res.get("overall_score",0)
            color="#16a34a" if score>=7 else ("#d97706" if score>=5 else "#dc2626")
            grade="Good" if score>=7 else ("Fair" if score>=5 else "Needs Adjustment")
            qa,qb=st.columns([1,3])
            with qa:
                st.markdown(
                    f"<div style='background:#fff;border:1px solid #e2e8f0;border-radius:14px;"
                    f"padding:1.2rem;text-align:center;box-shadow:0 1px 4px rgba(0,0,0,.05);'>"
                    f"<div style='font-size:2.5rem;font-weight:700;color:{color};line-height:1;'>{score:.1f}</div>"
                    f"<div style='font-size:.62rem;color:#94a3b8;'>/10</div>"
                    f"<div style='font-size:.8rem;font-weight:600;color:{color};margin-top:.4rem;'>{grade}</div>"
                    f"<div style='font-size:.68rem;color:#94a3b8;'>Segmentation Quality</div></div>",
                    unsafe_allow_html=True,
                )
            with qb:
                st.markdown("**What does this mean?**")
                for fb in eval_res.get("feedback",[]): st.markdown(f"- {fb}")
            st.markdown("<br>", unsafe_allow_html=True)

        if len(topics)==1:
            st.warning(
                "⚠️ **Only 1 topic detected.** The block size may be too large for this audio. "
                "Try: **Sidebar → Topic Sensitivity → reduce to 3–5** → click **New File** and re-run."
            )

        st.markdown(f'<div class="sec-head">Topic Segments ({len(topics)} found)</div>',
                    unsafe_allow_html=True)

        for tp in topics:
            c=TOPIC_COLORS[(tp["topic_id"]-1)%len(TOPIC_COLORS)]
            ss=tp.get("sentiment_score",0)
            sent_icon="😊 Positive" if ss>0.1 else ("😔 Negative" if ss<-0.1 else "😐 Neutral")
            kw_html="".join(f"<span class='kw'>{k}</span>" for k in tp.get("keywords",[]))
            st.markdown(
                f'<div class="tcard" style="border-left-color:{c};">'
                f'<div class="tcard-head">'
                f'<div class="tcard-title">📌 {tp.get("label","Topic")}</div>'
                f'<span class="tcard-badge" style="background:{c};">Topic {tp["topic_id"]}</span>'
                f'</div>'
                f'<div class="tcard-time">'
                f'⏱ {fmt_time(tp["start_time"])} → {fmt_time(tp["end_time"])} &nbsp;·&nbsp; '
                f'{tp.get("duration",0)/60:.1f} min &nbsp;·&nbsp; {tp["num_sentences"]} sentences &nbsp;·&nbsp; {sent_icon}'
                f'</div>'
                f'<div class="tcard-summary">{tp.get("summary","No summary available.")}</div>'
                f'<div class="kw-row">{kw_html}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        if cohesion:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**📉 Lexical Cohesion Chart**")
            st.caption("Valleys show where vocabulary shifts — these are the topic boundaries detected by the algorithm.")
            fig=go.Figure(go.Scatter(
                y=cohesion, mode="lines+markers",
                line=dict(color="#7c3aed",width=2.5),
                marker=dict(size=5,color="#7c3aed"),
                fill="tozeroy", fillcolor="rgba(124,58,237,.07)",
            ))
            fig.update_layout(
                height=200, margin=dict(l=20,r=20,t=10,b=30),
                paper_bgcolor="#fff", plot_bgcolor="#fafafa",
                font=dict(color="#64748b",family="JetBrains Mono"),
                yaxis=dict(gridcolor="#f1f5f9",title="Cohesion Score"),
                xaxis=dict(gridcolor="#f1f5f9",title="Block Number"),
                showlegend=False,
            )
            st.plotly_chart(fig, width="stretch")

    # ══════════════════════════════════════
    # TAB 3 — ANALYTICS
    # ══════════════════════════════════════
    with t3:
        st.markdown('<div class="sec-head">Audio Analytics</div>', unsafe_allow_html=True)

        col1,col2=st.columns(2)
        with col1:
            st.markdown("#### 🎙️ Speaking Patterns")
            wpm=speaking.get("words_per_minute",0)
            cat=speaking.get("speech_rate_category","")
            st.metric("Words per Minute", f"{wpm:.0f}", cat)
            st.metric("Avg Sentence Duration", f"{speaking.get('avg_sentence_duration',0):.1f}s",
                      help="Average length of each spoken sentence in seconds")
            st.metric("Total Pause Time", f"{speaking.get('total_pause_time',0):.1f}s",
                      help="Total silence detected between sentences")
            st.markdown("#### 📖 Vocabulary")
            st.metric("Unique Words",   f"{vocab.get('unique_words',0):,}")
            st.metric("Diversity Score",f"{vocab.get('vocabulary_diversity',0):.1%}",
                      help="Ratio of unique words to total. Higher = more varied language.")
            st.metric("Rare Words",     f"{vocab.get('hapax_legomena',0):,}",
                      help="Words appearing exactly once — indicator of rich vocabulary")
        with col2:
            rd=analytics.get("readability",{})
            if "error" not in rd:
                st.markdown("#### 📚 Readability Scores")
                st.metric("Reading Level",        rd.get("reading_level","—"),
                          help="Approximate education level needed to understand this content")
                st.metric("Flesch–Kincaid Grade", f"{rd.get('flesch_kincaid_grade',0):.1f}",
                          help="US school grade level. Lower = easier.")
                st.metric("Flesch Reading Ease",  f"{rd.get('flesch_reading_ease',0):.1f}",
                          help="0–100. Higher = easier. 60–70 is ideal for general audiences.")
                st.metric("Gunning Fog Index",    f"{rd.get('gunning_fog',0):.1f}",
                          help="Years of education needed. Under 12 is ideal for general audiences.")
            else:
                st.info("💡 Install **textstat** for readability scores:\n```\npip install textstat\n```")

        st.markdown("---")

        top_words=vocab.get("top_10_words",[])
        if top_words:
            wc_col, bar_col = st.columns([1,1])

            # ── WORD CLOUD ───────────────────────────────────────────────
            with wc_col:
                st.markdown("#### ☁️ Word Cloud")
                try:
                    from wordcloud import WordCloud
                    import matplotlib.pyplot as plt

                    # Build full word frequency dict from all sentences
                    full_text = " ".join(s.get("text","") for s in sents)
                    wc = WordCloud(
                        width=600, height=340,
                        background_color="white",
                        colormap="RdPu",
                        max_words=80,
                        prefer_horizontal=0.85,
                        collocations=False,
                        margin=6,
                        font_path=None,
                    ).generate(full_text)

                    fig_wc, ax = plt.subplots(figsize=(6,3.4))
                    ax.imshow(wc, interpolation="bilinear")
                    ax.axis("off")
                    fig_wc.patch.set_facecolor("white")
                    plt.tight_layout(pad=0)
                    st.pyplot(fig_wc)
                    plt.close(fig_wc)

                except ImportError:
                    st.info("💡 Install **wordcloud** to enable this:\n```\npip install wordcloud\n```")
                except Exception as e:
                    st.warning(f"Word cloud error: {e}")

            # ── BAR CHART ────────────────────────────────────────────────
            with bar_col:
                st.markdown("#### 🔤 Top 10 Words")
                words_=[w[0] for w in top_words]; freqs_=[w[1] for w in top_words]
                fig_wf=go.Figure(go.Bar(
                    x=freqs_[::-1], y=words_[::-1], orientation="h",
                    marker=dict(color=freqs_[::-1],colorscale=[[0,"#e9d5ff"],[1,"#7c3aed"]],showscale=False),
                    text=freqs_[::-1], textposition="outside",
                ))
                fig_wf.update_layout(
                    height=340, margin=dict(l=10,r=60,t=10,b=20),
                    paper_bgcolor="#fff", plot_bgcolor="#fafafa",
                    font=dict(color="#64748b",family="JetBrains Mono",size=11),
                    xaxis=dict(gridcolor="#f1f5f9",title="Frequency"),
                    yaxis=dict(gridcolor="#f1f5f9"),
                )
                st.plotly_chart(fig_wf, width="stretch")

        tl=analytics.get("sentiment",{}).get("timeline",[])
        if tl:
            st.markdown("#### 💭 Sentiment Over Time")
            st.caption("Above 0 = positive tone, below 0 = negative tone. Shows emotional shifts throughout the podcast.")
            fig_s=go.Figure()
            fig_s.add_trace(go.Scatter(
                x=[t["time"] for t in tl], y=[t["polarity"] for t in tl],
                mode="lines", line=dict(color="#7c3aed",width=1.5),
                fill="tozeroy", fillcolor="rgba(124,58,237,.06)",
            ))
            fig_s.add_hline(y=0, line_dash="dot", line_color="#cbd5e1")
            fig_s.update_layout(
                height=200, margin=dict(l=20,r=20,t=10,b=30),
                paper_bgcolor="#fff", plot_bgcolor="#fafafa",
                font=dict(color="#64748b",family="JetBrains Mono",size=11),
                xaxis=dict(title="Time (seconds)",gridcolor="#f1f5f9"),
                yaxis=dict(title="Polarity",gridcolor="#f1f5f9",range=[-1.1,1.1]),
                showlegend=False,
            )
            st.plotly_chart(fig_s, width="stretch")

        if topics:
            if len(topics)>1:
                st.markdown("#### 🥧 Topic Duration Split")
                fig_p=px.pie(
                    values=[t["duration"] for t in topics],
                    names=[f"T{t['topic_id']}: {t['label'][:18]}" for t in topics],
                    color_discrete_sequence=TOPIC_COLORS,
                )
                fig_p.update_traces(textposition="inside", textinfo="percent+label")
                fig_p.update_layout(
                    height=320, paper_bgcolor="#fff",
                    font=dict(color="#334155",family="JetBrains Mono",size=11),
                    margin=dict(t=20,b=20),
                )
                st.plotly_chart(fig_p, width="stretch")
            else:
                st.info(f"ℹ️ The entire {dur/60:.1f}-minute recording was 1 topic. "
                        f"Reduce block size (sidebar) for a topic duration chart.")

    # ══════════════════════════════════════
    # TAB 4 — SEARCH
    # ══════════════════════════════════════
    with t4:
        st.markdown('<div class="sec-head">Search Transcript</div>', unsafe_allow_html=True)
        st.markdown("Find any word or phrase and see exactly **when** it was spoken.")

        query=st.text_input("🔍 Search keyword or phrase",
            placeholder="e.g. machine learning, revenue, climate change",
            label_visibility="visible")

        if not query:
            st.markdown(
                '<div class="empty-state">'
                '<div class="empty-icon">🔍</div>'
                '<div class="empty-title">Type a keyword above to search</div>'
                '<div class="empty-desc">Search is instant and case-insensitive.<br>'
                'Results show the timestamp and topic for each match.</div>'
                '</div>', unsafe_allow_html=True,
            )
        else:
            import re as _re
            hits=[s for s in sents if query.lower() in s.get("text","").lower()]
            if not hits:
                st.warning(f"No results for **'{query}'**. Try a different keyword or check spelling.")
            else:
                st.success(f"✅ Found **{len(hits)} result{'s' if len(hits)!=1 else ''}** for **'{query}'**")
                for h in hits:
                    tp_badge=""
                    for tp in topics:
                        if any(s.get("sentence_id")==h.get("sentence_id") for s in tp.get("sentences",[])):
                            c=TOPIC_COLORS[(tp["topic_id"]-1)%len(TOPIC_COLORS)]
                            tp_badge=(f"<span style='background:{c};color:#fff;border-radius:4px;"
                                      f"padding:.1rem .4rem;font-size:.6rem;font-weight:600;"
                                      f"margin-left:.4rem;'>T{tp['topic_id']}: {tp['label'][:20]}</span>")
                            break
                    hi=_re.sub(
                        f"({_re.escape(query)})",
                        r"<mark style='background:#ddd6fe;color:#5b21b6;border-radius:3px;"
                        r"padding:0 .15rem;font-weight:600;'>\1</mark>",
                        h.get("text",""), flags=_re.IGNORECASE,
                    )
                    st.markdown(
                        f'<div class="search-hit">'
                        f"<span class='ts-time'>{fmt_time(h.get('start'))}</span>"
                        f"{tp_badge}"
                        f"<span style='margin-left:.5rem;'>{hi}</span>"
                        f'</div>',
                        unsafe_allow_html=True,
                    )

    # ══════════════════════════════════════
    # TAB 5 — DOWNLOAD
    # ══════════════════════════════════════
    with t5:
        st.markdown('<div class="sec-head">Download Results</div>', unsafe_allow_html=True)
        st.markdown("Export your analysis in different formats.")
        fn=D.get("filename","audio")

        plain=" ".join(s.get("text","") for s in sents)
        timed="\n".join(f"[{fmt_time(s.get('start'))}] {s.get('text','')}" for s in sents)
        topics_txt="\n\n".join(
            f"━━━ Topic {t['topic_id']}: {t['label']} ━━━\n"
            f"Time     : {fmt_time(t['start_time'])} → {fmt_time(t['end_time'])}\n"
            f"Duration : {t.get('duration',0)/60:.1f} min\n"
            f"Keywords : {', '.join(t.get('keywords',[]))}\n"
            f"Summary  : {t.get('summary','')}"
            for t in topics
        )
        full_json=json.dumps({
            "filename":fn,"audio_duration":dur,"num_topics":len(topics),
            "topics":[{k:v for k,v in t.items() if k!="sentences"} for t in topics],
            "evaluation":eval_res,
            "analytics":{k:v for k,v in analytics.items() if k!="sentiment"},
        }, indent=2, default=str)

        d1,d2,d3,d4=st.columns(4)
        with d1:
            st.markdown('<div class="dl-card"><div class="dl-icon">📄</div>'
                        '<div class="dl-title">Plain Transcript</div>'
                        '<div class="dl-desc">Clean text, no timestamps.<br>Good for reading or pasting.</div></div>',
                        unsafe_allow_html=True)
            st.download_button("⬇️ Download .txt", data=plain,
                               file_name=f"{fn}_transcript.txt", mime="text/plain", width="stretch")
        with d2:
            st.markdown('<div class="dl-card"><div class="dl-icon">🕐</div>'
                        '<div class="dl-title">Timestamped</div>'
                        '<div class="dl-desc">Every sentence with its timecode.<br>Good for referencing moments.</div></div>',
                        unsafe_allow_html=True)
            st.download_button("⬇️ Download .txt", data=timed,
                               file_name=f"{fn}_timestamped.txt", mime="text/plain", width="stretch")
        with d3:
            st.markdown('<div class="dl-card"><div class="dl-icon">📚</div>'
                        '<div class="dl-title">Topics Report</div>'
                        '<div class="dl-desc">Keywords & summaries per topic.<br>Good for sharing highlights.</div></div>',
                        unsafe_allow_html=True)
            st.download_button("⬇️ Download .txt", data=topics_txt,
                               file_name=f"{fn}_topics.txt", mime="text/plain", width="stretch")
        with d4:
            st.markdown('<div class="dl-card"><div class="dl-icon">📦</div>'
                        '<div class="dl-title">Full JSON Report</div>'
                        '<div class="dl-desc">All data in structured format.<br>Good for developers & tools.</div></div>',
                        unsafe_allow_html=True)
            st.download_button("⬇️ Download .json", data=full_json,
                               file_name=f"{fn}_report.json", mime="application/json", width="stretch")

        st.markdown("<br>", unsafe_allow_html=True)
        st.info("💡 **Tip:** Use **Topics Report** for a human-readable summary. Use **Full JSON** to import data into other tools or scripts.")
   

   