from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
DATA_DIR = ROOT / "data"
RESULT_PATH = DATA_DIR / "github_issue_result.md"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    parser.add_argument("--body-file")
    parser.add_argument("--body", default="")
    parser.add_argument("--issue-number", default="")
    args = parser.parse_args()
    body = Path(args.body_file).read_text(encoding="utf-8") if args.body_file else args.body
    payload = parse_payload(args.title, body)
    action = payload.get("action") or action_from_title(args.title)
    if action == "approve":
        result = approve_product(payload)
    elif action == "upload_csv":
        result = upload_csv(payload, body)
        run_daily_pipeline()
    elif action == "run_daily":
        result = run_daily_pipeline()
    else:
        raise SystemExit("Use [APPROVE], [UPLOAD_CSV], or [RUN_DAILY].")
    build_pages()
    write_result(format_result(action, result, args.issue_number))


def action_from_title(title: str) -> str | None:
    upper = title.upper()
    if upper.startswith("[APPROVE]"):
        return "approve"
    if upper.startswith("[UPLOAD_CSV]") or upper.startswith("[CSV]"):
        return "upload_csv"
    if upper.startswith("[RUN_DAILY]") or upper.startswith("[DAILY]"):
        return "run_daily"
    return None


def parse_payload(title: str, body: str) -> dict:
    text = fenced(body, "yaml") or body
    payload = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        payload[key.strip()] = value.strip().strip('"').strip("'")
    if "product_id" not in payload and title.upper().startswith("[APPROVE]"):
        payload["product_id"] = title.split("]", 1)[1].strip()
    if "action" not in payload:
        payload["action"] = action_from_title(title) or ""
    return payload


def fenced(body: str, lang: str) -> str | None:
    match = re.search(rf"```{lang}\s*(.*?)```", body, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else None


def approve_product(payload: dict) -> dict:
    product_id = payload.get("product_id", "").strip()
    if not product_id:
        raise SystemExit("product_id is required")
    build_candidates = read_json("build_candidates.json", [])
    product_ideas = read_json("product_ideas.json", [])
    latest = read_json("latest_snapshot.json", {})
    approved = None
    for rows in [build_candidates, product_ideas, latest.get("build_candidates", [])]:
        for row in rows:
            if row.get("product_id") == product_id or row.get("id") == product_id:
                row["status"] = "approved"
                row["approved"] = True
                row["approval_notes"] = payload.get("notes", "")
                approved = row
    if approved is None:
        raise SystemExit(f"product not found: {product_id}")
    approvals = [row for row in read_json("approved_products.json", []) if row.get("product_id") != product_id]
    approvals.append({"product_id": product_id, "action": "approve", "notes": payload.get("notes", ""), "source": "github_issue"})
    latest["build_candidates"] = latest.get("build_candidates", build_candidates)
    latest["approved_products"] = approvals
    latest.setdefault("github_issue_events", []).append({"action": "approve", "product_id": product_id})
    write_json("build_candidates.json", build_candidates)
    write_json("product_ideas.json", product_ideas)
    write_json("approved_products.json", approvals)
    write_json("latest_snapshot.json", latest)
    return {"product_id": product_id, "approved": True}


def upload_csv(payload: dict, body: str) -> dict:
    csv_url = payload.get("csv_url", "").strip()
    csv_content = fenced(body, "csv") or payload.get("csv_content", "")
    if csv_url:
        with urlopen(csv_url, timeout=30) as response:
            csv_content = response.read().decode("utf-8-sig")
    if not csv_content:
        raise SystemExit("csv_url or fenced csv block is required")
    rows = list(csv.reader(csv_content.splitlines()))
    if not rows or not any(cell.strip() for cell in rows[0]):
        raise SystemExit("CSV header is required")
    path = DATA_DIR / "amazon_reviews.csv"
    path.write_text(csv_content, encoding="utf-8")
    return {"saved_to": str(path), "rows": max(0, len(rows) - 1)}


def run_daily_pipeline() -> dict:
    try:
        from src.main import build_pipeline
        snapshot = build_pipeline().run_once()
    except ImportError:
        from src.main import run_daily
        snapshot = run_daily()
    return {"run_type": snapshot.get("run_type"), "selected_count": len(snapshot.get("build_candidates", [])), "excluded_count": len(snapshot.get("excluded_candidates", []))}


def build_pages() -> None:
    from scripts.build_pages import main as build_pages_main
    build_pages_main()


def read_json(name: str, fallback):
    path = DATA_DIR / name
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else fallback


def write_json(name: str, payload) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_result(text: str) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_text(text, encoding="utf-8")


def format_result(action: str, result: dict, issue_number: str) -> str:
    lines = ["## GitHub Issue Operation Result", "", f"- issue: #{issue_number}" if issue_number else "- issue: workflow_dispatch", f"- action: {action}"]
    lines.extend(f"- {key}: {value}" for key, value in result.items())
    lines.append("")
    lines.append("Dashboard data and GitHub Pages assets were regenerated.")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
