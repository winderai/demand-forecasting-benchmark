"""Stage 2: clean the raw downloads into data/prepared/ (weekly retail units, half-hourly GB demand)."""

import argparse
from pathlib import Path

from forecastbench import grid, retail


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, default=Path("data/raw"))
    parser.add_argument("--prepared", type=Path, default=Path("data/prepared"))
    args = parser.parse_args()
    retail.prepare(
        args.raw / "online_retail_II.xlsx",
        args.raw / "online_retail_ii.parquet",
        args.prepared / "retail_weekly.parquet",
        args.prepared / "retail_notes.json",
    )
    grid.prepare(args.raw, args.prepared / "grid_halfhourly.parquet", args.prepared / "grid_notes.json")
    print(f"prepared data in {args.prepared}")


if __name__ == "__main__":
    main()
