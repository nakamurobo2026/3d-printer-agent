# 3D Printer Autonomous AI Agent System

月利益5万円を目標に、オールジャンル市場調査から低リスクに売れる3Dプリント商品だけを選定するシステムです。

## Operation Model

GitHub Pages is read-only. All operations are done with GitHub Issues and GitHub Actions.

- View dashboard: GitHub Pages
- Approve product: product card `Approve` link or GitHub Issue `[APPROVE] product_id`
- Pause product: product card `Pause` link or GitHub Issue `[PAUSE] product_id`
- Archive product: product card `Archive` link or GitHub Issue `[ARCHIVE] product_id`
- Upload review CSV: dashboard header `CSV Upload` link or GitHub Issue `[UPLOAD_CSV]`
- Run Daily Pipeline: dashboard header `Run Daily Pipeline` link, GitHub Issue `[RUN_DAILY]`, or GitHub Actions `workflow_dispatch`
- Local FastAPI admin app: deprecated

Dashboard:

https://nakamurobo2026.github.io/3d-printer-agent/

## 5分運用フロー

毎日06:00 JSTに `daily-agent.yml` が自動実行され、GitHub Pagesの閲覧専用ダッシュボードが更新されます。手動で確認する日は、以下だけを行います。

1. GitHub Pagesを開き、Build Candidatesの `Selection Score`、`Precision Risk`、`Expected Profit`、`Search Trend`、`Top Pain Point` を確認する。
2. 作る候補は商品カードの `Approve`、保留は `Pause`、除外は `Archive` を押してGitHub Issueを作成する。
3. AmazonレビューCSVを追加する日は、ヘッダーの `CSV Upload` から `data/input` にアップロードする。
4. すぐ再集計したい場合は、ヘッダーの `Run Daily Pipeline` から `daily-agent.yml` を手動実行する。
5. 更新後のGitHub Pagesで、選定結果とDesign Queueを確認する。

## GitHub Issue Commands

Approve:

```yaml
product_id: selected_office
action: approve
notes: ""
```

Pause:

```yaml
product_id: selected_office
action: pause
notes: ""
```

Archive:

```yaml
product_id: selected_office
action: archive
notes: ""
```

CSV upload:

```yaml
action: upload_csv
csv_url: ""
notes: ""
```

```csv
product_name,genre,title,review,rating
example,office,使いにくい,交換部品がなくて困る,2
```

Daily Pipeline:

```yaml
action: run_daily
notes: ""
```

## Architecture

```text
AllGenreMarketResearch -> PainDiscovery -> MarketAnalysis -> CompetitiveAnalysis
PrecisionRisk -> ProfitForecast -> MarketingPotential -> ProductSelection
DesignBrief -> Human Fusion Design -> Prototype / Sales / Learning
```

## GitHub Pages Settings

404が出る場合はGitHub上で以下を設定してください。

1. Repository の `Settings` を開く
2. 左メニューの `Pages` を開く
3. `Build and deployment` で `Source: Deploy from a branch` を選択
4. `Branch: main` を選択
5. `Folder: /docs` を選択
6. `Save` を押す

## GitHub Actions

- `.github/workflows/daily-agent.yml`: main push、手動実行、毎日06:00 JSTで市場調査とPages更新
- `.github/workflows/build-dashboard.yml`: dashboard生成互換ワークフロー
- `.github/workflows/issue-ops.yml`: GitHub Issueを操作コマンドとして処理

## Local Development

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m src.main daily
```

## Deprecated Local Admin App

The local FastAPI admin app is deprecated. Product approval, CSV upload, and Daily Pipeline execution should be performed through GitHub Issues and GitHub Actions.

## Goal

```yaml
monthly_profit_target_jpy: 50000
max_weekly_operations_hours: 3
inventory_policy: make_to_order
personal_information_policy: do_not_store
```
