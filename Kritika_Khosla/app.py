import streamlit as st
import requests
import tempfile
import os

# Backend API URL
API_URL = "http://127.0.0.1:8000/analyze/"

st.set_page_config(
    page_title="PodIntel AI",
    layout="wide"
)

st.title("🎙 PodIntel AI")
st.markdown("Upload a podcast/audio file and get topic insights instantly.")

# -------------------------
# Session History Storage
# -------------------------
if "session_history" not in st.session_state:
    st.session_state.session_history = []

# -------------------------
# Sidebar - Previous Sessions
# -------------------------
st.sidebar.title("📁 Previous Sessions")

if st.session_state.session_history:
    for session in st.session_state.session_history:
        if st.sidebar.button(session["session_id"]):
            st.write(f"## Session: {session['session_id']}")
            for idx, topic in enumerate(session["topics"], start=1):
                with st.expander(f"📌 Topic {idx}", expanded=False):
                    st.subheader("Summary")
                    st.write(topic.get("summary", "N/A"))

                    st.subheader("Sentiment")
                    st.write(topic.get("sentiment", "N/A"))

                    st.subheader("Keywords")
                    keywords = topic.get("keywords", [])
                    if isinstance(keywords, list):
                        st.write(", ".join(keywords))
                    else:
                        st.write(keywords)
else:
    st.sidebar.info("No sessions yet.")

# -------------------------
# File Upload Section
# -------------------------
uploaded_file = st.file_uploader(
    "Upload Podcast Audio",
    type=["wav", "mp3"]
)

if uploaded_file:

    # Save temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(uploaded_file.read())
        temp_file_path = tmp.name

    st.info("Processing audio... Please wait ⏳")

    try:
        with open(temp_file_path, "rb") as audio_file:
            response = requests.post(
                API_URL,
                files={"file": audio_file},
                timeout=None
            )

        if response.status_code == 200:
            data = response.json()

            session_id = data.get("session_id")
            result = data.get("result", {})
            topics = result.get("topics", [])

            st.success("Analysis Completed ✅")
            st.write(f"### Session ID: `{session_id}`")

            # Save session to history
            st.session_state.session_history.insert(0, {
                "session_id": session_id,
                "topics": topics
            })

            # Display results
            for idx, topic in enumerate(topics, start=1):
                with st.expander(f"📌 Topic {idx}", expanded=True):
                    st.subheader("Summary")
                    st.write(topic.get("summary", "N/A"))

                    st.subheader("Sentiment")
                    st.write(topic.get("sentiment", "N/A"))

                    st.subheader("Keywords")
                    keywords = topic.get("keywords", [])
                    if isinstance(keywords, list):
                        st.write(", ".join(keywords))
                    else:
                        st.write(keywords)

        else:
            st.error(f"Backend Error (Status Code: {response.status_code})")
            st.text(response.text)

    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend server.")
        st.info("Make sure backend is running:\n\nuvicorn backend.main:app --reload")

    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")

    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

else:
    st.info("Please upload an audio file to begin analysis.")