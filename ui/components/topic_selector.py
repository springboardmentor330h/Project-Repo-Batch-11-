import streamlit as st

def render_topic_selector(topics):


    st.subheader("📚 Step 2: Topic Navigation (Segment Jumping)")

    if not topics or not isinstance(topics, list):
        st.error("❌ No valid topics available.")
        return None

    topic_labels = []

    for idx, topic in enumerate(topics):
        summary = topic.get("summary", "").strip()
        if not summary:
            summary = "No summary available for this topic."

        topic_labels.append(f"Topic {idx + 1}: {summary}")

    selected_index = st.radio(
        "Select a topic to jump to:",
        options=list(range(len(topic_labels))),
        format_func=lambda i: topic_labels[i],
        index=0
    )

    return selected_index
