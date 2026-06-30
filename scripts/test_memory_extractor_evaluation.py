from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pandas as pd

from scripts.evaluate_memory_extractor import (
    ALL_FIELDS,
    CORE_FIELDS,
    DEFAULT_DATASET_PATH,
    evaluate_dataset,
    load_dataset,
)


def main() -> None:
    dataset = load_dataset(DEFAULT_DATASET_PATH)

    assert dataset["dataset_name"] == "Yanxin Memory Extraction Evaluation Set"
    assert len(dataset["cases"]) == 24
    assert {case["language"] for case in dataset["cases"]} == {"zh", "en"}
    assert len({case["case_id"] for case in dataset["cases"]}) == 24

    with tempfile.TemporaryDirectory() as temporary_directory:
        output_dir = Path(temporary_directory)
        summary = evaluate_dataset(DEFAULT_DATASET_PATH, output_dir)

        required_outputs = {
            "memory_extraction_case_results.csv",
            "memory_extraction_field_metrics.csv",
            "memory_extraction_language_metrics.csv",
            "memory_extraction_difficulty_metrics.csv",
            "memory_extraction_error_analysis.csv",
            "memory_extraction_summary.json",
        }
        assert required_outputs == {path.name for path in output_dir.iterdir()}

        case_df = pd.read_csv(output_dir / "memory_extraction_case_results.csv")
        field_df = pd.read_csv(output_dir / "memory_extraction_field_metrics.csv")
        language_df = pd.read_csv(
            output_dir / "memory_extraction_language_metrics.csv"
        )

        assert len(case_df) == 24
        assert set(field_df["field"]) == set(ALL_FIELDS)
        assert set(language_df["language"]) == {"zh", "en"}
        assert summary["total_cases"] == 24
        assert summary["review_required_rate"] == 1.0
        assert 0.0 <= summary["core_field_micro_accuracy"] <= 1.0
        assert 0.0 <= summary["core_complete_record_accuracy"] <= 1.0
        assert summary["language_detection_accuracy"] == 1.0

        for field in CORE_FIELDS:
            assert f"match_{field}" in case_df.columns

        with (output_dir / "memory_extraction_summary.json").open(
            "r",
            encoding="utf-8",
        ) as file:
            saved_summary = json.load(file)

        assert saved_summary["total_cases"] == 24
        assert saved_summary["dataset_version"] == "1.0.0"

    print("Memory extractor evaluation test completed successfully.")
    print("Dataset integrity, metrics and output files all passed.")


if __name__ == "__main__":
    main()
