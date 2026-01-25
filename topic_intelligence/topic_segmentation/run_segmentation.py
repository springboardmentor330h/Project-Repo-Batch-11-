
import subprocess
import sys
from pathlib import Path

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent

def run_segmentation(input_json: str, algorithm: str):
    # Run as a module to allow relative imports
    cmd = [
        sys.executable,
        "-m",
        "topic_intelligence.topic_segmentation.topic_segmentation_core",
        input_json,
        algorithm
    ]

    print(f"[RUNNING] Running topic segmentation [{algorithm}]")
    subprocess.run(cmd, check=True, cwd=str(PROJECT_ROOT))
    print("[SUCCESS] Topic segmentation completed")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_segmentation.py <pipeline_output.json> [algorithm]")
        sys.exit(1)

    input_json = sys.argv[1]
    algorithm = sys.argv[2] if len(sys.argv) > 2 else "baseline_similarity"

    run_segmentation(input_json, algorithm)
