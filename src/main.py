from __future__ import annotations

import argparse
import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
INPUT_REVIEWS_DIR = DATA_DIR / "input" / "reviews"

SOURCES = [
    ("reddit", ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET"]),
    ("youtube", ["YOUTUBE_API_KEY"]),
    ("google_trends", []),
    ("etsy", ["ETSY_API_KEY"]),
    ("ebay", ["EBAY_CLIENT_ID", "EBAY_CLIENT_SECRET"]),
    ("rakuten", ["RAKUTEN_APP_ID"]),
    ("yahoo", ["YAHOO_APP_ID"]),
]
RAW_FILES = {
    "reddit": "reddit.json",
    "youtube": "youtube.json",
    "google_trends": "google_trends.json",
    "etsy": "etsy.json",
    "ebay": "ebay.json",
    "rakuten": "rakuten.json",
    "yahoo": "yahoo.json",
    "csv_reviews": "csv_reviews.json",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["daily", "run-once", "dashboard"])
    args = parser.parse_args()
    if args.command in {"daily", "run-once"}:
        snapshot = run_daily()
        print(json.dumps(snapshot.get("analytics", {}), ensure_ascii=False, indent=2))
    else:
        print(DATA_DIR / "dashboard.html")


def run_daily() -> dict:
    prepare_dirs()
    csv_rows = collect_csv_reviews()
    source_status = build_source_status(csv_rows)
    observations = normalize_csv_observations(csv_rows)
    pain_database = extract_pains(observations)
    pain_clusters = cluster_pains(pain_database)
    opportunities = [row for row in pain_clusters if row.get("scoring_gate_passed")]
    data_source_status = summarize_sources(source_status, observations)
    snapshot = {
        "run_type": "review_mining",
        "flow": [
            "RedditCollector",
            "YouTubeCollector",
            "GoogleTrendsCollector",
            "EtsyCollector",
            "EbayCollector",
            "RakutenCollector",
            "YahooShoppingCollector",
            "CsvReviewCollector",
            "PainExtraction",
            "PainClustering",
            "DashboardGenerator",
        ],
        "data_source_status": data_source_status,
        "review_mining": {
            "source_files": [],
            "source_errors": [],
            "api_source_status": source_status,
            "rejected_reviews": [],
            "database_status": {
                "review_count": len(observations),
                "real_data_count": len(observations),
                "csv_count": len(csv_rows),
                "api_count": 0,
                "trend_count": 0,
                "pain_count": len(pain_database),
                "cluster_count": len(pain_clusters),
                "candidate_pain_count": len(opportunities),
                "is_sufficient_for_product_planning": bool(opportunities),
                "minimum_reviews": 50,
                "minimum_candidate_pain_clusters": 5,
                "last_fetch_time": data_source_status["last_fetch_time"],
                "stub_data_used": False,
                "real_data_status": data_source_status["status"],
            },
        },
        "normalized_reviews": observations,
        "pain_database": pain_database,
        "pain_clusters": pain_clusters,
        "market_opportunity_mapping": opportunities,
        "trend_data": [],
        "real_market_observations": observations,
        "research_candidates": opportunities,
        "excluded_candidates": [row for row in pain_clusters if not row.get("scoring_gate_passed")],
        "build_candidates": [],
        "design_queue": [],
        "evergreen_products": [],
        "analytics": {
            "selected_count": 0,
            "excluded_count": len([row for row in pain_clusters if not row.get("scoring_gate_passed")]),
            "researched_genre_count": len({row.get("category", "") for row in observations}),
            "review_count": len(observations),
            "pain_count": len(pain_database),
            "pain_cluster_count": len(pain_clusters),
            "candidate_pain_count": len(opportunities),
            "expected_monthly_profit": 0,
        },
    }
    write_outputs(snapshot, source_status, observations, pain_database, pain_clusters, opportunities, csv_rows)
    return snapshot


def prepare_dirs() -> None:
    for path in [DATA_DIR, RAW_DIR, PROCESSED_DIR, INPUT_REVIEWS_DIR, DATA_DIR / "docs"]:
        path.mkdir(parents=True, exist_ok=True)


def collect_csv_reviews() -> list[dict]:
    rows: list[dict] = []
    for path in sorted(INPUT_REVIEWS_DIR.glob("*.csv")):
        for encoding in ["utf-8-sig", "utf-8", "cp932", "shift_jis"]:
            try:
                with path.open("r", encoding=encoding, newline="") as handle:
                    reader = csv.DictReader(handle)
                    for row in reader:
                        rows.append({str(k or "").strip().lower(): v for k, v in row.items()})
                break
            except UnicodeDecodeError:
                continue
    return rows


def build_source_status(csv_rows: list[dict]) -> list[dict]:
    rows = []
    for source, keys in SOURCES:
        present = all(os.getenv(key) for key in keys) if keys else False
        reason = "" if present else ("pytrends_not_installed_or_not_run" if source == "google_trends" else "api_key_not_configured")
        rows.append(source_status(source, present, "skipped", reason, 0, None, present, False))
        write_json(RAW_DIR / RAW_FILES[source], [])
    csv_status = "success" if csv_rows else "skipped"
    rows.append(source_status("csv_reviews", True, csv_status, "" if csv_rows else "no_csv_files", len(csv_rows), utc_now() if csv_rows else None, True, bool(csv_rows)))
    write_json(RAW_DIR / RAW_FILES["csv_reviews"], csv_rows)
    return rows


def normalize_csv_observations(csv_rows: list[dict]) -> list[dict]:
    observations = []
    for index, row in enumerate(csv_rows):
        text = clean(row.get("review_text") or row.get("review") or row.get("comment") or "")
        if not text:
            continue
        observations.append({
            "observation_id": f"csv_{index+1:05d}",
            "review_id": f"csv_{index+1:05d}",
            "source": clean(row.get("source") or "csv_reviews"),
            "category": clean(row.get("category") or "unknown"),
            "product_name": clean(row.get("product_name") or row.get("title") or "unknown"),
            "review_text": text,
            "rating": row.get("rating") or "",
            "url": row.get("url") or "",
            "signal_type": "pain_text",
        })
    return observations


def extract_pains(observations: list[dict]) -> list[dict]:
    patterns = {
        "収納不足": ["収納", "置き場所", "store", "storage"],
        "破損": ["壊", "割れ", "broken", "break"],
        "サイズ不一致": ["合わない", "サイズ", "fit", "does not fit"],
        "ケーブル問題": ["ケーブル", "cable", "cord"],
        "使いにくさ": ["使いにく", "不便", "hard to"],
        "交換部品不足": ["交換", "replacement", "parts"],
    }
    pains = []
    for obs in observations:
        text = obs["review_text"].lower()
        for pain, terms in patterns.items():
            if any(term.lower() in text for term in terms):
                pains.append({**obs, "pain_category": pain, "pain_text": obs["review_text"], "severity": 70})
    return pains


def cluster_pains(pains: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str], list[dict]] = {}
    for pain in pains:
        grouped.setdefault((pain["category"], pain["pain_category"]), []).append(pain)
    clusters = []
    for i, ((category, pain_category), rows) in enumerate(grouped.items(), 1):
        sources = {row["source"] for row in rows}
        evidence = len(rows)
        confidence = min(100, evidence * 2 + len(sources) * 15 + 14)
        gate = evidence >= 20 and len(sources) >= 2 and confidence >= 50
        clusters.append({
            "cluster_id": f"cluster_{i:04d}",
            "category": category,
            "pain_category": pain_category,
            "pain_summary": f"{category}カテゴリで{pain_category}の不満が集中",
            "review_count": evidence,
            "evidence_count": evidence,
            "source_count": len(sources),
            "sources": sorted(sources),
            "confidence_score": confidence,
            "scoring_gate_passed": gate,
            "pain_score": confidence if gate else 0,
            "print_suitability_score": 50 if gate else 0,
            "suitability_status": "candidate_pain" if gate else "insufficient_evidence",
            "suitability_reasons": ["Scoring Gate passed"] if gate else ["evidence_count/source_count/confidence_score below gate"],
            "opportunity_id": f"opp_{i:04d}",
        })
    return clusters


