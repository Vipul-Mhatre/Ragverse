import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DATASET_PATH = REPO_ROOT / "data" / "sample_enterprise_dataset.json"


def load_documents() -> list[dict]:
    with DATASET_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)
