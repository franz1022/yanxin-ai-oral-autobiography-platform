from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from app.services.memory_extractor import extract_memory


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_PATH = (
    PROJECT_ROOT / "data" / "evaluation" / "memory_extraction_cases.json"
)
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "outputs" / "evaluation"


CORE_FIELDS = (
    "start_year",
    "end_year",
    "location",
    "people_involved",
    "emotional_tone",
)
SUPPORTING_FIELDS = (
    "detected_language",
    "event_title",
    "date_certainty",
)
ALL_FIELDS = SUPPORTING_FIELDS + CORE_FIELDS


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and pd.isna(value):
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


def _normalise_value(value: Any) -> Any:
    """Normalise values for deterministic exact-match evaluation."""
    if _is_missing(value):
        return None

    if isinstance(value, bool):
        return value

    if isinstance(value, int):
        return value

    if isinstance(value, float) and value.is_integer():
        return int(value)

    text = str(value).strip()
    text = text.replace("->", "→").replace("—>", "→")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s*→\s*", " → ", text)
    return text.casefold()


def _values_match(expected: Any, predicted: Any) -> bool:
    return _normalise_value(expected) == _normalise_value(predicted)


def _error_type(expected: Any, predicted: Any, is_match: bool) -> str:
    if is_match:
        return "match"
    if _is_missing(expected) and not _is_missing(predicted):
        return "false_positive"
    if not _is_missing(expected) and _is_missing(predicted):
        return "missed_value"
    return "wrong_value"


def load_dataset(dataset_path: Path) -> dict[str, Any]:
    with dataset_path.open("r", encoding="utf-8") as file:
        dataset = json.load(file)

    cases = dataset.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("Evaluation dataset must contain a non-empty 'cases' list.")

    case_ids = [case.get("case_id") for case in cases]
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("Every evaluation case must have a unique case_id.")

    for case in cases:
        if not case.get("memory_text", "").strip():
            raise ValueError(f"Case {case.get('case_id')} has empty memory_text.")
        expected = case.get("expected")
        if not isinstance(expected, dict):
            raise ValueError(f"Case {case.get('case_id')} has no expected labels.")
        missing_fields = [field for field in ALL_FIELDS if field not in expected]
        if missing_fields:
            raise ValueError(
                f"Case {case.get('case_id')} is missing expected fields: "
                f"{', '.join(missing_fields)}"
            )

    return dataset


