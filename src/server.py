from __future__ import annotations

import json
from pathlib import Path
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from scripts.build_pages import render_public_dashboard
from src.main import DATA_DIR, run_daily

ROOT = Path(__file__).resolve().parents[1]
app = FastAPI(title="3D Printer Agent Dashboard")


def read_json(name: str, fallback):
    path = DATA_DIR / name
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(name: str, payload) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return render_public_dashboard()


@app.get("/api/snapshot")
def snapshot() -> dict:
    return read_json("latest_snapshot.json", {})


@app.get("/api/opportunities")
def opportunities() -> list[dict]:
    return read_json("opportunities.json", [])


@app.get("/api/products")
def products() -> list[dict]:
    return read_json("product_ideas.json", [])


@app.get("/api/listings")
def listings() -> list[dict]:
    return read_json("listing_drafts.json", [])


@app.post("/api/run/daily")
def daily() -> dict:
    return run_daily()


@app.post("/api/product/{product_id}/{action}")
def set_status(product_id: str, action: str) -> dict:
    status_map = {"approve":"approved", "pause":"paused", "archive":"archived"}
    if action not in status_map:
        raise HTTPException(status_code=404, detail="unsupported action")
    rows = products()
    for row in rows:
        if row.get("id") == product_id or row.get("market_id") == product_id:
            row["status"] = status_map[action]
            row["next_action"] = f"manual {action} from local dashboard"
            write_json("product_ideas.json", rows)
            snap = snapshot()
            snap["products"] = rows
            write_json("latest_snapshot.json", snap)
            return {"product": row, "snapshot": snap}
    raise HTTPException(status_code=404, detail="product not found")


@app.post("/api/upload/amazon-csv")
async def upload_amazon_csv(file: UploadFile = File(...)) -> dict:
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    content = await file.read()
    path = DATA_DIR / "amazon_reviews.csv"
    path.write_bytes(content)
    snap = run_daily()
    return {"saved_to": str(path), "snapshot": snap}


def main() -> None:
    import uvicorn
    run_daily()
    uvicorn.run("src.server:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
