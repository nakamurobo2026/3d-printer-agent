from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DOCS_DIR = ROOT / "docs"
DOCS_DATA_DIR = DOCS_DIR / "data"
PUBLIC_JSON_FILES = [
    "latest_snapshot.json",
    "opportunities.json",
    "product_ideas.json",
    "listing_drafts.json",
    "strategies.json",
    "approved_products.json",
    "normalized_reviews.json",
    "pain_database.json",
    "pain_clusters.json",
    "market_opportunity_mapping.json",
    "api_source_status.json",
    "data_source_status.json",
    "trend_data.json",
    "real_market_observations.json",
    "market_observations.json",
]


def main() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DATA_DIR.mkdir(parents=True, exist_ok=True)
    for name in PUBLIC_JSON_FILES:
        source = DATA_DIR / name
        fallback = "{}" if name == "latest_snapshot.json" else "[]"
        if source.exists():
            shutil.copyfile(source, DOCS_DATA_DIR / name)
        else:
            (DOCS_DATA_DIR / name).write_text(fallback, encoding="utf-8")
    index = DOCS_DIR / "index.html"
    if not index.exists():
        index.write_text(fallback_dashboard(), encoding="utf-8")
    for path in DOCS_DATA_DIR.glob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))
    print(f"GitHub Pages dashboard generated: {index}")


def fallback_dashboard() -> str:
    return """<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Market Research Dashboard</title></head><body><h1>Market Research Dashboard</h1><p>docs/index.html is ready for GitHub Pages.</p></body></html>"""


if __name__ == "__main__":
    main()
