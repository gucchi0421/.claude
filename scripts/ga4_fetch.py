#!/usr/bin/env python3.12
"""GA4 Data API からデータを取得して JSON で stdout に出力するスクリプト。"""

import argparse
import json
import os
import sys
from pathlib import Path

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest


def load_global_env() -> dict[str, str]:
    """~/.claude/.env からグローバル設定を読む。"""
    env_file = Path.home() / ".claude" / ".env"
    if not env_file.exists():
        return {}
    env: dict[str, str] = {}
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def find_settings(start_dir: Path) -> Path | None:
    """カレントディレクトリから親を辿って .claude/ga4_settings.json を探す。"""
    for directory in [start_dir, *start_dir.parents]:
        candidate = directory / ".claude" / "ga4_settings.json"
        if candidate.exists():
            return candidate
    return None


def fetch_report(
    client: BetaAnalyticsDataClient,
    property_id: str,
    settings: dict,
    start_date: str,
    end_date: str,
) -> list[dict]:
    """GA4 レポートを取得して辞書のリストで返す。"""
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name=d) for d in settings["dimensions"]],
        metrics=[Metric(name=m) for m in settings["metrics"]],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
    )
    response = client.run_report(request)

    dim_names = [h.name for h in response.dimension_headers]
    met_names = [h.name for h in response.metric_headers]

    rows = []
    for row in response.rows:
        record: dict[str, str] = {}
        for i, val in enumerate(row.dimension_values):
            record[dim_names[i]] = val.value
        for i, val in enumerate(row.metric_values):
            record[met_names[i]] = val.value
        rows.append(record)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="GA4 Data API からデータを取得する")
    parser.add_argument("--start-date", default=None, help="開始日 (例: 30daysAgo, 2024-01-01)")
    parser.add_argument("--end-date", default=None, help="終了日 (例: today, 2024-01-31)")
    parser.add_argument("--property-id", default=None, help="プロパティID（指定時は settings より優先）")
    args = parser.parse_args()

    global_env = load_global_env()
    credentials_path = global_env.get("CLAUDE_GCP_CREDENTIALS") or os.environ.get("CLAUDE_GCP_CREDENTIALS")
    if not credentials_path:
        print("エラー: CLAUDE_GCP_CREDENTIALS が ~/.claude/.env に見つかりません", file=sys.stderr)
        sys.exit(1)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

    settings_file = find_settings(Path.cwd())
    if not settings_file:
        print("エラー: .claude/ga4_settings.json が見つかりません", file=sys.stderr)
        sys.exit(1)
    settings = json.loads(settings_file.read_text())

    start_date = args.start_date or settings.get("date_range", {}).get("start", "30daysAgo")
    end_date = args.end_date or settings.get("date_range", {}).get("end", "today")

    client = BetaAnalyticsDataClient()

    properties = settings.get("properties", [])
    if args.property_id:
        properties = [{"id": args.property_id, "name": args.property_id}]

    if not properties:
        print("エラー: ga4_settings.json に properties が設定されていません", file=sys.stderr)
        sys.exit(1)

    result = []
    for prop in properties:
        prop_id = prop["id"]
        prop_name = prop.get("name", prop_id)
        rows = fetch_report(client, prop_id, settings, start_date, end_date)
        result.append({
            "property_id": prop_id,
            "property_name": prop_name,
            "start_date": start_date,
            "end_date": end_date,
            "row_count": len(rows),
            "rows": rows,
        })

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