def _build_case_rows(cases: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for case in cases:
        result = extract_memory(case["memory_text"])
        predicted = asdict(result)
        expected = case["expected"]

        row: dict[str, Any] = {
            "case_id": case["case_id"],
            "language": case["language"],
            "difficulty": case.get("difficulty", "unspecified"),
            "memory_text": case["memory_text"],
            "review_required": result.review_required,
            "extraction_method": result.extraction_method,
        }

        core_matches: list[bool] = []
        all_matches: list[bool] = []

        for field in ALL_FIELDS:
            expected_value = expected[field]
            predicted_value = predicted[field]
            is_match = _values_match(expected_value, predicted_value)

            row[f"expected_{field}"] = expected_value
            row[f"predicted_{field}"] = predicted_value
            row[f"match_{field}"] = is_match
            row[f"error_type_{field}"] = _error_type(
                expected_value,
                predicted_value,
                is_match,
            )

            all_matches.append(is_match)
            if field in CORE_FIELDS:
                core_matches.append(is_match)

        row["core_fields_correct"] = sum(core_matches)
        row["core_fields_total"] = len(CORE_FIELDS)
        row["core_field_accuracy"] = sum(core_matches) / len(CORE_FIELDS)
        row["core_complete_match"] = all(core_matches)
        row["all_fields_correct"] = sum(all_matches)
        row["all_fields_total"] = len(ALL_FIELDS)
        row["all_field_accuracy"] = sum(all_matches) / len(ALL_FIELDS)
        row["all_fields_complete_match"] = all(all_matches)
        rows.append(row)

    return rows


def _field_metrics(case_df: pd.DataFrame) -> pd.DataFrame:
    records: list[dict[str, Any]] = []

    for field in ALL_FIELDS:
        expected_col = f"expected_{field}"
        predicted_col = f"predicted_{field}"
        match_col = f"match_{field}"

        expected_present = ~case_df[expected_col].apply(_is_missing)
        predicted_present = ~case_df[predicted_col].apply(_is_missing)
        correct = case_df[match_col].astype(bool)
        correct_present = correct & expected_present & predicted_present

        expected_present_count = int(expected_present.sum())
        predicted_present_count = int(predicted_present.sum())
        correct_present_count = int(correct_present.sum())

        records.append(
            {
                "field": field,
                "field_group": "core" if field in CORE_FIELDS else "supporting",
                "total_cases": len(case_df),
                "correct_cases": int(correct.sum()),
                "accuracy": float(correct.mean()),
                "expected_present_cases": expected_present_count,
                "predicted_present_cases": predicted_present_count,
                "correct_present_cases": correct_present_count,
                "recall_on_expected_present": (
                    correct_present_count / expected_present_count
                    if expected_present_count
                    else 1.0
                ),
                "precision_on_predicted_present": (
                    correct_present_count / predicted_present_count
                    if predicted_present_count
                    else 1.0
                ),
                "missed_value_count": int(
                    (
                        case_df[f"error_type_{field}"] == "missed_value"
                    ).sum()
                ),
                "false_positive_count": int(
                    (
                        case_df[f"error_type_{field}"] == "false_positive"
                    ).sum()
                ),
                "wrong_value_count": int(
                    (case_df[f"error_type_{field}"] == "wrong_value").sum()
                ),
            }
        )

    return pd.DataFrame(records)


def _group_metrics(case_df: pd.DataFrame, group_column: str) -> pd.DataFrame:
    records: list[dict[str, Any]] = []

    for group_value, group in case_df.groupby(group_column, dropna=False):
        records.append(
            {
                group_column: group_value,
                "cases": len(group),
                "average_core_field_accuracy": float(
                    group["core_field_accuracy"].mean()
                ),
                "core_complete_records": int(group["core_complete_match"].sum()),
                "core_complete_record_accuracy": float(
                    group["core_complete_match"].mean()
                ),
                "average_all_field_accuracy": float(
                    group["all_field_accuracy"].mean()
                ),
                "all_fields_complete_records": int(
                    group["all_fields_complete_match"].sum()
                ),
                "all_fields_complete_record_accuracy": float(
                    group["all_fields_complete_match"].mean()
                ),
            }
        )

    return pd.DataFrame(records).sort_values(group_column).reset_index(drop=True)


def _error_analysis(case_df: pd.DataFrame) -> pd.DataFrame:
    errors: list[dict[str, Any]] = []

    for _, case in case_df.iterrows():
        for field in ALL_FIELDS:
            error_type = case[f"error_type_{field}"]
            if error_type == "match":
                continue

            errors.append(
                {
                    "case_id": case["case_id"],
                    "language": case["language"],
                    "difficulty": case["difficulty"],
                    "field": field,
                    "field_group": "core" if field in CORE_FIELDS else "supporting",
                    "error_type": error_type,
                    "expected": case[f"expected_{field}"],
                    "predicted": case[f"predicted_{field}"],
                    "memory_text": case["memory_text"],
                }
            )

    return pd.DataFrame(
        errors,
        columns=[
            "case_id",
            "language",
            "difficulty",
            "field",
            "field_group",
            "error_type",
            "expected",
            "predicted",
            "memory_text",
        ],
    )


def _summary(
    dataset: dict[str, Any],
    case_df: pd.DataFrame,
    field_df: pd.DataFrame,
    errors_df: pd.DataFrame,
) -> dict[str, Any]:
    core_rows = field_df[field_df["field_group"] == "core"]
    supporting_rows = field_df[field_df["field_group"] == "supporting"]

    return {
        "dataset_name": dataset.get("dataset_name"),
        "dataset_version": dataset.get("version"),
        "total_cases": len(case_df),
        "languages": sorted(case_df["language"].unique().tolist()),
        "core_fields": list(CORE_FIELDS),
        "supporting_fields": list(SUPPORTING_FIELDS),
        "core_field_micro_accuracy": float(core_rows["accuracy"].mean()),
        "supporting_field_micro_accuracy": float(
            supporting_rows["accuracy"].mean()
        ),
        "all_field_micro_accuracy": float(field_df["accuracy"].mean()),
        "core_complete_records": int(case_df["core_complete_match"].sum()),
        "core_complete_record_accuracy": float(
            case_df["core_complete_match"].mean()
        ),
        "all_fields_complete_records": int(
            case_df["all_fields_complete_match"].sum()
        ),
        "all_fields_complete_record_accuracy": float(
            case_df["all_fields_complete_match"].mean()
        ),
        "language_detection_accuracy": float(
            case_df["match_detected_language"].mean()
        ),
        "review_required_rate": float(case_df["review_required"].mean()),
        "total_field_errors": int(len(errors_df)),
        "error_type_counts": (
            errors_df["error_type"].value_counts().to_dict()
            if not errors_df.empty
            else {}
        ),
        "interpretation": (
            "This is a deterministic baseline evaluation on fictional labelled "
            "data. Results should be used for error analysis and workflow design, "
            "not as evidence of production readiness."
        ),
    }


def evaluate_dataset(
    dataset_path: Path = DEFAULT_DATASET_PATH,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    dataset_path = Path(dataset_path)
    output_dir = Path(output_dir)

    dataset = load_dataset(dataset_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    case_df = pd.DataFrame(_build_case_rows(dataset["cases"]))
    field_df = _field_metrics(case_df)
    language_df = _group_metrics(case_df, "language")
    difficulty_df = _group_metrics(case_df, "difficulty")
    errors_df = _error_analysis(case_df)
    summary = _summary(dataset, case_df, field_df, errors_df)

    case_df.to_csv(
        output_dir / "memory_extraction_case_results.csv",
        index=False,
        encoding="utf-8-sig",
    )
    field_df.to_csv(
        output_dir / "memory_extraction_field_metrics.csv",
        index=False,
        encoding="utf-8-sig",
    )
    language_df.to_csv(
        output_dir / "memory_extraction_language_metrics.csv",
        index=False,
        encoding="utf-8-sig",
    )
    difficulty_df.to_csv(
        output_dir / "memory_extraction_difficulty_metrics.csv",
        index=False,
        encoding="utf-8-sig",
    )
    errors_df.to_csv(
        output_dir / "memory_extraction_error_analysis.csv",
        index=False,
        encoding="utf-8-sig",
    )

    with (output_dir / "memory_extraction_summary.json").open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(summary, file, ensure_ascii=False, indent=2)

    print("Memory extractor evaluation completed successfully.")
    print(f"Dataset: {dataset_path}")
    print(f"Cases: {summary['total_cases']}")
    print()
    print("Overall summary")
    print("-" * 72)
    print(
        f"Core field micro accuracy: "
        f"{summary['core_field_micro_accuracy']:.2%}"
    )
    print(
        f"Core complete-record accuracy: "
        f"{summary['core_complete_record_accuracy']:.2%}"
    )
    print(
        f"All-field micro accuracy: "
        f"{summary['all_field_micro_accuracy']:.2%}"
    )
    print(
        f"Language detection accuracy: "
        f"{summary['language_detection_accuracy']:.2%}"
    )
    print(f"Human-review flag rate: {summary['review_required_rate']:.2%}")
    print()
    print("Field metrics")
    print("-" * 72)
    display_fields = field_df[
        [
            "field",
            "field_group",
            "accuracy",
            "recall_on_expected_present",
            "precision_on_predicted_present",
            "missed_value_count",
            "false_positive_count",
            "wrong_value_count",
        ]
    ].copy()
    for column in (
        "accuracy",
        "recall_on_expected_present",
        "precision_on_predicted_present",
    ):
        display_fields[column] = display_fields[column].map(lambda value: f"{value:.2%}")
    print(display_fields.to_string(index=False))
    print()
    print("Language metrics")
    print("-" * 72)
    display_language = language_df.copy()
    for column in (
        "average_core_field_accuracy",
        "core_complete_record_accuracy",
        "average_all_field_accuracy",
        "all_fields_complete_record_accuracy",
    ):
        display_language[column] = display_language[column].map(
            lambda value: f"{value:.2%}"
        )
    print(display_language.to_string(index=False))
    print()
    print(f"Output directory: {output_dir}")

    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate the Yanxin rule-based memory extractor on a fictional "
            "bilingual labelled dataset."
        )
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET_PATH,
        help="Path to the labelled JSON evaluation dataset.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for CSV and JSON evaluation outputs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    evaluate_dataset(args.dataset, args.output_dir)


if __name__ == "__main__":
    main()
