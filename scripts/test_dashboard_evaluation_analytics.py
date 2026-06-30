from __future__ import annotations

import ast
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DASHBOARD_PATH = BASE_DIR / "app" / "dashboard.py"
SNAPSHOT_PATH = (
    BASE_DIR
    / "data"
    / "evaluation"
    / "memory_extraction_evaluation_snapshot.json"
)


def main() -> None:
    dashboard_source = DASHBOARD_PATH.read_text(encoding="utf-8")
    ast.parse(dashboard_source)

    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))

    assert '"Evaluation Analytics"' in dashboard_source
    assert "load_evaluation_snapshot" in dashboard_source
    assert "Holdout Core-Field Accuracy" in dashboard_source

    assert snapshot["holdout"]["cases"] == 20
    assert snapshot["holdout"]["core_field_micro_accuracy"] == 91.0
    assert snapshot["holdout"]["core_complete_record_accuracy"] == 55.0
    assert snapshot["metadata"]["frozen_rule_commit"] == "0169ccd"
    assert snapshot["metadata"]["one_shot_protocol"] is True
    assert snapshot["metadata"]["do_not_tune_on_holdout"] is True

    fields = {
        item["field"]: item
        for item in snapshot["field_metrics"]
    }
    assert fields["Event title"]["holdout_accuracy"] == 40.0
    assert fields["Location"]["holdout_accuracy"] == 70.0
    assert fields["Start year"]["holdout_accuracy"] == 100.0

    print("Dashboard evaluation analytics test completed successfully.")
    print("Analytics tab, frozen snapshot and governance assertions passed.")


if __name__ == "__main__":
    main()
