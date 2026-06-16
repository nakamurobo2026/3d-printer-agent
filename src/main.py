from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

OPPORTUNITIES = [
    {"id":"opp_accessibility_handle","market_name":"アクセシビリティ補助ハンドル","category":"accessibility","pain_category":"使いにくさ","customer_pain":"既存の取っ手やスイッチが握りにくく使いにくい","average_price_jpy":2980,"competitor_count":120,"estimated_margin":0.68,"opportunity_score":83,"pain_score":98,"margin_score":83,"repeatability_score":70,"search_volume_score":67,"precision_risk_score":0,"development_hours":2.5,"market_lifetime":"seasonal-to-evergreen","search_trend":"rising"},
    {"id":"opp_pet_storage","market_name":"ペット用品清掃・収納パーツ","category":"pet","pain_category":"収納不足","customer_pain":"ブラシや掃除用品の置き場所が決まらず散らかる","average_price_jpy":1980,"competitor_count":95,"estimated_margin":0.68,"opportunity_score":81,"pain_score":91,"margin_score":75,"repeatability_score":76,"search_volume_score":70,"precision_risk_score":0,"development_hours":1.0,"market_lifetime":"evergreen","search_trend":"rising"},
    {"id":"opp_cable_organizer","market_name":"ケーブル整理","category":"office","pain_category":"ケーブル問題","customer_pain":"充電ケーブルやUSBケーブルが絡まり作業机が散らかる","average_price_jpy":1680,"competitor_count":180,"estimated_margin":0.70,"opportunity_score":81,"pain_score":88,"margin_score":78,"repeatability_score":72,"search_volume_score":74,"precision_risk_score":0,"development_hours":1.0,"market_lifetime":"evergreen","search_trend":"stable"},
    {"id":"opp_battery_holder","market_name":"バッテリーホルダー","category":"garage","pain_category":"整理整頓","customer_pain":"工具バッテリーの置き場がなく、作業台で散らかる","average_price_jpy":2480,"competitor_count":230,"estimated_margin":0.66,"opportunity_score":84,"pain_score":86,"margin_score":82,"repeatability_score":74,"search_volume_score":82,"precision_risk_score":44,"development_hours":2.0,"market_lifetime":"evergreen","search_trend":"rising"}
]


def run_daily() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    products = [
        {"id":"product_accessibility_handle","market_id":"opp_accessibility_handle","name":"アクセシビリティ補助ハンドル 標準版","expected_price_jpy":2980,"status":"listing_generated","next_action":"市場分析後に設計指示書生成"},
        {"id":"product_pet_storage","market_id":"opp_pet_storage","name":"ペット用品清掃・収納パーツ 標準版","expected_price_jpy":1980,"status":"watching","next_action":"レビュー不満点を追加収集"},
        {"id":"product_cable_organizer","market_id":"opp_cable_organizer","name":"ケーブル整理 標準版","expected_price_jpy":1680,"status":"validated","next_action":"商品ページ構成を確認"},
        {"id":"product_battery_holder","market_id":"opp_battery_holder","name":"バッテリーホルダー 標準版","expected_price_jpy":2480,"status":"paused","next_action":"Precision Riskが35超のため実測リスク再評価"}
    ]
    listings = [{"id":"listing_accessibility_handle","product_id":"product_accessibility_handle","title":"アクセシビリティ補助ハンドル 標準版","price_jpy":2980,"body":"握りにくい取っ手やスイッチを使いやすくする受注生産パーツです。","status":"draft_ready","channel":"BASE"}]
    strategies = {"product_accessibility_handle":{"market_analysis":{"market_summary":"使いにくさ起点の継続需要があり、受注生産の小型3Dプリント品と相性が良い。","target_customer":"既製品が握りにくい、使いにくいユーザー","customer_pain":"既存の取っ手やスイッチが握りにくく使いにくい","buying_motivation":"専用品で毎日の操作負担を減らしたい。","search_intent":"補助ハンドル、操作補助、3Dプリント便利グッズを探している","market_lifetime":"seasonal-to-evergreen","demand_strength":"strong","recommended_price_range":"2480-3680円","go_no_go":"Go"},"competitive_analysis":{"common_complaints":["高い","使いにくい","説明がわかりにくい"],"weak_points":["寸法情報が不足","使用写真が少ない","対応条件が曖昧"],"differentiation_points":["寸法図を明記","使用前後写真を掲載","用途別バリエーション"]},"marketing_strategy":{"headline":"握りにくさをすっきり解決する補助ハンドル","subheadline":"H2D試作、P2S量産の受注生産3Dプリント品。","seo_keywords":["補助ハンドル","3Dプリント","アクセシビリティ","便利グッズ"],"product_page_structure":["課題提起","使用前/使用後","寸法と対応条件","使い方","FAQ"],"short_video_scripts":["握りにくい場面 -> 補助ハンドル装着 -> 操作しやすい状態 -> CTA"],"sns_post_templates":["毎日の小さな使いにくさを3Dプリントで改善。"],"faq":[{"q":"素材は何ですか？","a":"用途に応じてPETGまたはPLA+で製作します。"}]}}}
    snapshot = {"run_type":"daily","opportunities":OPPORTUNITIES,"products":products,"listings":listings,"strategies":strategies,"analytics":{"weekly_candidate_count":len(OPPORTUNITIES),"profit_forecast":{"monthly_profit_if_required_units_sold":50000,"target_jpy":50000}}}
    write_json("opportunities.json", OPPORTUNITIES)
    write_json("product_ideas.json", products)
    write_json("listing_drafts.json", listings)
    write_json("strategies.json", strategies)
    write_json("latest_snapshot.json", snapshot)
    return snapshot


def write_json(name: str, payload) -> None:
    (DATA_DIR / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["daily", "run-once", "dashboard"])
    args = parser.parse_args()
    if args.command in {"daily", "run-once"}:
        snapshot = run_daily()
        print(json.dumps(snapshot.get("analytics", {}), ensure_ascii=False, indent=2))
    else:
        path = DATA_DIR / "dashboard.html"
        print(path)


if __name__ == "__main__":
    main()
