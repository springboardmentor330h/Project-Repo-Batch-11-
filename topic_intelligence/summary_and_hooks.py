import nltk
from nltk.tokenize import sent_tokenize

nltk.download("punkt")

def generate_title(text):
    sentences = sent_tokenize(text)
    return sentences[0][:60] if sentences else "Topic Overview"

def generate_hook(text):
    sentences = sent_tokenize(text)
    if len(sentences) >= 2:
        return f"Why listen: {sentences[0]} {sentences[1]}"
    elif sentences:
        return f"Why listen: {sentences[0]}"
    return "Why listen: Key discussion in this segment."

def generate_questions(text, max_q=3):
    sentences = sent_tokenize(text)
    questions = []
    for s in sentences[:max_q]:
        questions.append(f"What does the speaker mean by: '{s[:50]}…'?")
    return questions
