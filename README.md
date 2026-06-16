# 3D Printer Autonomous AI Agent System

月利益5万円を目標に、公式API・CSV・公開データから市場の不満を集め、Pain Databaseを作ってから商品化候補を判断するシステムです。

## GitHub Pages

Public read-only dashboard:

```text
https://nakamurobo2026.github.io/3d-printer-agent/
```

GitHub Pages UI is a market research dashboard, not a product ranking screen. It shows:

- Data Health
- Top Pain Clusters
- Opportunity Watch
- Design Queue

Design Queue is hidden until Data Health passes the evidence gate. The intended reading flow is:

```text
市場 -> Pain -> Opportunity -> 設計
```

## Operation Model

GitHub Pages is read-only. Operations are done with GitHub Actions and CSV uploads.

- View dashboard: GitHub Pages
- Upload CSV: dashboard header `CSV Upload`
- Run Daily Pipeline: dashboard header `Run Daily Pipeline` or GitHub Actions `workflow_dispatch`
- Local FastAPI admin app: deprecated

## Market Data Acquisition Layer

市場データ取得は、公式API、CSV、公開取得が現実的なデータのみを使います。スクレイピングは禁止です。Amazonレビューの自動取得は禁止し、Amazonは `data/input/reviews/*.csv` からのCSV手動投入のみです。

Collectors:

- `RedditCollector`
- `YouTubeCollector`
- `GoogleTrendsCollector`
- `EtsyCollector`
- `EbayCollector`
- `RakutenCollector`
- `YahooShoppingCollector`
- `CsvReviewCollector`

Raw outputs:

- `data/raw/reddit.json`
- `data/raw/youtube.json`
- `data/raw/google_trends.json`
- `data/raw/etsy.json`
- `data/raw/ebay.json`
- `data/raw/rakuten.json`
- `data/raw/yahoo.json`
- `data/raw/csv_reviews.json`

Processed outputs:

- `data/processed/market_observations.json`
- `data/processed/data_source_status.json`
- `data/processed/pain_database.json`
- `data/processed/pain_clusters.json`
- `data/processed/market_opportunity_mapping.json`

Data source status schema:

```yaml
source:
enabled:
status: success | skipped | failed
reason:
fetched_count:
last_fetch_time:
api_key_present:
used_in_score:
```

Scoring Gate:

- `evidence_count >= 20`
- `source_count >= 2`
- `confidence_score >= 50`

Gateを満たさないPain Clusterは商品候補に進めません。取得件数0の場合はMarket Scoreを計算せず、Dashboardに `実データ未取得` と表示します。

## GitHub Secrets

Set these repository secrets when available. Missing keys are skipped source-by-source.

- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`
- `REDDIT_USER_AGENT`
- `YOUTUBE_API_KEY`
- `ETSY_API_KEY`
- `EBAY_CLIENT_ID`
- `EBAY_CLIENT_SECRET`
- `RAKUTEN_APP_ID`
- `YAHOO_APP_ID`

## CSV Input

```text
data/input/reviews/*.csv
```

Required columns:

- `source`
- `category`
- `product_name`
- `review_text`

Optional columns:

- `rating`
- `review_date`
- `price`
- `url`
- `product_id`
- `reviewer_region`
- `helpful_count`

Supported encodings:

- UTF-8
- UTF-8 BOM
- Shift_JIS / CP932

## GitHub Actions

- `.github/workflows/daily-agent.yml`: main push, manual run, and daily 06:00 JST market research dashboard update
- `.github/workflows/build-dashboard.yml`: dashboard generation compatibility workflow
- `.github/workflows/issue-ops.yml`: GitHub Issue command workflow

## GitHub Pages Settings

If GitHub Pages returns 404, configure:

1. Repository `Settings`
2. `Pages`
3. `Build and deployment`
4. `Source: Deploy from a branch`
5. `Branch: main`
6. `Folder: /docs`
7. `Save`

## Local Development

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m src.main daily
python scripts/build_pages.py
```

## Goal

```yaml
monthly_profit_target_jpy: 50000
max_weekly_operations_hours: 3
inventory_policy: make_to_order
personal_information_policy: do_not_store
stub_data_used: false
```
