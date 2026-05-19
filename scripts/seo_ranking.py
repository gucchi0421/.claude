#!/usr/bin/env python3.12
"""
キーワード順位遷移をGoogleスプレッドシートに記録するスクリプト。

列構成: キーワード | 対象URL | トレンド | [日付列... 古→新]

使い方:
  python3.12 ~/.claude/scripts/seo_ranking.py \
    --keyword "SEO対策" \
    --url "https://example.com/blog/seo" \
    --rank 5
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

COL_KEYWORD    = 0
COL_URL        = 1
COL_SPARKLINE  = 2
COL_DATE_START = 3


def rgb(r: int, g: int, b: int) -> dict:
    return {"red": r / 255, "green": g / 255, "blue": b / 255}


C = {
    "header_bg":  rgb(0x1e, 0x3a, 0x5f),
    "header_fg":  rgb(0xFF, 0xFF, 0xFF),
    "keyword_bg": rgb(0xE8, 0xEA, 0xF6),
    "improved":   rgb(0xC8, 0xE6, 0xC9),
    "declined":   rgb(0xFF, 0xCD, 0xD2),
    "new_entry":  rgb(0xE1, 0xF5, 0xFE),
    "same":       rgb(0xFF, 0xFF, 0xFF),
    "stripe":     rgb(0xFA, 0xFA, 0xFD),
}
SPARKLINE_COLOR = "#1565C0"
HEADER = ["キーワード", "対象URL", "トレンド"]


def load_global_env() -> dict[str, str]:
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


def col_letter(index: int) -> str:
    s = ""
    n = index + 1
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def get_sheet_id(service, spreadsheet_id: str, sheet_name: str) -> int | None:
    meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    for sheet in meta["sheets"]:
        if sheet["properties"]["title"] == sheet_name:
            return sheet["properties"]["sheetId"]
    return None


def create_sheet(service, spreadsheet_id: str, sheet_name: str) -> int:
    resp = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": [{"addSheet": {"properties": {"title": sheet_name}}}]},
    ).execute()
    return resp["replies"][0]["addSheet"]["properties"]["sheetId"]


def setup_sheet(service, spreadsheet_id: str, sheet_id: int) -> None:
    requests = [
        # ヘッダー行スタイル
        {
            "repeatCell": {
                "range": {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 1},
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": C["header_bg"],
                        "textFormat": {
                            "foregroundColor": C["header_fg"],
                            "bold": True,
                            "fontSize": 10,
                        },
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE",
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)",
            }
        },
        # キーワード列（A）スタイル
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 1,
                    "startColumnIndex": COL_KEYWORD,
                    "endColumnIndex": COL_KEYWORD + 1,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": C["keyword_bg"],
                        "textFormat": {"bold": True},
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat)",
            }
        },
        # ヘッダー行の高さ
        {
            "updateDimensionProperties": {
                "range": {"sheetId": sheet_id, "dimension": "ROWS", "startIndex": 0, "endIndex": 1},
                "properties": {"pixelSize": 40},
                "fields": "pixelSize",
            }
        },
        # 列幅: キーワード=180, URL=230, トレンド=110
        *[
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": col,
                        "endIndex": col + 1,
                    },
                    "properties": {"pixelSize": width},
                    "fields": "pixelSize",
                }
            }
            for col, width in [(COL_KEYWORD, 180), (COL_URL, 230), (COL_SPARKLINE, 110)]
        ],
        # 1行 + 2列を固定
        {
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sheet_id,
                    "gridProperties": {"frozenRowCount": 1, "frozenColumnCount": 2},
                },
                "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount",
            }
        },
        # 交互ストライプ
        {
            "addBanding": {
                "bandedRange": {
                    "range": {"sheetId": sheet_id, "startRowIndex": 1},
                    "rowProperties": {
                        "firstBandColor": {"red": 1, "green": 1, "blue": 1},
                        "secondBandColor": C["stripe"],
                    },
                }
            }
        },
    ]
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id, body={"requests": requests}
    ).execute()


def get_all_values(service, spreadsheet_id: str, sheet_name: str) -> list[list]:
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=f"'{sheet_name}'!A:ZZ")
        .execute()
    )
    return result.get("values", [])


def sparkline_formula(row: int, date_col_count: int) -> str:
    if date_col_count == 0:
        return "—"
    start = col_letter(COL_DATE_START)
    end = col_letter(COL_DATE_START + date_col_count - 1)
    return (
        f'=IFERROR(SPARKLINE({start}{row}:{end}{row},'
        f'{{"charttype","line";"color","{SPARKLINE_COLOR}";"lineWidth",2}}),"—")'
    )


def write_value(service, spreadsheet_id: str, sheet_name: str, cell: str, value, input_option: str = "RAW") -> None:
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"'{sheet_name}'!{cell}",
        valueInputOption=input_option,
        body={"values": [[value]]},
    ).execute()


def apply_cell_format(service, spreadsheet_id: str, sheet_id: int, row: int, col: int, bg: dict) -> None:
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": row,
                            "endRowIndex": row + 1,
                            "startColumnIndex": col,
                            "endColumnIndex": col + 1,
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "backgroundColor": bg,
                                "horizontalAlignment": "CENTER",
                                "textFormat": {"bold": True, "fontSize": 11},
                            }
                        },
                        "fields": "userEnteredFormat(backgroundColor,horizontalAlignment,textFormat)",
                    }
                }
            ]
        },
    ).execute()


def format_date_col(service, spreadsheet_id: str, sheet_id: int, col: int) -> None:
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "requests": [
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": sheet_id,
                            "dimension": "COLUMNS",
                            "startIndex": col,
                            "endIndex": col + 1,
                        },
                        "properties": {"pixelSize": 90},
                        "fields": "pixelSize",
                    }
                },
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": 0,
                            "endRowIndex": 1,
                            "startColumnIndex": col,
                            "endColumnIndex": col + 1,
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "backgroundColor": C["header_bg"],
                                "textFormat": {
                                    "foregroundColor": C["header_fg"],
                                    "bold": True,
                                    "fontSize": 10,
                                },
                                "horizontalAlignment": "CENTER",
                            }
                        },
                        "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)",
                    }
                },
            ]
        },
    ).execute()


def main() -> None:
    parser = argparse.ArgumentParser(description="キーワード順位をスプレッドシートに記録する")
    parser.add_argument("--keyword", required=True, help="対策キーワード")
    parser.add_argument("--url", default="", help="対象ページのURL")
    parser.add_argument("--rank", required=True, type=int, help="現在の検索順位（数値）")
    parser.add_argument("--date", default="", help="日付（省略時は今日 YYYY-MM-DD）")
    args = parser.parse_args()

    today = args.date or date.today().strftime("%Y-%m-%d")

    env = load_global_env()
    credentials_path = env.get("CLAUDE_GCP_CREDENTIALS", "")
    if not credentials_path:
        print("ERROR: CLAUDE_GCP_CREDENTIALS が ~/.claude/.env に未設定", file=sys.stderr)
        sys.exit(1)

    settings_path = find_settings(Path.cwd())
    if not settings_path:
        print("ERROR: .claude/settings.sheets.json が見つかりません", file=sys.stderr)
        sys.exit(1)

    settings = json.loads(settings_path.read_text())
    spreadsheet_id = settings.get("spreadsheet_id", "")
    sheet_name = settings.get("ranking_sheet", "キーワード順位遷移")
    if not spreadsheet_id:
        print("ERROR: settings.sheets.json に spreadsheet_id がありません", file=sys.stderr)
        sys.exit(1)

    service = get_service(credentials_path)

    sheet_id = get_sheet_id(service, spreadsheet_id, sheet_name)
    if sheet_id is None:
        sheet_id = create_sheet(service, spreadsheet_id, sheet_name)
        setup_sheet(service, spreadsheet_id, sheet_id)

    values = get_all_values(service, spreadsheet_id, sheet_name)
    if not values:
        write_value(service, spreadsheet_id, sheet_name, "A1", HEADER[0])
        write_value(service, spreadsheet_id, sheet_name, "B1", HEADER[1])
        write_value(service, spreadsheet_id, sheet_name, "C1", HEADER[2])
        values = [HEADER[:]]

    header_row = list(values[0]) if values else HEADER[:]

    # 日付列を探す / 追加
    date_cols = header_row[COL_DATE_START:]
    if today in date_cols:
        date_col_idx = COL_DATE_START + date_cols.index(today)
    else:
        date_col_idx = len(header_row)
        write_value(service, spreadsheet_id, sheet_name, f"{col_letter(date_col_idx)}1", today)
        format_date_col(service, spreadsheet_id, sheet_id, date_col_idx)
        header_row.append(today)

    # キーワード行を探す / 追加
    kw_values = [row[COL_KEYWORD] if len(row) > COL_KEYWORD else "" for row in values[1:]]
    if args.keyword in kw_values:
        kw_row_idx = kw_values.index(args.keyword) + 1
        # 直前の順位を取得
        row_data = values[kw_row_idx] if kw_row_idx < len(values) else []
        prev_rank = None
        if date_col_idx > COL_DATE_START:
            prev_col = date_col_idx - 1
            prev_val = row_data[prev_col] if len(row_data) > prev_col else ""
            try:
                prev_rank = int(prev_val)
            except (ValueError, TypeError):
                prev_rank = None
        is_new_keyword = False
    else:
        kw_row_idx = len(values)
        is_new_keyword = True
        prev_rank = None
        write_value(service, spreadsheet_id, sheet_name, f"A{kw_row_idx + 1}", args.keyword)
        if args.url:
            write_value(service, spreadsheet_id, sheet_name, f"B{kw_row_idx + 1}", args.url)

    # 順位を書き込む
    write_value(
        service, spreadsheet_id, sheet_name,
        f"{col_letter(date_col_idx)}{kw_row_idx + 1}",
        args.rank,
    )

    # スパークラインを更新
    date_col_count = len(header_row) - COL_DATE_START
    formula = sparkline_formula(kw_row_idx + 1, date_col_count)
    write_value(
        service, spreadsheet_id, sheet_name,
        f"{col_letter(COL_SPARKLINE)}{kw_row_idx + 1}",
        formula,
        input_option="USER_ENTERED",
    )

    # セルの色
    if is_new_keyword or prev_rank is None:
        bg = C["new_entry"]
        change_str = "初回記録"
    elif args.rank < prev_rank:
        bg = C["improved"]
        change_str = f"↑ {prev_rank - args.rank}位改善（{prev_rank}→{args.rank}）"
    elif args.rank > prev_rank:
        bg = C["declined"]
        change_str = f"↓ {args.rank - prev_rank}位下落（{prev_rank}→{args.rank}）"
    else:
        bg = C["same"]
        change_str = f"→ 変化なし（{args.rank}位）"

    apply_cell_format(service, spreadsheet_id, sheet_id, kw_row_idx, date_col_idx, bg)

    print(f"記録完了: [{args.keyword}] 順位{args.rank}位 / {change_str}")


if __name__ == "__main__":
    main()