def summarize_sources(status_rows: list[dict], observations: list[dict]) -> dict:
    def count(source: str) -> int:
        row = next((item for item in status_rows if item["source"] == source), {})
        return int(row.get("fetched_count") or 0)
    total = len(observations)
    return {
        "real_data_count": total,
        "reddit_count": count("reddit"),
        "youtube_count": count("youtube"),
        "google_trends_count": count("google_trends"),
        "etsy_count": count("etsy"),
        "ebay_count": count("ebay"),
        "csv_count": count("csv_reviews"),
        "api_count": 0,
        "trend_count": 0,
        "last_fetch_time": utc_now() if total else None,
        "real_data_ratio": 0.0 if total == 0 else 100.0,
        "stub_data_used": False,
        "sources_enabled": sum(1 for row in status_rows if row["enabled"]),
        "sources_skipped": sum(1 for row in status_rows if row["status"] == "skipped"),
        "sources_failed": sum(1 for row in status_rows if row["status"] == "failed"),
        "used_in_score_count": sum(1 for row in status_rows if row["used_in_score"]),
        "status": "実データ未取得" if total == 0 else "実データ取得済み",
        "sources": status_rows,
    }


def write_outputs(snapshot, source_status_rows, observations, pains, clusters, opportunities, csv_rows) -> None:
    write_json(DATA_DIR / "latest_snapshot.json", snapshot)
    write_json(DATA_DIR / "data_source_status.json", source_status_rows)
    write_json(DATA_DIR / "api_source_status.json", source_status_rows)
    write_json(DATA_DIR / "market_observations.json", observations)
    write_json(DATA_DIR / "real_market_observations.json", observations)
    write_json(DATA_DIR / "normalized_reviews.json", observations)
    write_json(DATA_DIR / "pain_database.json", pains)
    write_json(DATA_DIR / "pain_clusters.json", clusters)
    write_json(DATA_DIR / "market_opportunity_mapping.json", opportunities)
    write_json(DATA_DIR / "opportunities.json", opportunities)
    write_json(DATA_DIR / "product_ideas.json", [])
    write_json(DATA_DIR / "listing_drafts.json", [])
    write_json(DATA_DIR / "strategies.json", {})
    write_json(DATA_DIR / "approved_products.json", [])
    write_json(PROCESSED_DIR / "data_source_status.json", source_status_rows)
    write_json(PROCESSED_DIR / "market_observations.json", observations)
    write_json(PROCESSED_DIR / "pain_database.json", pains)
    write_json(PROCESSED_DIR / "pain_clusters.json", clusters)
    write_json(PROCESSED_DIR / "market_opportunity_mapping.json", opportunities)


def source_status(source, enabled, status, reason, fetched_count, last_fetch_time, api_key_present, used_in_score):
    return {
        "source": source,
        "enabled": enabled,
        "status": status,
        "reason": reason,
        "fetched_count": fetched_count,
        "last_fetch_time": last_fetch_time,
        "api_key_present": api_key_present,
        "used_in_score": used_in_score,
    }


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def clean(value) -> str:
    return str(value or "").strip()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


if __name__ == "__main__":
    main()
