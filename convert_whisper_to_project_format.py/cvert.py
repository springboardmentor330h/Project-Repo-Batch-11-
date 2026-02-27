import json
import os
from textblob import TextBlob

# Absolute path to transcripts folder
INPUT_FOLDER = r"C:\Users\ammu ayinavalli\Desktop\Automated_Podcast_project\transcripts"

for filename in os.listdir(INPUT_FOLDER):
    if filename.endswith(".json"):

        file_path = os.path.join(INPUT_FOLDER, filename)

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # If file already converted, skip
        if isinstance(data, list):
            print(f"Skipping {filename} (already converted)")
            continue

        segments_output = []

        # If whisper format with segments
        if "segments" in data:
            for i, seg in enumerate(data["segments"]):

                text = seg["text"].strip()

                sentiment_score = TextBlob(text).sentiment.polarity

                if sentiment_score > 0:
                    sentiment = "Positive"
                elif sentiment_score < 0:
                    sentiment = "Negative"
                else:
                    sentiment = "Neutral"

                segment_data = {
                    "title": f"{filename.replace('.json','')}_chunk{i}",
                    "text": text,
                    "summary": text[:120] + "...",
                    "keywords": text.split()[:5],
                    "sentiment": sentiment
                }

                segments_output.append(segment_data)

        # If simple text format
        elif "text" in data:
            text = data["text"].strip()

            sentiment_score = TextBlob(text).sentiment.polarity

            if sentiment_score > 0:
                sentiment = "Positive"
            elif sentiment_score < 0:
                sentiment = "Negative"
            else:
                sentiment = "Neutral"

            segments_output.append({
                "title": f"{filename.replace('.json','')}_chunk0",
                "text": text,
                "summary": text[:120] + "...",
                "keywords": text.split()[:5],
                "sentiment": sentiment
            })

        # Save converted format
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(segments_output, f, indent=4)

        print(f"Converted {filename}")

print("ALL FILES CONVERTED SUCCESSFULLY")
