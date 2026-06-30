from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from scripts.evaluate_memory_extractor import evaluate_dataset


PROJECT_ROOT = Path(__file__).resolve().parents[1]
HOLDOUT_DATASET = (
    PROJECT_ROOT
    / "data"
    / "evaluation"
    / "memory_extraction_holdout_cases.json"
)
HOLDOUT_OUTPUT_DIR = PROJECT_ROOT / "outputs" / "evaluation" / "holdout"
FROZEN_RULE_COMMIT = "0169ccd"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_head() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def _update_summary_manifest(summary: dict[str, Any]) -> None:
    summary_path = HOLDOUT_OUTPUT_DIR / "memory_extraction_summary.json"
    with summary_path.open("r", encoding="utf-8") as file:
        saved_summary = json.load(file)

    saved_summary.update(
        {
            "evaluation_role": "holdout",
            "frozen_rule_commit": FROZEN_RULE_COMMIT,
            "evaluated_git_head": _git_head(),
            "dataset_sha256": _sha256(HOLDOUT_DATASET),
            "one_shot_protocol": True,
            "do_not_tune_on_holdout": True,
            "reporting_note": (
                "This holdout result is a one-shot generalisation check. "
                "Do not modify extraction rules in response to these cases."
            ),
        }
    )

    with summary_path.open("w", encoding="utf-8") as file:
        json.dump(saved_summary, file, ensure_ascii=False, indent=2)

    manifest = {
        "evaluation_role": "holdout",
        "frozen_rule_commit": FROZEN_RULE_COMMIT,
        "evaluated_git_head": saved_summary["evaluated_git_head"],
        "dataset_path": str(HOLDOUT_DATASET),
        "dataset_sha256": saved_summary["dataset_sha256"],
        "total_cases": summary["total_cases"],
        "one_shot_protocol": True,
        "do_not_tune_on_holdout": True,
    }

    with (HOLDOUT_OUTPUT_DIR / "holdout_run_manifest.json").open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(manifest, file, ensure_ascii=False, indent=2)


def main() -> None:
    if not HOLDOUT_DATASET.exists():
        raise FileNotFoundError(f"Holdout dataset not found: {HOLDOUT_DATASET}")

    print("Yanxin one-shot holdout evaluation")
    print("-" * 72)
    print(f"Frozen rule commit: {FROZEN_RULE_COMMIT}")
    print(f"Current Git HEAD: {_git_head()}")
    print(f"Dataset SHA-256: {_sha256(HOLDOUT_DATASET)}")
    print(
        "Protocol: report this result once and do not tune extraction rules "
        "against the holdout cases."
    )
    print()

    summary = evaluate_dataset(HOLDOUT_DATASET, HOLDOUT_OUTPUT_DIR)
    _update_summary_manifest(summary)

    print()
    print("Holdout evaluation manifest written successfully.")
    print(f"Manifest: {HOLDOUT_OUTPUT_DIR / 'holdout_run_manifest.json'}")


if __name__ == "__main__":
    main()
