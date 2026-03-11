import os
from wordcloud import WordCloud
import matplotlib.pyplot as plt


def generate_keyword_cloud(input_path,
                           output_folder="../output/keyword_clouds"):
    """
    Generate word cloud from a single keyword file.
    Returns generated image path.
    """

    os.makedirs(output_folder, exist_ok=True)

    # Read keyword text
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read().replace(",", " ")

    # Generate word cloud
    wc = WordCloud(
        width=800,
        height=400,
        background_color="white"
    ).generate(text)

    # Create output filename dynamically
    filename = os.path.basename(input_path)
    image_name = filename.replace(".txt", ".png")
    output_path = os.path.join(output_folder, image_name)

    # Save image
    plt.figure(figsize=(8, 4))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

    print("Keyword cloud generated successfully")

    return output_path


# Optional: run on entire folder if executed directly
if __name__ == "__main__":
    keywords_dir = "../dataset/topic_keywords"

    for file in os.listdir(keywords_dir):
        if file.endswith("_keywords.txt"):
            generate_keyword_cloud(os.path.join(keywords_dir, file))

    print("All keyword clouds generated.")