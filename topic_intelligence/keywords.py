from keybert import KeyBERT

kw_model = KeyBERT(model="all-MiniLM-L6-v2")

def extract_keywords(text, top_n=5):
    keywords = kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 2),
        stop_words="english",
        top_n=top_n
    )
    return [kw[0] for kw in keywords]
