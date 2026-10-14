---
name: ga4-auto-report
description: "毎月のアクセス解析レポート（Google Analytics 4）をPDFでダウンロードし、顧客フォルダへ保存→Chatworkへ通知→作業フォルダをZIP化して送信するワークフロー。 ユーザーが「今月分の作業」「アクセス解析」「レポートダウンロード」と言ったら必ずこのスキルを使うこと。"
---

---
name: ga4-auto-report
description: "毎月のアクセス解析レポート（Google Analytics 4）をPDFでダウンロードし、顧客フォルダへ保存→Chatworkへ通知→作業フォルダをZIP化して送信するワークフロー。 ユーザーが「今月分の作業」「アクセス解析」「レポートダウンロード」と言ったら必ずこのスキルを使うこと。"
---

# アクセス解析レポートダウンロード スキル

## 概要

毎月1回、Google Analytics 4（GA4）から指定顧客のレポートをPDFでダウンロードし、
所定フォルダへ保存・Chatworkへ通知する作業を自動化するスキル。

---

## ⚡ 作業開始時に必ず最初に実行すること（パス自動検出）

作業者のWindowsユーザー名・セッションIDは毎回異なる可能性があるため、
**作業開始時に必ずbashで動的に検出**すること。

```bash
# セッションIDを検出（Claude Cowork環境）
SESSION_ID=$(ls /sessions/ 2>/dev/null | head -1)

# パスを組み立て
if [ -n "$SESSION_ID" ]; then
  MNT_BASE="/sessions/${SESSION_ID}/mnt"
else
  MNT_BASE="/mnt"
fi

DOWNLOADS_PATH="${MNT_BASE}/Downloads"
WORK_BASE="${MNT_BASE}/アクセス解析"

# Windowsユーザー名を検出（ログ表示用）
WIN_USER=$(ls "${MNT_BASE}/Users/" 2>/dev/null | grep -v 'Public\|Default\|All Users' | head -1)

echo "=== 検出結果 ==="
echo "セッションID    : ${SESSION_ID:-（直接マウント）}"
echo "Windowsユーザー : ${WIN_USER:-（不明）}"
echo "Downloadsパス   : ${DOWNLOADS_PATH}"
echo "作業ベースパス  : ${WORK_BASE}"
echo ""

# 存在確認
ls "${DOWNLOADS_PATH}" > /dev/null 2>&1 && echo "✅ Downloads 確認OK" || echo "❌ Downloads が見つからない"
ls "${WORK_BASE}"      > /dev/null 2>&1 && echo "✅ アクセス解析フォルダ 確認OK" || echo "❌ アクセス解析フォルダが見つからない"
```

> ⚠️ パスが見つからない場合はユーザーに確認を取ること。絶対にパスを決め打ちしない。

以降の手順で `${DOWNLOADS_PATH}` `${WORK_BASE}` `${WORK_FOLDER}` と記載している箇所は、
上記で検出した値に置き換えて実行すること。

---

## 事前準備

### 作業フォルダの準備

1. `${WORK_BASE}/` を開く
2. `■サンプル` フォルダを複製し `20XX年XX月アクセス解析レポート` にリネーム
3. 以後「作業フォルダ」（`${WORK_FOLDER}`）＝この複製フォルダ

### 作業月の日付範囲を決定する

- 作業日が4/21なら：当月=3月（3/1〜3/31）、前月=2月（2/1〜2/28）
- URLパラメータ形式：`_u.date00=YYYYMMDD&_u.date01=YYYYMMDD&_u.date10=YYYYMMDD&_u.date11=YYYYMMDD`
  - date00/date01 = 当月（メイン期間）
  - date10/date11 = 前月（比較期間）

### ダウンロードフォルダのパス対応表

| Windows上のパス | Claude（Linux）からのパス |
|---|---|
| `C:\Users\{WIN_USER}\Downloads` | `${DOWNLOADS_PATH}`（自動検出済み） |

最新ダウンロードファイルの確認：
```bash
ls -t "${DOWNLOADS_PATH}"/*.pdf | head -3
```

---

## 作業の流れ

### ステップ1：クリエイティブエナジーの表示条件を確認

作業フォルダ内 `C - クリエイティブエナジー御中` のサンプルPDFを確認し、
レポートの種類・表示条件をキャッシュする。

### ステップ2：GA4へアクセス

**Googleアカウント：** `seo@a-manage.jp`  
**URL：** `https://analytics.google.com/analytics/web/?authuser=0#/a34342081p306694413/reports/intelligenthome`

ブラウザで開いたら、アカウントが `seo@a-manage.jp` であることを確認する。

### ステップ3：各顧客のPDFをダウンロード

顧客ごとに「ダウンロードすべきレポート種別」を確認し（サンプルPDF参照）、以下の手順を繰り返す。

