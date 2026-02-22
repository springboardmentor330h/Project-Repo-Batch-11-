
import re
from sklearn.feature_extraction.text import TfidfVectorizer

MAX_KEYWORDS = 6
MIN_KEYWORDS = 3

STOPWORDS = {
    "the","a","an","this","that","these","those",
    "i","you","he","she","it","we","they","them","their","our","your",
    "is","are","was","were","be","been","being",
    "have","has","had","do","does","did",
    "can","could","may","might","must","shall","should","will","would",
    "and","or","but","so","because","for","with","without",
    "from","to","in","on","at","by","of","as","about","into","over","after",
    "now","then","here","there","okay","alright","yes","no",
    "just","like","well","also","very","basically","actually",
    "use","used","using","say","said","tell","told",
    "give","given","get","got","take","put","make",
    "look","see","go","come","want","need","think","know","remember",
    "podcast","episode","page","video","audio","channel",
    "lesson","today","next","again","always",
}


def tokenize(text):
    words = re.findall(r"[a-zA-Z]{3,}", text.lower())
    return [w for w in words if w not in STOPWORDS]

def clean_keyword(word):
    if word.endswith(("ing","ed","ly")):
        return False
    if re.search(r"(.)\1\1", word):
        return False
    return True

def extract_phrases(text, max_ngram=2):
    try:
        vectorizer = TfidfVectorizer(
            tokenizer=tokenize,
            ngram_range=(1, max_ngram),
            max_features=50
        )
        tfidf = vectorizer.fit_transform([text])
        scores = dict(zip(
            vectorizer.get_feature_names_out(),
            tfidf.toarray()[0]
        ))
        return scores
    except ValueError:
        return {}


def extract_keywords(segments, summary_text=None):
    
        
    if isinstance(segments, str):
        full_text = segments
    else:
        full_text = " ".join(s.get("text","") for s in segments)
    
    if not full_text.strip():
        return ["general topic", "discussion", "content"]
    
    scores = extract_phrases(full_text, max_ngram=2)
    
    if not scores:
        words = tokenize(full_text)
        from collections import Counter
        word_counts = Counter(words)
        keywords = [w for w, _ in word_counts.most_common(MAX_KEYWORDS) if clean_keyword(w)]
        return keywords[:MAX_KEYWORDS] if keywords else ["topic", "discussion"]
    
    keywords = []
    summary_lower = summary_text.lower() if summary_text else ""
    
    for keyword, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        parts = keyword.split()
        if all(clean_keyword(p) for p in parts):
            if summary_text and keyword in summary_lower:
                keywords.insert(0, keyword)
            else:
                keywords.append(keyword)
        
        if len(keywords) >= MAX_KEYWORDS:
            break
    
    if len(keywords) < MIN_KEYWORDS:
        words = tokenize(full_text)
        from collections import Counter
        word_counts = Counter(words)
        
        for word, _ in word_counts.most_common(20):
            if clean_keyword(word) and word not in keywords:
                keywords.append(word)
            if len(keywords) >= MIN_KEYWORDS:
                break
    
    return keywords[:MAX_KEYWORDS] if keywords else ["topic", "content", "discussion"]
