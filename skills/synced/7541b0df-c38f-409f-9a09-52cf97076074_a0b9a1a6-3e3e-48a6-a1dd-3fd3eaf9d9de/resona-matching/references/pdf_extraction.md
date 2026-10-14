# PDF抽出リファレンス

りそな振替照合スキルで使用するPDF読み取り手法の詳細ドキュメント。

---

## 振替一覧PDFの抽出戦略

### 優先順位

```
1. pdfplumber（列ベース抽出）
2. pdftotext -layout（テキスト整形抽出）
3. pdftoppm → 視覚抽出（ラスタライズフォールバック）
```

### pdfplumber による列抽出（第一選択）

```python
import pdfplumber
import re

def extract_resona_table(pdf_path: str) -> list[dict]:
    """
    りそな振替一覧PDFから顧客番号・預金者名・入金金額を抽出する。
    Returns:
        list of {"customer_id": str, "name": str, "amount": int}
    """
    records = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if row is None:
                        continue
                    # 顧客番号・預金者名・金額の列インデックスは
                    # 実際のPDFレイアウトに合わせて調整すること
                    customer_id = (row[0] or "").strip()
                    name        = (row[1] or "").strip()
                    amount_raw  = (row[2] or "").strip()

                    # 金額のカンマ・円記号を除去して整数化
                    amount_str = re.sub(r"[^\d]", "", amount_raw)
                    if not customer_id or not amount_str:
                        continue

                    records.append({
                        "customer_id": customer_id,
                        "key4": customer_id[-4:],   # 照合キー（下4桁）
                        "name": name,
                        "amount": int(amount_str),
                    })
    return records
```

> **列インデックスの調整**  
> りそなPDFのフォーマットは変更されることがある。  
> 初回実行時は `page.extract_tables()` の生データをプリントして列順を確認すること。

---

### pdftotext フォールバック（第二選択）

pdfplumber でテーブルが取れない場合（ヘッダー行のみ取得・空行多数など）に使用する。

```bash
# レイアウト保持モードでテキスト化
pdftotext -layout resona.pdf resona.txt
```

```python
import subprocess
import re

def extract_resona_text_fallback(pdf_path: str) -> list[dict]:
    """
    pdftotext -layout の出力から固定幅列を正規表現でパースする。
    """
    result = subprocess.run(
        ["pdftotext", "-layout", pdf_path, "-"],
        capture_output=True, text=True
    )
    records = []
    for line in result.stdout.splitlines():
        # 例: "  1234567890  山田太郎          10,000"
        # パターンは実際のPDF出力に合わせて調整すること
        m = re.match(r"\s*(\d{7,})\s+(.+?)\s+([\d,]+)\s*$", line)
        if m:
            customer_id = m.group(1).strip()
            name        = m.group(2).strip()
            amount      = int(m.group(3).replace(",", ""))
            records.append({
                "customer_id": customer_id,
                "key4": customer_id[-4:],
                "name": name,
                "amount": amount,
            })
    return records
```

---

### ラスタライズ＋視覚抽出（第三選択・フォールバック）

文字化けや暗号化されたPDFで上記2手法が使えない場合のみ使用する。

```bash
# 150DPIでJPEGに変換（全ページ）
pdftoppm -jpeg -r 150 resona.pdf /tmp/resona_page
ls /tmp/resona_page-*.jpg
```

変換後、各ページ画像をClaudeのビジョン機能で読み取り、
テキスト抽出結果と同様の辞書形式に整形する。

---

## 請求書PDFの金額抽出

請求書は1ファイル1顧客。金額フィールドの場所はテンプレートに依存する。

```python
import pdfplumber
import re

def extract_invoice_amount(pdf_path: str) -> int | None:
    """
    請求書PDFから請求金額（税込）を抽出する。
    金額が見つからない場合は None を返す。
    """
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += (page.extract_text() or "")

    # 「合計」「請求金額」「税込」などのキーワード後の数値を探す
    patterns = [
        r"(?:ご請求金額|請求金額|合計金額|税込合計)[^\d]*([\d,]+)",
        r"([\d,]+)\s*円\s*(?:（税込）|\(税込\))",
    ]
    for pattern in patterns:
        m = re.search(pattern, full_text)
        if m:
            return int(m.group(1).replace(",", ""))

    return None  # 抽出失敗
```

> **テンプレート依存の注意**  
> 請求書のフォーマットが複数種類ある場合は、パターン一覧を拡張するか  
> ラスタライズ＋視覚抽出にフォールバックすること。

---

## 文字化け・抽出失敗時のチェックリスト

```bash
# フォント埋め込み確認
pdffonts target.pdf

# テキスト抽出の簡易確認
pdftotext -f 1 -l 1 target.pdf - | head -30
```

| 症状 | 原因 | 対処 |
|------|------|------|
| 文字が□や？になる | フォント未埋め込み | ラスタライズ＋視覚抽出へ切替 |
| テキストが空 | スキャンPDF（画像のみ） | `pytesseract` OCRを適用 |
| 列がずれる | 固定幅フォント以外 | `pdfplumber` のbbox指定で列を絞り込む |