#### ダウンロード手順（1レポートあたり）

**① プロパティ切り替え**

GA4上部のプロパティセレクターをクリック → 検索ボックスに顧客名を入力 → 対象プロパティを選択。

スクロールで見つからない場合は必ず検索ボックスを使うこと。

**② 正しいレポートURLに移動**

直接URLを組み立てて移動する。基本形：

```
https://analytics.google.com/analytics/web/?authuser=0#/p{プロパティID}/reports/explorer?params=_u.date00%3D{YYYYMMDD}%26_u.date01%3D{YYYYMMDD}%26_u.date10%3D{YYYYMMDD}%26_u.date11%3D{YYYYMMDD}%26_u..nav%3Dmaui&r={レポートID}&collectionId={コレクションID}
```

主要レポートIDとコレクションID：

| レポート名 | r= | collectionId= |
|---|---|---|
| デバイス別割合 | `user-technology-overview` | `user` |
| 閲覧ページランキング | `all-pages-and-screens` | `life-cycle` |
| 検索クエリ | `search-query` | `search-console` |
| 新規とリピーター | `lifecycle-retention-overview` | `life-cycle` |

**③ URLリダイレクト問題への対処（重要）**

直接URLで移動すると `intelligenthome` や他ページにリダイレクトされることがある。これは**そのプロパティにそのコレクションが公開されていない**サインである。

対処手順：
1. 左サイドバーのレポートアイコン（棒グラフ）をクリック
2. サイドバーで目的のセクション（例：ライフサイクル）を探す
3. **サイドバーにそのセクションが存在しない場合 → そのレポートはそのプロパティには存在しない。スキップする。**
4. サイドバーにある場合 → サイドバーから直接クリックして移動し、その後URLのparamsだけ日付を更新する

> **リダイレクト多発プロパティの例（2026年4月時点）：**
> - RE-SOUL（田中啓文総合建築研究所御中）→ ライフサイクルなし
> - 田中啓文総合建築研究所御中 → ライフサイクルなし
> - 全日本不動産協会 → ライフサイクルなし

**④ PDFダウンロード**

1. 画面右上の「このレポートの共有」ボタン（aria-label）をクリック
   - 座標目安：(1136, 248) だが、ウィンドウサイズにより変わる
   - クリックしてもパネルが開かない場合は `find` ツールで `ファイルをダウンロード` ボタンのrefを探す

2. `ファイルをダウンロード` ボタンをクリック

3. `PDF形式でダウンロード` ボタンをクリック（**1回だけ**クリック）

4. ダウンロード完了を確認（Downloadsフォルダに新しいPDFが現れるまで数秒待つ）：
   ```bash
   ls -t "${DOWNLOADS_PATH}"/*.pdf | head -1
   ```

**⑤ PDFを顧客フォルダへ移動**

```bash
# 例：デバイス別割合.pdf を所定フォルダへコピー
cp "${DOWNLOADS_PATH}/ダウンロードされたファイル名.pdf" \
   "${WORK_FOLDER}/顧客フォルダ名/デバイス別割合.pdf"
```

同名ファイルが既にある場合は上書き（`-f` オプション使用）。

**PDFサイズがA4でない場合（Ghostscriptでリサイズ）：**

```bash
gs -sDEVICE=pdfwrite -dNOPAUSE -dBATCH -dSAFER \
   -sPAPERSIZE=a4 -dFIXEDMEDIA -dPDFFitPage \
   -sOutputFile="/path/to/output.pdf" "/path/to/input.pdf"
```

> ⚠️ Cowork環境では外部サイトへのファイルアップロード（avepdf.com等）は「Not allowed」となるため、
> Ghostscriptを使うこと。

---

### ステップ4：進捗記録

1顧客のダウンロードが完了するたびに `${WORK_FOLDER}/アクセス解析進捗メモ.txt` を更新する：

```
■通常レポート
ビューラー大谷 ★
クリエイティブエナジー ★
...
```

`★` や `〇` など何でもよいのでチェックをつける。セッション再開時の再開位置がわかるようにすること。

---

### ステップ5：顧客ごとのChatwork通知

1顧客のダウンロードが完了したら、Chatworkに送信する。

**Chatwork URL：** `https://www.chatwork.com/#!rid373763856`  
**送信先：** 谷口 弘哉

メッセージ形式：
```
【Claude Cowork自動送信】　※試験運用中
{顧客名}のアクセス解析レポート完了：{実際の顧客フォルダのパス}
```

Chatworkへのメッセージ送信手順：
1. `mcp__Claude_in_Chrome__navigate` でURLを開く
2. `mcp__Claude_in_Chrome__find` でメッセージ入力欄を探す（ref_536付近）
3. テキストを入力
4. 送信ボタンをクリック（ユーザーに確認を取ってから送信すること）

---

### ステップ6：全顧客完了後の処理

