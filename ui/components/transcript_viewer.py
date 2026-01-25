import streamlit as st

def render_transcript(topic, language_code: str, localization_enabled: bool):

    st.subheader("📄 Step 5: Transcript View (Selected Topic)")

    sentences = topic.get("sentences", [])

    if not sentences:
        st.warning("No transcript sentences available for this topic.")
        return None

    topic_start_time = sentences[0].get("start", 0.0)

    for sent in sentences:
        if language_code == "en":
            display_text = sent.get("text", "")
        else:
            if localization_enabled:
                display_text = (
                    sent.get("romanized")
                    or sent.get("translation")
                    or sent.get("text", "")
                )
            else:
                display_text = sent.get("translation") or sent.get("text", "")

        if display_text.strip():
            st.write(display_text)

    return topic_start_time
