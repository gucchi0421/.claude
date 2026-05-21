#!/usr/bin/env python3.12
"""
SEO作業履歴をGoogleスプレッドシートに記録するスクリプト。

- ~/.claude/.env の CLAUDE_GCP_CREDENTIALS でサービスアカウント認証（ファイルパス）
- プロジェクトの .claude/settings.sheets.json でスプレッドシートID・シート名を取得
- 引数で作業内容を受け取り末尾にAppendする

使い方:
  python3 ~/.claude/scripts/seo_log.py \
    --type "記事投稿" \
    --page "/blog/seo-tips" \
    --summary "SEOキーワード記事を投稿" \
    --agent "writer" \
    --result "公開完了"
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

HEADER = ["日付", "作業種別", "URL", "キーワード", "作業内容", "担当エージェント", "結果・メモ", "詳細（3C分析・調査内容等）"]


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
    """カレントディレクトリから親を辿って .claude/settings.sheets.json を探す。"""
    for directory in [start_dir, *start_dir.parents]:
        candidate = directory / ".claude" / "settings.sheets.json"
        if candidate.exists():
            return candidate
    return None


def get_service(credentials_path: str):
    creds = service_account.Credentials.from_service_account_file(
        str(Path(credentials_path).expanduser()), scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds, cache_discovery=False)


def ensure_header(service, spreadsheet_id: str, sheet_name: str) -> None:
    """シートが空ならヘッダー行を書く。"""
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=f"{sheet_name}!A1:F1")
        .execute()
    )
    if not result.get("values"):
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A1",
            valueInputOption="RAW",
            body={"values": [HEADER]},
        ).execute()


def append_row(service, spreadsheet_id: str, sheet_name: str, row: list[str]) -> None:
    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": [row]},
    ).execute()


def main() -> None:
    parser = argparse.ArgumentParser(description="SEO作業履歴をスプレッドシートに記録する")
    parser.add_argument("--type", required=True, help="作業種別（例: 記事投稿 / メタ更新 / リライト）")
    parser.add_argument("--url", default="", help="対象ページのURL またはスラッグ")
    parser.add_argument("--keywords", default="", help="対策キーワード（カンマ区切り可）")
    parser.add_argument("--summary", required=True, help="作業内容の要約")
    parser.add_argument("--agent", default="", help="担当エージェント（例: writer / seo-engineer）")
    parser.add_argument("--result", default="", help="結果・メモ")
    parser.add_argument("--detail", default="", help="詳細情報（3C分析・競合調査・キーワードリスト等、長文可）")
    args = parser.parse_args()

    env = load_global_env()
    credentials_path = env.get("CLAUDE_GCP_CREDENTIALS", "")
    if not credentials_path:
        print("ERROR: CLAUDE_GCP_CREDENTIALS が ~/.claude/.env に設定されていません", file=sys.stderr)
        sys.exit(1)

    settings_path = find_settings(Path.cwd())
    if not settings_path:
        print("ERROR: .claude/settings.sheets.json が見つかりません", file=sys.stderr)
        sys.exit(1)

    settings = json.loads(settings_path.read_text())
    spreadsheet_id = settings.get("spreadsheet_id", "")
    sheet_name = settings.get("seo_sheet", "SEO作業履歴")

    if not spreadsheet_id:
        print("ERROR: settings.sheets.json に spreadsheet_id がありません", file=sys.stderr)
        sys.exit(1)

    service = get_service(credentials_path)
    ensure_header(service, spreadsheet_id, sheet_name)

    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        args.type,
        args.url,
        args.keywords,
        args.summary,
        args.agent,
        args.result,
        args.detail,
    ]
    append_row(service, spreadsheet_id, sheet_name, row)
    print(f"記録完了: [{args.type}] {args.summary}")


if __name__ == "__main__":
    main()
