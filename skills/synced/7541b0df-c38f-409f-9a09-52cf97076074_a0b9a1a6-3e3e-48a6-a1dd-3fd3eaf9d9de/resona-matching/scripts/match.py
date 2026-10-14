"""
match.py

りそな振替一覧PDFと請求書PDF群の金額照合スクリプト本体。

使用方法:
    python scripts/match.py --base-dir /path/to/作業フォルダ
    python scripts/match.py --base-dir /path/to/作業フォルダ --year 2024 --month 3
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import pdfplumber


# ---------------------------------------------------------------------------
# データクラス
# ---------------------------------------------------------------------------

@dataclass
class ResonaRecord:
    """りそな振替一覧の1行分"""
    customer_id: str         # 顧客番号（フル桁）
    key4: str                # 照合キー（下4桁）
    name: str                # 預金者名
    amount: int              # 入金金額（税込）


@dataclass
class InvoiceRecord:
    """請求書PDFの1ファイル分"""
    filepath: Path           # ファイルパス
    key4: str                # ファイル名から取得した下4桁
    amount: int | None       # 請求金額（抽出失敗時は None）


@dataclass
class MatchResult:
    """照合結果1行分"""
    key4: str
    name: str
    payment_amount: int | None
    invoice_file: str
    invoice_amount: int | None
    diff: int | None         # 入金 - 請求（正=過入金、負=不足）
    status: str              # ✅ ⚠️ ❓ 🔴


# ---------------------------------------------------------------------------
# PDF抽出ロジック
# ---------------------------------------------------------------------------

def extract_resona_records(pdf_path: Path) -> tuple[list[ResonaRecord], list[str]]:
    """
    りそな振替一覧PDFを解析して ResonaRecord のリストを返す。

    Returns:
        (records, errors) のタプル
        errors: 読み取れなかった旨のメッセージ一覧
    """
    records: list[ResonaRecord] = []
    errors: list[str] = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        if not row:
                            continue

                        # --- 列インデックスは実際のPDFに合わせて調整すること ---
                        # 期待する列順: [顧客番号, 預金者名, 入金金額, ...]
                        if len(row) < 3:
                            continue

                        customer_id = (row[0] or "").strip()
                        name        = (row[1] or "").strip()
                        amount_raw  = (row[2] or "").strip()

                        # ヘッダー行スキップ（数字以外の顧客番号）
                        if not re.match(r"^\d+$", customer_id):
                            continue

                        amount_str = re.sub(r"[^\d]", "", amount_raw)
                        if not amount_str:
                            continue

                        records.append(ResonaRecord(
                            customer_id=customer_id,
                            key4=customer_id[-4:],
                            name=name,
                            amount=int(amount_str),
                        ))

    except Exception as e:
        errors.append(f"{pdf_path.name}: 読み取りエラー ({e})")

    return records, errors


def extract_invoice_amount(pdf_path: Path) -> int | None:
    """
    請求書PDFから請求金額（税込）を抽出する。
    抽出失敗時は None を返す。
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                full_text += (page.extract_text() or "")
    except Exception:
        return None

    # 金額パターン（テンプレートに応じて拡張すること）
    patterns = [
        r"(?:ご請求金額|請求金額|合計金額|税込合計)[^\d]*([\d,]+)",
        r"([\d,]+)\s*円\s*(?:（税込）|\(税込\))",
        r"合\s*計[^\d]*([\d,]+)",
    ]
    for pattern in patterns:
        m = re.search(pattern, full_text)
        if m:
            return int(m.group(1).replace(",", ""))

    return None


# ---------------------------------------------------------------------------
# 照合ロジック
# ---------------------------------------------------------------------------

def match_records(
    resona_records: list[ResonaRecord],
    invoice_records: list[InvoiceRecord],
) -> list[MatchResult]:
    """
    顧客番号下4桁をキーとして振替データと請求書を突合する。
    4つのケース（正常・差異・請求書なし・未入金）をすべて記録する。
    """
    results: list[MatchResult] = []

    resona_map:  dict[str, ResonaRecord]  = {r.key4: r for r in resona_records}
    invoice_map: dict[str, InvoiceRecord] = {i.key4: i for i in invoice_records}

    all_keys = set(resona_map.keys()) | set(invoice_map.keys())

    for key4 in sorted(all_keys):
        resona  = resona_map.get(key4)
        invoice = invoice_map.get(key4)

        payment_amount  = resona.amount  if resona  else None
        invoice_amount  = invoice.amount if invoice else None
        invoice_file    = invoice.filepath.name if invoice else "（なし）"
        name            = resona.name if resona else "-"

        # ステータス判定
        if resona and invoice:
            if invoice_amount is None:
                status = "⚠️ 金額抽出失敗"
                diff   = None
            elif payment_amount == invoice_amount:
                status = "✅ 正常"
                diff   = 0
            else:
                diff   = payment_amount - invoice_amount  # 正=過入金、負=不足
                status = "⚠️ 差異あり"
        elif resona and not invoice:
            status = "❓ 請求書なし"
            diff   = None
        else:
            status = "🔴 未入金"
            diff   = None

        results.append(MatchResult(
            key4=key4,
            name=name,
            payment_amount=payment_amount,
            invoice_file=invoice_file,
            invoice_amount=invoice_amount,
            diff=diff,
            status=status,
        ))

    return results


# ---------------------------------------------------------------------------
# レポート出力
# ---------------------------------------------------------------------------

