---
name: support-ryoyukai
description: 大阪府猟友会ウェブサイトの年間行事を追加・更新するスキル。「猟友会」「年間行事」「行事追加」「行事更新」「イベント追加」「講習会追加」「射撃会追加」などのキーワードが含まれる場合は必ずこのスキルを使うこと。PDF（案内・申込書）から行事情報を読み取り、events/index.html と index.html の2ファイルを同時に更新する。PDFのリネームもあわせて行う。サーバーへのアップロードは行わない。
---

# 大阪府猟友会 年間行事追加・更新スキル

## 前提

- **サーバーへのアップロードは絶対に行わない**（Step 3 は手順説明のみ）
- ワークスペースフォルダはユーザーが指定・接続済みのフォルダを使う
- 更新対象は常に 2 ファイル同時：
  - `events/index.html`（年間行事ページ）
  - `index.html`（トップページ 新着情報）

---

## Step 1：PDF の確認・種別判断・リネーム

### 1-1：PDF を探す

ワークスペースフォルダ内の PDF ファイルを Glob で検索する。

### 1-2：内容を読んで種別を判断する

PDF を Read ツールで読み取り、内容から以下を判断する：

| 種別           | 見分け方                                           | リネーム後のファイル名 |
| -------------- | -------------------------------------------------- | ---------------------- |
| **案内 PDF**   | 行事の詳細（日時・場所・費用など）が記載されている | `YYYYMMDD-1.pdf`       |
| **申込書 PDF** | 氏名・住所・銃種など記入欄が並んでいる             | `YYYYMMDD-2.pdf`       |

`YYYYMMDD` は**本日のアップロード日**（開催日ではない）！

例：本日が 2026 年 4 月 28 日 → `20260428-1.pdf`（案内）、`20260428-2.pdf`（申込書）

### 1-3：案内 PDF から行事情報を抽出する

- **行事名**（例：第 64 回 銃砲所持希望者講習会（予備講習会））
- **開催日**（例：令和 8 年 5 月 23 日（土））
- **場所**（例：大阪府社会福祉会館 404 号室）
- **各 PDF のファイルサイズ**（Read ツールの KB 表示を四捨五入して使う）

### 1-4：PDF をリネームする

元の PDF をコピーまたはリネームして `YYYYMMDD-1.pdf`、`YYYYMMDD-2.pdf` としてワークスペース内に保存する（元ファイルはそのまま残してよい）！

---

## Step 2：HTML ファイルの編集

### イベント ID の命名規則

| 項目        | 命名規則         | 例               |
| ----------- | ---------------- | ---------------- |
| イベント ID | `event-YYYYMMDD` | `event-20260428` |

### Step 2-1：events/index.html の更新

`<table class="sheet_01">` 内のヘッダー行（`<tr><th>日時</th>...`）の直後に以下のブロックを追加する：

```html
<tr>
  <td class="date" id="event-YYYYMMDD">令和〇年〇月〇日（〇）<br /></td>
  <td>
    <a href="../images/events/YYYYMMDD-1.pdf" target="_blank">行事名</a>
  </td>
  <td class="apply">
    <a
      href="../images/events/YYYYMMDD-2.pdf"
      target="_blank"
      class="inlineBlock"
      ><img src="../images/common/pdf_icon.png" width="25" height="25" /></a
    >〇〇KB
  </td>
  <td class="place">場所名</td>
</tr>
```

**申込書がない場合**（`class="apply"` の代わり）：

```html
<td class="blank">－</td>
```

**案内 PDF もない場合**（行事名リンクなし）：

```html
<td>行事名</td>
```

### Step 2-2：index.html の更新

新着情報テーブル `<table class="sheet_01">` の先頭（既存の最初の `<tr>` の直前）に追加する：

```html
<tr>
  <th>YYYY.MM.DD<img src="images/common/badge_01.gif" /></th>
  <td>
    <a href="events/#event-YYYYMMDD">行事名のご案内</a>
  </td>
</tr>
```

- 日付は `YYYY.MM.DD` 形式（例：`2026.04.28`）
- `href` のアンカーは events/index.html の `id` と必ず一致させる

---

## Step 3：アップロード手順（説明のみ／実行しない）

更新完了後、以下をユーザーに伝える：

**FTP でアップロードするファイル：**

| ファイル                        | アップロード先               |
| ------------------------------- | ---------------------------- |
| `index.html`（トップページ）    | `public_html/`               |
| `events/index.html`（年間行事） | `public_html/events/`        |
| `YYYYMMDD-1.pdf`（案内 PDF）    | `public_html/images/events/` |
| `YYYYMMDD-2.pdf`（申込書 PDF）  | `public_html/images/events/` |

**FTP 情報の場所：**
`\\IODATA-35A52A\disk1\【顧客情報】\【ＦＴＰ情報／サーバー情報】\O - 大阪府猟友会`

---

## チェックリスト

作業完了後、確認してユーザーに報告する：

- [ ] 案内 PDF と申込書 PDF を正しく判別できているか
- [ ] PDF が `YYYYMMDD-1.pdf` / `YYYYMMDD-2.pdf` にリネームされているか
- [ ] `id="event-YYYYMMDD"` が本日の日付になっているか
- [ ] `events/index.html` の href が正しい PDF パスを指しているか
- [ ] `index.html` のアンカー `#event-YYYYMMDD` が events/index.html の id と一致しているか
- [ ] 申込書の有無に応じて `class="apply"` / `class="blank"` が正しいか
- [ ] 新着情報の日付が本日の日付（`YYYY.MM.DD`）になっているか
- [ ] 両ファイルとも**テーブルの先頭**（最新が上）に追加されているか

---

## 注意事項

- イベント ID は「アップロード日（本日）」ベース、開催日ではない
- 複数案内がある場合はファイル名末尾を `-1`、`-2`、`-3` と連番
- 既存の HTML のインデントスタイルを必ず踏襲する
