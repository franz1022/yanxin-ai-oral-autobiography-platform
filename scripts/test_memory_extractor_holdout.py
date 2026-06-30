from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.evaluate_memory_extractor import ALL_FIELDS, load_dataset


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEVELOPMENT_DATASET = (
    PROJECT_ROOT / "data" / "evaluation" / "memory_extraction_cases.json"
)
HOLDOUT_DATASET = (
    PROJECT_ROOT
    / "data"
    / "evaluation"
    / "memory_extraction_holdout_cases.json"
)


def _normalise_text(value: str) -> str:
    return " ".join(value.casefold().split())


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    development = load_dataset(DEVELOPMENT_DATASET)
    holdout = load_dataset(HOLDOUT_DATASET)

    cases = holdout["cases"]
    assert holdout.get("evaluation_role") == "holdout"
    assert len(cases) == 20

    languages = [case["language"] for case in cases]
    assert languages.count("zh") == 10
    assert languages.count("en") == 10

    difficulties = {case["difficulty"] for case in cases}
    assert difficulties == {"easy", "medium", "hard"}

    case_ids = [case["case_id"] for case in cases]
    assert len(case_ids) == len(set(case_ids))
    assert all(case_id.startswith("holdout_") for case_id in case_ids)

    development_texts = {
        _normalise_text(case["memory_text"])
        for case in development["cases"]
    }
    holdout_texts = [_normalise_text(case["memory_text"]) for case in cases]

    assert len(holdout_texts) == len(set(holdout_texts))
    assert not development_texts.intersection(holdout_texts)

    for case in cases:
        expected = case["expected"]
        assert set(ALL_FIELDS).issubset(expected)
        assert isinstance(case["memory_text"], str)
        assert case["memory_text"].strip()

    print("Memory extractor holdout integrity test completed successfully.")
    print("Cases: 20 (10 Chinese, 10 English).")
    print("No exact text overlap with the development benchmark.")
    print(f"Holdout dataset SHA-256: {_sha256(HOLDOUT_DATASET)}")
    print("The holdout labels are frozen and must not be used for rule tuning.")


if __name__ == "__main__":
    main()