#### 全完了メッセージをChatworkへ送信

```
【Claude Cowork自動送信】　※試験運用中
〇月分アクセス解析レポートのダウンロード作業一式が完了いたしました。
ご確認よろしくお願いいたします。
パス：{作業フォルダのパス}
```

#### 作業フォルダをZIP化してChatworkへ送信

1. 作業フォルダ全体をZIPに圧縮：
   ```bash
   cd "${WORK_BASE}"
   zip -r "${WORK_FOLDER_NAME}.zip" "${WORK_FOLDER_NAME}/"
   ```

2. ZIPファイルのパスをChatworkメッセージで通知する：
   ```
   【Claude Cowork自動送信】　※試験運用中
   ZIPファイルを作成しました。
   パス：{ZIPファイルのWindowsパス}
   ```

   > ⚠️ Chatworkへの直接ファイル添付はCowork環境では未対応のため、
   > ZIPのローカルパスをメッセージとして通知する。

---

## 顧客リストと注意事項

### 通常レポート対象顧客（2026年4月時点）

| # | 顧客名 | 備考 |
|---|---|---|
| 1 | ビューラー大谷 | |
| 2 | クリエイティブエナジー | |
| 3 | フォーカス | |
| 4 | ホクヨー西部販売 | |
| 5 | 公益社団法人兵庫県柔道整復師会 | |
| 6 | いしかわ矯正クリニック | |
| 7 | 池田商店 | |
| 8 | きかわ歯科 | |
| 9 | 広光印刷 | |
| 10 | 神戸海星病院 | |
| 11 | 神戸海星病院 看護部 | |
| 12 | 神戸海星病院 消化器センター | |
| 13 | 大阪高級葬儀 | |
| 14 | ルビー | |
| 15 | 大平製作所 | |
| 16 | 吉田・吉竹・有田特許 | |
| 17 | サンピア | |
| 18 | RE-SOUL（田中啓文総合建築研究所御中） | ライフサイクルレポートなし |
| 19 | 田中啓文総合建築研究所御中 | ライフサイクルレポートなし |
| 20 | 全日本不動産協会 | ライフサイクルレポートなし |

### ○○検索順位レポート.pdfについて

これは他システム（GRC）のレポートのため、**スキップする**（GA4からダウンロードしない）。

---

## よくあるエラーと対処

### エラー1：URLリダイレクト（`intelligenthome`に戻る）

**原因：** そのプロパティにコレクションが公開されていない  
**対処：** サイドバーで確認 → なければスキップ、あればサイドバーから遷移後にURLのdate paramsを更新

### エラー2：共有パネルが開かない

**原因：** ウィンドウサイズ・座標ずれ  
**対処：** `find` ツールで `ファイルをダウンロード` のaria-labelやテキストを検索してrefを取得しクリック

### エラー3：ダウンロードしたPDFがAcrobatで自動開く

**対処：** Acrobatを閉じてから `cp` コマンドで移動する

### エラー4：プロパティが一覧に見つからない

**対処：** プロパティセレクターパネルの検索ボックスに顧客名を直接入力

### エラー5：ファイルアップロードが「Not allowed」

**対処：** Ghostscriptをローカルで実行してPDF変換・リサイズを行う（外部サービス使用不可）

### エラー6：レポート画面ではなく管理画面（歯車）が開く

**対処：** 左サイドバーのレポートアイコン（棒グラフ ≡）をクリック

### エラー7：パス自動検出に失敗する

**対処：** ユーザーに以下を確認する
- WindowsのユーザーフォルダがCドライブ以外にあるか
- セッションIDの構造が変わっていないか
- `ls /sessions/` の出力結果を共有してもらい、手動でパスを特定する

---

## Looker Studioレポートの場合

一部顧客はLooker Studioでレポートが作成されている。

ダウンロード手順：
1. 画面右上の「共有」ボタンをクリック（ドロップダウンが開く）
2. 「レポートをダウンロード」を選択
3. PDF形式でダウンロード

> ⚠️ ケバブメニュー（⋮）からではなく、「共有」ドロップダウンから行うこと

---

## プロジェクト設定情報

| 項目 | 値 |
|---|---|
| Googleアカウント | seo@a-manage.jp |
| GA4プロパティベースURL | `https://analytics.google.com/analytics/web/?authuser=0` |
| Chatwork送信先 | 谷口 弘哉（#!rid373763856） |
| ダウンロード先（Windows） | `C:\Users\{WIN_USER}\Downloads`（作業開始時に自動検出） |
| ダウンロード先（Claude） | `${DOWNLOADS_PATH}`（作業開始時に自動検出） |
| 作業フォルダ（Claude） | `${WORK_BASE}`（作業開始時に自動検出） |
| 進捗メモファイル | `アクセス解析進捗メモ.txt`（作業フォルダ直下） |