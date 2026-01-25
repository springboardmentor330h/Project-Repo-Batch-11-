import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()

PYTHON = PROJECT_ROOT / "venv" / "Scripts" / "python.exe"

PIPELINE_OUTPUT = PROJECT_ROOT / "pipeline_output.json"
SEGMENTED_OUTPUT = PROJECT_ROOT / "segmented_output.json"
INDEXED_OUTPUT = PROJECT_ROOT / "indexed_output.json"


def run_step(name, command):
    print(f"\n[RUNNING] {name}...")
    try:
        subprocess.run(
            command,
            check=True,
            cwd=PROJECT_ROOT
        )
        print(f"[SUCCESS] {name} completed")
    except subprocess.CalledProcessError:
        print(f"[ERROR] {name} failed")
        raise


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python pipeline_runner.py <audio_file>")
        sys.exit(1)

    audio_path = Path(sys.argv[1]).resolve()

    run_step(
        "pipeline_core",
        [str(PYTHON), "pipeline_core.py", str(audio_path)]
    )

    run_step(
        "topic_segmentation_core",
        [str(PYTHON), "topic_segmentation_core.py", str(PIPELINE_OUTPUT)]
    )

    run_step(
        "indexing_core",
        [str(PYTHON), "indexing_core.py", str(SEGMENTED_OUTPUT)]
    )

    run_step(
        "pipeline_validation_core",
        [str(PYTHON), "pipeline_validation_core.py", str(INDEXED_OUTPUT)]
    )

    print("\n[SUCCESS] FULL PIPELINE COMPLETED SUCCESSFULLY")
    print(f"Final output → {INDEXED_OUTPUT}")
