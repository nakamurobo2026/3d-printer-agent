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
]


def main() -> None:
    DOCS_DATA_DIR.mkdir(parents=True, exist_ok=True)
    for name in PUBLIC_JSON_FILES:
        source = DATA_DIR / name
        fallback = "{}" if name == "latest_snapshot.json" else "[]"
        if source.exists():
            shutil.copyfile(source, DOCS_DATA_DIR / name)
        else:
            (DOCS_DATA_DIR / name).write_text(fallback, encoding="utf-8")
    (DOCS_DIR / "index.html").write_text(render_dashboard(), encoding="utf-8")
    for path in DOCS_DATA_DIR.glob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))
    print(f"GitHub Pages dashboard generated: {DOCS_DIR / 'index.html'}")


def render_dashboard() -> str:
    return """<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>3D Printer Agent Dashboard</title>
  <style>
    body{font-family:Arial,sans-serif;margin:0;background:#f5f7f8;color:#17202a}header{background:#0f766e;color:white;padding:20px 24px}main{padding:20px 24px;max-width:1200px;margin:auto}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.card,table{background:white;border:1px solid #d9e0e6;border-radius:8px}.card{padding:14px}.card h2{font-size:12px;color:#60707f;margin:0 0 8px}.card p{font-size:24px;font-weight:700;margin:0}table{width:100%;border-collapse:collapse;margin-top:16px;overflow:hidden}th,td{padding:10px;border-bottom:1px solid #d9e0e6;text-align:left;font-size:13px}th{background:#edf2f4}.risk-low{color:#15803d}.risk-mid{color:#b45309}.risk-high{color:#b91c1c}@media(max-width:800px){.grid{grid-template-columns:1fr}}
  </style>
</head>
<body>
  <header><h1>3D Printer Agent Dashboard</h1><p>GitHub Pages is read-only. Use GitHub Issues and Actions for approval, CSV upload, and Daily Pipeline.</p></header>
  <main>
    <p id="notice">Loading...</p>
    <section class="grid"><div class="card"><h2>候補</h2><p id="candidates">0</p></div><div class="card"><h2>承認済み</h2><p id="approved">0</p></div><div class="card"><h2>平均Score</h2><p id="score">0</p></div><div class="card"><h2>平均Risk</h2><p id="risk">0</p></div></section>
    <table><thead><tr><th>商品/市場</th><th>Pain</th><th>Score</th><th>Risk</th><th>Status</th><th>Next Action</th></tr></thead><tbody id="rows"></tbody></table>
  </main>
<script>
let S={opportunities:[],products:[],approved:[]};
async function j(p,f){try{let r=await fetch(p,{cache:'no-store'});return r.ok?await r.json():f}catch{return f}}
function prod(o){return S.products.find(p=>p.market_id===o.id||p.product_id===o.product_id||p.id===o.id)||{}}
function riskClass(r){return r>=50?'risk-high':r>=25?'risk-mid':'risk-low'}
async function load(){S.opportunities=await j('data/opportunities.json',[]);S.products=await j('data/product_ideas.json',[]);S.approved=await j('data/approved_products.json',[]);let rows=S.opportunities.length?S.opportunities:S.products;document.getElementById('rows').innerHTML=rows.map(o=>{let p=prod(o),risk=Number(o.precision_risk_score||0),score=Number(o.opportunity_score||o.selection_score||0),name=o.market_name||o.product_name||o.name||o.product_id;return `<tr><td>${name}</td><td>${o.pain_category||''}</td><td>${score}</td><td class="${riskClass(risk)}">${risk}</td><td>${p.status||o.status||'discovered'}</td><td>${p.next_action||o.why_build_this||''}</td></tr>`}).join('');document.getElementById('candidates').textContent=rows.length;document.getElementById('approved').textContent=S.approved.length || S.products.filter(p=>p.status==='approved').length;document.getElementById('score').textContent=rows.length?Math.round(rows.reduce((a,o)=>a+Number(o.opportunity_score||o.selection_score||0),0)/rows.length):0;document.getElementById('risk').textContent=rows.length?Math.round(rows.reduce((a,o)=>a+Number(o.precision_risk_score||0),0)/rows.length):0;document.getElementById('notice').textContent='Loaded docs/data/*.json'}
load();
</script>
</body>
</html>"""


if __name__ == "__main__":
    main()
