"""
detect_target_folder.py

実行月から自動的に「前月」の作業フォルダを特定するユーティリティ。
"""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path


def get_target_month(year: int | None = None, month: int | None = None) -> tuple[int, int]:
    """
    照合対象の年月を返す。
    引数省略時は「実行月の前月」を自動算出する。

    Returns:
        (year, month) のタプル
    """
    if year is not None and month is not None:
        return year, month

    today = date.today()
    if today.month == 1:
        return today.year - 1, 12
    return today.year, today.month - 1


def find_target_folder(base_dir: str | Path, year: int, month: int) -> Path | None:
    """
    base_dir 配下から "{YYYY}年{M}月" パターンに一致するフォルダを探す。

    Args:
        base_dir: 作業フォルダのルートパス
        year:     対象年
        month:    対象月

    Returns:
        見つかった場合は Path オブジェクト、見つからない場合は None
    """
    base = Path(base_dir)
    # フォルダ名候補（ゼロパディングあり・なし両方に対応）
    candidates = [
        f"{year}年{month}月",
        f"{year}年{month:02d}月",
    ]
    for name in candidates:
        candidate = base / name
        if candidate.is_dir():
            return candidate

    return None


def find_resona_pdf(folder: Path) -> Path | None:
    """
    指定フォルダ内からりそな振替一覧PDFを検索する。
    複数ヒットした場合は None を返し、呼び出し元でユーザーに選択させる。

    Returns:
        単一ファイルが見つかった場合は Path、それ以外は None
    """
    # 「りそな」を含むPDFを優先検索
    matches = list(folder.glob("*りそな*.pdf"))
    if not matches:
        # フォールバック：PDF全件から手動選択
        matches = list(folder.glob("*.pdf"))

    if len(matches) == 1:
        return matches[0]

    # 複数または0件の場合は呼び出し元へ委譲
    return None


def find_invoice_pdfs(folder: Path) -> list[Path]:
    """
    invoices サブフォルダ、または folder 直下から請求書PDFを収集する。

    ファイル名規則: {Ymd}-{NNNN}U.pdf
    規則外のファイルはスキップ一覧に追加する。

    Returns:
        (valid_files, skipped_files) のタプル
    """
    import re

    invoice_dir = folder / "invoices"
    search_dir = invoice_dir if invoice_dir.is_dir() else folder

    pattern = re.compile(r"^\d{8}-\d{4}U\.pdf$", re.IGNORECASE)

    valid: list[Path] = []
    skipped: list[Path] = []

    for f in sorted(search_dir.glob("*.pdf")):
        if pattern.match(f.name):
            valid.append(f)
        else:
            skipped.append(f)

    return valid, skipped


# ---------------------------------------------------------------------------
# デバッグ用: 単体実行
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    base = sys.argv[1] if len(sys.argv) > 1 else "."
    year, month = get_target_month()
    print(f"対象月: {year}年{month}月")

    folder = find_target_folder(base, year, month)
    if folder:
        print(f"対象フォルダ: {folder}")
    else:
        print(f"ERROR: {year}年{month}月 フォルダが見つからない！")