def fmt_amount(amount: int | None) -> str:
    """金額を3桁カンマ区切りの文字列にフォーマットする"""
    if amount is None:
        return "-"
    return f"{amount:,}"


def fmt_diff(diff: int | None) -> str:
    """差異を ▲付きの文字列にフォーマットする（負の場合は ▲）"""
    if diff is None:
        return "-"
    if diff == 0:
        return "なし"
    if diff > 0:
        return f"+{diff:,}"
    return f"▲{abs(diff):,}"


def build_report(
    results: list[MatchResult],
    skipped_files: list[Path],
    errors: list[str],
    year: int,
    month: int,
) -> str:
    """Markdown形式のレポート文字列を生成する"""
    lines: list[str] = []

    lines.append(f"# りそな振替照合レポート — {year}年{month}月分\n")

    # メインテーブル
    lines.append("| 顧客番号下4桁 | 預金者名 | 入金金額 | 請求書ファイル | 請求金額 | 差異 | ステータス |")
    lines.append("|:---:|:---|---:|:---|---:|:---:|:---:|")

    total_payment = 0
    total_invoice = 0

    for r in results:
        if r.payment_amount:
            total_payment += r.payment_amount
        if r.invoice_amount:
            total_invoice += r.invoice_amount

        lines.append(
            f"| {r.key4} "
            f"| {r.name} "
            f"| {fmt_amount(r.payment_amount)} "
            f"| {r.invoice_file} "
            f"| {fmt_amount(r.invoice_amount)} "
            f"| {fmt_diff(r.diff)} "
            f"| {r.status} |"
        )

    # 合計行
    lines.append(
        f"| | | **{total_payment:,}** | | **{total_invoice:,}** | | |"
    )

    # サマリー
    ok_count    = sum(1 for r in results if r.status == "✅ 正常")
    diff_count  = sum(1 for r in results if "差異" in r.status)
    noInv_count = sum(1 for r in results if "請求書なし" in r.status)
    unPaid_count = sum(1 for r in results if "未入金" in r.status)

    lines.append("\n## サマリー\n")
    lines.append(f"- ✅ 正常: {ok_count} 件")
    lines.append(f"- ⚠️ 差異あり: {diff_count} 件")
    lines.append(f"- ❓ 請求書なし（入金あり）: {noInv_count} 件")
    lines.append(f"- 🔴 未入金（請求書あり）: {unPaid_count} 件")
    lines.append(f"- 入金合計: {total_payment:,} 円")
    lines.append(f"- 請求合計: {total_invoice:,} 円")
    lines.append(f"- 差額合計: {fmt_diff(total_payment - total_invoice)}")

    # スキップファイル
    if skipped_files:
        lines.append("\n## 命名規則不正ファイル（スキップ）\n")
        for f in skipped_files:
            lines.append(f"- `{f.name}`")

    # エラー
    if errors:
        lines.append("\n## 読み取りエラー\n")
        for e in errors:
            lines.append(f"- {e}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# エントリーポイント
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="りそな振替照合スクリプト")
    parser.add_argument("--base-dir", required=True, help="作業フォルダのルートパス")
    parser.add_argument("--year",  type=int, default=None, help="対象年（省略時: 前月）")
    parser.add_argument("--month", type=int, default=None, help="対象月（省略時: 前月）")
    args = parser.parse_args()

    # detect_target_folder から対象月・フォルダを取得
    sys.path.insert(0, str(Path(__file__).parent))
    from detect_target_folder import (
        find_invoice_pdfs,
        find_resona_pdf,
        find_target_folder,
        get_target_month,
    )

    year, month = get_target_month(args.year, args.month)
    print(f"対象月: {year}年{month}月")

    folder = find_target_folder(args.base_dir, year, month)
    if not folder:
        print(f"ERROR: {year}年{month}月 フォルダが見つからない！")
        sys.exit(1)
    print(f"対象フォルダ: {folder}")

    # りそなPDF
    resona_pdf = find_resona_pdf(folder)
    if not resona_pdf:
        print("ERROR: りそな振替一覧PDFが特定できない！手動でパスを指定してください。")
        sys.exit(1)
    print(f"振替一覧PDF: {resona_pdf.name}")

    # 請求書PDF一覧
    valid_invoices, skipped = find_invoice_pdfs(folder)
    print(f"請求書PDF: {len(valid_invoices)} 件（スキップ: {len(skipped)} 件）")

    # 抽出
    resona_records, errors = extract_resona_records(resona_pdf)
    print(f"振替レコード: {len(resona_records)} 件")

    invoice_records: list[InvoiceRecord] = []
    for inv_path in valid_invoices:
        key4 = inv_path.stem[-5:-1]  # "20240301-0001U" → "0001"
        amount = extract_invoice_amount(inv_path)
        if amount is None:
            errors.append(f"{inv_path.name}: 金額抽出失敗")
        invoice_records.append(InvoiceRecord(
            filepath=inv_path,
            key4=key4,
            amount=amount,
        ))

    # 照合
    results = match_records(resona_records, invoice_records)

    # レポート出力
    report = build_report(results, skipped, errors, year, month)
    print("\n" + "=" * 60)
    print(report)
    print("=" * 60)

    # ファイル保存
    output_path = folder / f"照合レポート_{year}{month:02d}.md"
    output_path.write_text(report, encoding="utf-8")
    print(f"\nレポート保存先: {output_path}")


if __name__ == "__main__":
    main()
