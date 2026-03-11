import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def segment_topics(
    input_folder,
    output_folder="../dataset/topic_segments_baseline",
    min_df=2
):
    """
    Segment merged transcript blocks into topic-based groups
    using TF-IDF cosine similarity.

    Returns list of generated topic file paths.
    """

    if not os.path.exists(input_folder):
        print("Input folder does not exist.")
        return []

    os.makedirs(output_folder, exist_ok=True)

    files = sorted(
        [f for f in os.listdir(input_folder) if f.endswith(".txt")]
    )

    if len(files) < 2:
        print("Not enough documents to perform segmentation.")
        return []

    documents = []
    for f in files:
        with open(os.path.join(input_folder, f), "r", encoding="utf-8") as file:
            documents.append(file.read().strip())

    # TF-IDF Vectorization
    vectorizer = TfidfVectorizer(
        stop_words="english",
        min_df=min_df
    )

    tfidf = vectorizer.fit_transform(documents)

    # Compute similarity between consecutive blocks
    similarities = []
    for i in range(len(documents) - 1):
        sim = cosine_similarity(tfidf[i], tfidf[i + 1])[0][0]
        similarities.append(sim)

    if not similarities:
        print("No similarity values computed.")
        return []

    threshold = sum(similarities) / len(similarities)

    segments = []
    current_segment = [0]

    for i, sim in enumerate(similarities):
        if sim < threshold:
            segments.append(current_segment)
            current_segment = []
        current_segment.append(i + 1)

    segments.append(current_segment)

    # Write topic files
    generated_files = []

    for idx, segment in enumerate(segments, start=1):
        output_path = os.path.join(output_folder, f"topic_{idx:02d}.txt")

        with open(output_path, "w", encoding="utf-8") as out:
            for block_index in segment:
                out.write(f"===== {files[block_index]} =====\n")
                out.write(documents[block_index] + "\n\n")

        generated_files.append(output_path)

    print(f"Created {len(segments)} topic segment files.")

    return generated_files


# Optional standalone execution
if __name__ == "__main__":
    INPUT_DIR = "../dataset/merged_transcripts"
    segment_topics(INPUT_DIR)