"""Stage 1: download every public input and record its provenance in data/manifest.json."""

import argparse
from pathlib import Path

from forecastbench import sources

TEMPERATURE_WINDOWS = [
    ("2024-01-01", "2024-12-31"),
    ("2025-01-01", "2025-12-31"),
    ("2026-01-01", "2026-10-20"),
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, default=Path("data/raw"))
    parser.add_argument("--manifest", type=Path, default=Path("data/manifest.json"))
    parser.add_argument("--only", choices=["retail", "grid", "weather"], nargs="*")
    args = parser.parse_args()
    chosen = set(args.only or ["retail", "grid", "weather"])
    files = []
    if "retail" in chosen:
        files += sources.retail(args.raw)
    if "grid" in chosen:
        files += sources.grid(args.raw)
    if "weather" in chosen:
        files += sources.temperature(args.raw, TEMPERATURE_WINDOWS)
    sources.manifest(files, args.manifest)
    print(f"fetched {len(files)} files into {args.raw}")


if __name__ == "__main__":
    main()
