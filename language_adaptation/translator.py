
"""
translator.py - Multi-language translation using deep-translator
"""

try:
    from deep_translator import GoogleTranslator
    USE_DEEP_TRANSLATOR = True
except ImportError:
    USE_DEEP_TRANSLATOR = False

from transformers import MarianMTModel, MarianTokenizer

_MODEL_CACHE = {}


def _load_model(source_lang: str, target_lang: str):
    model_name = f"Helsinki-NLP/opus-mt-{source_lang}-{target_lang}"

    if model_name in _MODEL_CACHE:
        return _MODEL_CACHE[model_name]

    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)

    _MODEL_CACHE[model_name] = (tokenizer, model)
    return tokenizer, model


def chunk_text(text: str, max_chars: int = 4500) -> list[str]:
    """
    Split text into chunks of at most max_chars, trying to split at sentence endings.
    """
    if len(text) <= max_chars:
        return [text]
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    # Split by simple sentence delimiters
    sentences = text.replace('? ', '?. ').replace('! ', '!. ').split('. ')
    
    for sentence in sentences:
        # Add the period back if it was removed
        if not sentence.endswith(('.', '?', '!')):
            sentence += '.'
            
        sent_len = len(sentence)
        if current_length + sent_len < max_chars:
            current_chunk.append(sentence)
            current_length += sent_len
        else:
            # If a single sentence is huge (unlikely but possible), force split it
            if not current_chunk:
                chunks.append(sentence[:max_chars])
                if len(sentence) > max_chars:
                     # Recursive chunking for the remainder
                     chunks.extend(chunk_text(sentence[max_chars:], max_chars))
            else:
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_length = sent_len
                
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    return chunks

def translate_auto(text: str, source_lang: str, target_lang: str) -> str:
    """
    Translate text from source language to target language.
    Uses deep-translator (Google Translate) with chunking support.
    """
    if not text.strip():
        return text

    if source_lang == target_lang:
        return text
    
    # Try deep-translator (Google) with retries
    if USE_DEEP_TRANSLATOR:
        try:
            from deep_translator import MyMemoryTranslator
            import time
            
            # GoogleTranslator expects language codes like 'en', 'te', 'hi'
            translator = GoogleTranslator(source=source_lang, target=target_lang)
            
            # Handle long text via chunking
            chunks = chunk_text(text)
            translated_chunks = []
            
            for chunk in chunks:
                chunk_translated = False
                
                # Retry loop for Google Translator
                for attempt in range(3):
                    try:
                        res = translator.translate(chunk)
                        if res:
                            translated_chunks.append(res)
                            chunk_translated = True
                            break
                    except Exception:
                        time.sleep(1) # Backoff
                
                # If Google fails, try MyMemory as secondary API fallback
                if not chunk_translated:
                    try:
                        res = MyMemoryTranslator(source=source_lang, target=target_lang).translate(chunk)
                        if res:
                            translated_chunks.append(res)
                            chunk_translated = True
                    except Exception:
                        pass
                
                # If both fail for a chunk, we could potentially use local model JUST for this chunk,
                # but mixing models might look weird. For now we will rely on the main catch-all to switch entire mechanism?
                # Actually, better to use local model for this chunk if API failed!
                if not chunk_translated:
                    raise Exception("Chunk translation failed")

            return " ".join(translated_chunks)
            
        except Exception as e:
            print(f"Deep Translator error: {e}")
            pass  # Fall through to Helsinki-NLP
    
    # Fallback to Helsinki-NLP
    try:
        tokenizer, model = _load_model(source_lang, target_lang)
        # Handle chunking for local model too (max 512 tokens -> approx 2000 chars safe bet)
        chunks = chunk_text(text, max_chars=1500)
        translated_chunks = []
        
        for chunk in chunks:
            inputs = tokenizer(chunk, return_tensors="pt", truncation=True)
            translated = model.generate(**inputs)
            out = tokenizer.decode(translated[0], skip_special_tokens=True)
            if out:
                translated_chunks.append(out.strip())
                
        return " ".join(translated_chunks) if translated_chunks else text
    except Exception:
        # If both fail, return original
        return text
