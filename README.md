# 3D Printer Autonomous AI Agent System

3Dプリンター事業で月利益5万円を目標に、商品候補の市場スコア、Precision Risk、利益予測、商品ステータスを管理するローカル管理アプリです。

## GitHub Pages

公開用の閲覧専用ダッシュボード:

https://nakamurobo2026.github.io/3d-printer-agent/

GitHub Pages版は閲覧専用です。商品承認、CSVアップロード、Daily Pipeline実行などの操作機能はローカル版のみで利用します。

公開対象ファイル:

```text
docs/index.html
docs/data/latest_snapshot.json
docs/data/opportunities.json
docs/data/product_ideas.json
docs/data/listing_drafts.json
```

## GitHub Pages Settings

404が出る場合は、GitHub上で以下を設定してください。

1. Repository の `Settings` を開く
2. 左メニューの `Pages` を開く
3. `Build and deployment` で `Source: Deploy from a branch` を選択
4. `Branch: main` を選択
5. `Folder: /docs` を選択
6. `Save` を押す
7. 数十秒から数分待って `https://nakamurobo2026.github.io/3d-printer-agent/` を再読み込みする

## GitHub Actions

`.github/workflows/build-dashboard.yml` は main へのpush時に以下を実行します。

1. Python環境をセットアップ
2. `python -m src.main daily` で dashboard data を生成
3. `python scripts/build_pages.py` で `docs/index.html` と `docs/data/*.json` を更新
4. `docs/.nojekyll` を作成
5. 生成済みの `docs/` と `data/*.json` を main にコミットできる状態にする

GitHub Pages自体の公開元は、上記の通り `main` ブランチの `/docs` に設定します。

## Local Admin App

ローカル版では次を利用できます。

- 商品承認、停止、アーカイブ
- AmazonレビューCSVアップロード
- Daily Pipeline実行
- 商品詳細確認

```powershell
start_dashboard.bat
```

または:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m src.server
```

ブラウザで `http://127.0.0.1:8000` を開きます。

## Modes

- GitHub Pages: 閲覧専用
- Local FastAPI: 承認、CSVアップロード、Daily Pipeline実行

## Goal

```yaml
monthly_profit_target_jpy: 50000
max_weekly_operations_hours: 3
inventory_policy: make_to_order
personal_information_policy: do_not_store
```
