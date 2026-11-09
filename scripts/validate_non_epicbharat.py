#!/usr/bin/env python3
"""Read-only syntax/config validation for the six non-EpicBharat pipelines.

This script deliberately uses an explicit allowlist. It never walks the repository
root and cannot inspect EpicBharat files.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PYTHON_ROOTS = (
    ROOT / "blog",
    ROOT / "channels" / "TigerVlogs-2026",
    ROOT / "channels" / "DigitalImmortals" / "shorts" / "pipeline",
    ROOT / "channels" / "IndianHorrorTapes",
    ROOT / "channels" / "AllTrainReels",
    ROOT / "channels" / "MindNestTales",
)
JSON_FILES = (
    ROOT / "channels" / "TigerVlogs-2026" / "config.json",
    ROOT / "channels" / "DigitalImmortals" / "config.json",
    ROOT / "channels" / "IndianHorrorTapes" / "config.json",
    ROOT / "channels" / "AllTrainReels" / "config.json",
    ROOT / "channels" / "MindNestTales" / "channels_config.json",
)
WORKFLOWS = (
    ROOT / ".github" / "workflows" / "buzzstorm_blog_scheduler.yml",
    ROOT / ".github" / "workflows" / "tigervlogs_2026_scheduler.yml",
    ROOT / ".github" / "workflows" / "digital_immortals_shorts_scheduler.yml",
    ROOT / ".github" / "workflows" / "indian_horror_tapes_scheduler.yml",
    ROOT / ".github" / "workflows" / "all_train_reels_scheduler.yml",
    ROOT / ".github" / "workflows" / "mindnest_tales_scheduler.yml",
)

def main() -> int:
    failures: list[str] = []
    checked = 0
    for root in PYTHON_ROOTS:
        if not root.exists():
            failures.append(f"Missing expected source directory: {root.relative_to(ROOT)}")
            continue
        for path in root.rglob("*.py"):
            try:
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
                checked += 1
            except (SyntaxError, UnicodeDecodeError) as exc:
                failures.append(f"{path.relative_to(ROOT)}: {exc}")

    for path in JSON_FILES:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            failures.append(f"{path.relative_to(ROOT)}: {exc}")

    for path in WORKFLOWS:
        if not path.is_file():
            failures.append(f"Missing workflow: {path.relative_to(ROOT)}")
            continue
        content = path.read_text(encoding="utf-8")
        if "name:" not in content or "jobs:" not in content:
            failures.append(f"Workflow missing name/jobs: {path.relative_to(ROOT)}")

    if failures:
        print("Non-EpicBharat validation FAILED:")
        for failure in failures:
            print(f"::error::{failure}")
        return 1

    print(f"Non-EpicBharat validation passed: {checked} Python files, "
          f"{len(JSON_FILES)} JSON configs, {len(WORKFLOWS)} workflow definitions.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
