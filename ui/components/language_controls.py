import streamlit as st

LANGUAGE_OPTIONS = {
    "English": "en",
    "Hindi": "hi",
    "Telugu": "te",
    "Tamil": "ta",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Bengali": "bn",
    "Marathi": "mr",
    "Urdu": "ur",
    "Arabic": "ar",
    "Russian": "ru",
    "Chinese": "zh",
    "Japanese": "ja",
    "Korean": "ko"
}

def render_language_controls():

    st.subheader("🌍 Step 3: Translation")

    selected_language_name = st.selectbox(
        "Display transcript in:",
        options=list(LANGUAGE_OPTIONS.keys()),
        index=0
    )

    selected_language_code = LANGUAGE_OPTIONS[selected_language_name]

    localization_enabled = False

    if selected_language_code != "en":
        st.subheader("🈶 Step 4: Localization")
        localization_enabled = st.checkbox(
            "Enable localized readable form (romanized / local)",
            value=False
        )

    return selected_language_code, localization_enabled
