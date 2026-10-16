#!/usr/bin/env python3
"""Render the compact Azure DevOps run summary for one evaluation output directory."""

from __future__ import annotations

import argparse
from pathlib import Path

from aggregate_results import write_azure_summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    write_azure_summary(args.run_dir.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
