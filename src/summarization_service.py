import nltk
from rake_nltk import Rake
from transformers import pipeline
import os

# Download NLTK stopwords
nltk.download('stopwords')
nltk.download('punkt')

class Summarizer:
    def __init__(self, model_name="t5-small"):
        print(f"Loading summarization model: {model_name}...")
        # Use a lightweight pipeline for speed
        self.summarizer = pipeline("summarization", model=model_name, device=-1) # -1 for CPU
        self.rake = Rake()

    def extract_keywords(self, text, top_n=5):
        """
        Extracts keywords using RAKE.
        """
        self.rake.extract_keywords_from_text(text)
        keywords = self.rake.get_ranked_phrases()
        return keywords[:top_n]

    def generate_summary(self, text, max_length=150, min_length=40):
        """
        Generates a polished 2-3 sentence summary using a Transformer model.
        """
        if len(text.split()) < 20:
            return text  # Too short to summarize meaningfully
        
        try:
            # T5 handles the 'summarize: ' prefix internally with the summarization pipeline
            summary_res = self.summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
            summary = summary_res[0]['summary_text']
            
            # Post-processing for conciseness: ensure it doesn't end abruptly and is around 2-3 sentences.
            sentences = nltk.sent_tokenize(summary)
            if len(sentences) > 3:
                summary = " ".join(sentences[:3])
            
            return summary.strip()
        except Exception as e:
            print(f"Summarization error: {e}")
            return "Summary generation failed for this segment."

    def generate_title(self, text, summary=None, max_new_tokens=10):
        """
        Generates a professional conceptual podcast chapter title.
        Uses a QA-style prompt which often performs better for short-form extraction.
        """
        # Focus on the summary for the highest conceptual density
        input_content = summary if summary and len(summary.split()) > 10 else text
        
        try:
            # Explicit prompt for conceptual titling
            prompt = f"question: what is the 3-word title of this? context: {input_content}"
            # Use the underlying model to generate directly for more control
            title_res = self.summarizer(prompt, max_new_tokens=max_new_tokens, min_new_tokens=3, do_sample=False)
            title = title_res[0]['summary_text'].strip(". \"'").title()
            
            # Post-cleanup: filter out generic lead-ins
            words = title.split()
            if any(words[0].lower() == w for w in ["the", "a", "it", "this", "he"]):
                title = " ".join(words[1:])
            
            # If the result is a long sentence or too short, use refined keywords
            if len(title.split()) > 5 or len(title.split()) < 2:
                self.rake.extract_keywords_from_text(text)
                # Select the top conceptual phrase (2-3 words)
                concepts = [p.title() for p in self.rake.get_ranked_phrases() if 1 < len(p.split()) <= 3]
                if concepts:
                    title = concepts[0]
                else:
                    title = " ".join(title.split()[:4])

            # Ensure it fits the 'Campaign Clash Over Medicare' length
            if len(title.split()) > 6:
                title = " ".join(title.split()[:5])
                
            return title
        except Exception as e:
            return "Untitled Chapter"

if __name__ == "__main__":
    # Test
    sample_segment = (
        "The economy is facing significant challenges as inflation continues to rise. "
        "The Federal Reserve is contemplating further interest rate hikes to stabilize the market. "
        "Experts suggest that these measures are necessary to prevent a long-term recession, "
        "although they acknowledge the immediate burden on consumers and small businesses."
    )
    
    gen = Summarizer()
    print("\nKeywords:", gen.extract_keywords(sample_segment))
    print("\nSummary:", gen.generate_summary(sample_segment))
