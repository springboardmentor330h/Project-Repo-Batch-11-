import os
import pandas as pd

# PATHS
RAW_DIR = "data/raw_transcripts/american_life"
OUT_DIR = "data/transcripts"

os.makedirs(OUT_DIR, exist_ok=True)

csv_path = os.path.join(RAW_DIR, "lines_clean.csv")

print("Reading CSV...")
df = pd.read_csv(csv_path)

print("Columns detected:", df.columns.tolist())

# REQUIRED COLUMNS
required_cols = {"episode_id", "line_text", "timestamp", "speaker"}
if not required_cols.issubset(df.columns):
    raise ValueError(f"CSV must contain columns: {required_cols}")

# TIMESTAMP PARSER
def time_to_seconds(t):
    """
    Supports:
    mm:ss
    mm:ss.s
    hh:mm:ss
    hh:mm:ss.s
    """
    parts = str(t).split(":")

    if len(parts) == 2:
        m, s = parts
        return int(m) * 60 + float(s)

    elif len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + float(s)

    else:
        raise ValueError(f"Unrecognized timestamp format: {t}")

# PREPROCESS
print("Normalizing timestamps...")
df["start_sec"] = df["timestamp"].apply(time_to_seconds)

# Sort properly
df = df.sort_values(["episode_id", "start_sec"])

# Generate end time using next utterance
df["end_sec"] = df.groupby("episode_id")["start_sec"].shift(-1)
df["end_sec"] = df["end_sec"].fillna(df["start_sec"] + 2.0)

# WRITE TRANSCRIPTS 
print("Generating speaker-attributed transcripts...")

for episode_id, group in df.groupby("episode_id"):
    lines = []

    for _, row in group.iterrows():
        speaker = str(row["speaker"]).strip().upper()
        text = str(row["line_text"]).strip()

        if not text:
            continue

        start = row["start_sec"]
        end = row["end_sec"]

        lines.append(
            f"[{start:.2f} - {end:.2f}] {speaker}: {text}"
        )

    if not lines:
        continue

    out_file = os.path.join(OUT_DIR, f"episode_{episode_id}.txt")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✔ Created episode_{episode_id}.txt")

print("\n Completed: Speaker-aware transcripts generated")