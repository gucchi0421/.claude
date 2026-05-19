# references/aioseo.md

AIOSEO に関する操作・確認事項をまとめる。
audit・execute の両フェーズで参照する。

---

## 1. General Settings（サイト全体設定）

WP管理画面 → All in One SEO → General Settings

### 確認・調整ポイント

| 設定項目 | 場所 | 確認内容 | 推奨値 |
|---------|------|---------|--------|
| JSON-LD 構造化データ | General Settings → Webmaster Tools | 有効になっているか | ON |
| Open Graph | Social Networks → Facebook | OGP が有効か | ON |
| Twitter Card | Social Networks → Twitter | Summary with Large Image | ON |
| Breadcrumbs | General Settings → Breadcrumbs | 有効か / JSON-LD か | JSON-LD ON |
| Robots.txt | Tools → Robots.txt Editor | 不要なURL（/wp-admin等）が noindex になっているか | 確認のみ |
| Sitemap | Sitemaps → XML Sitemap | 有効か / 投稿・固定ページが含まれるか | ON |
| Search Appearance（グローバルテンプレート） | Search Appearance → Global Settings | タイトルのフォーマット（`%post_title% %separator% %site_title%`） | 確認 |

---

## 2. 記事ごとのAIOSEOスコア確認

### スコアの構成（AIOSEOが見ている項目）

AIOSEOスコアは以下の項目で構成される。各記事の編集画面下部のAIOSEOブロックで確認。

#### Basic SEO（基本SEO）
| チェック項目 | 合格条件 | よくある問題 |
|------------|---------|------------|
| Focus Keyword in Title | タイトルに含む | KWが後ろすぎる → 前半に移動 |
| Focus Keyword in Meta Description | ディスクリプションに含む | 含まれていない |
| Focus Keyword in Content | 本文に適切な密度（1〜3%） | 出現回数が多すぎor少なすぎ |
| Focus Keyword in Introduction | 最初の段落に含む | 冒頭に対策KWなし |
| Focus Keyword in Subheading | H2/H3に含む | 見出しに対策KW未使用 |
| Focus Keyword in Image Alt | 画像のalt属性に含む | altが空 or KW未使用 |
| Meta Description Length | 120〜160文字 | 短すぎor長すぎ |
| Title Length | 50〜60文字（表示上32文字以内が望ましい） | 長すぎ |
| Content Length | 300文字以上（実際は1500文字以上推奨） | 文字数不足 |
| Internal Links | 記事内に内部リンクあり | 内部リンクがゼロ |
| Outbound Links | 外部リンクあり | 外部リンクがゼロ |

#### Readability（読みやすさ）
| チェック項目 | 合格条件 |
|------------|---------|
| Paragraph Length | 1段落が長すぎない（150文字程度が目安） |
| Subheadings Distribution | 300文字ごとに見出し1つ程度 |
| Images in Content | 本文中に画像あり |
| Passive Voice | 受動態の使用が10%未満（日本語では参考程度） |
| Transition Words | 繋ぎ言葉（しかし、つまり等）の使用 |

---

## 3. 記事ごとの設定手順（編集画面）

WP管理画面 → 投稿一覧 → 対象記事を編集 → 下部のAIOSEOブロック

### General タブ

```
Focus Keyword    : [対策KW を入力]（例: ホームページ制作 大阪）
Post Title       : [タイトル案を入力] ← 32文字以内を厳守
Meta Description : [ディスクリプション案を入力] ← 120文字前後
```

**タイトルのコツ:**
- 対策KWを先頭に近い位置に配置
- 数字・地域名・ベネフィットを含めるとCTR向上
- 例: `ホームページ制作 大阪｜費用・期間・選び方を解説【実績多数】`

**ディスクリプションのコツ:**
- 対策KWを前半に含める
- ユーザーが得られるものを明示（「〜がわかります」「〜できます」）
- CTA的な文言で締める（「まずはお気軽にご相談ください」など）

### Schema タブ

```
Schema Type を設定:
- 記事（解説系）    → Article
- FAQ記事          → FAQPage または Article + FAQ Block
- サービスページ   → Service
- 会社概要ページ   → Organization + LocalBusiness
```

FAQPageスキーマの追加手順:
1. Schema タブ → Add Schema → FAQPage を選択
2. Q&Aを1件ずつ入力（plan.md で生成済みのQ&Aをそのまま入力）
3. Save

### Social タブ

```
OG Title       : タイトルと同じかSNS向けに調整
OG Description : ディスクリプションと同じかSNS向けに調整
OG Image       : アイキャッチ画像が設定されていればそのまま
```

---

## 4. スコア別の対応方針

| スコア帯 | 優先度 | 対応 |
|---------|--------|------|
| 70点以上 | 低 | 基本的に放置可。フォーカスKWと更新日だけ確認 |
| 50〜69点 | 中 | タイトル・ディスクリプション修正 + 本文に対策KWを追加 |
| 50点未満 | 高 | フルリライト対象。競合調査→plan→executeを実施 |

---

## 5. 投稿一覧でのスコア一括確認

WP管理画面 → 投稿 → 投稿一覧

- 列表示に「SEO Score（AIOSEOカラム）」が表示される
- スコアカラムをクリックでソート可能
- スコアが赤（低）の記事を優先的に抽出する

抽出基準:
- 🔴 赤（〜49点）: 要対応
- 🟡 黄（50〜69点）: 機会があれば対応
- 🟢 緑（70点〜）: 放置可

---

## 6. Local SEO 設定（LocalBusinessスキーマ）

WP管理画面 → All in One SEO → Local SEO

```
Business Name    : 株式会社e-webseisaku（または正式社名）
Business Type    : ProfessionalService
Phone            : 電話番号
Address          : 住所
Opening Hours    : 営業時間
```

→ これを設定するとトップページに LocalBusiness スキーマが自動付与される。
Googleマップとの連携・MAP表示にも影響するため要設定確認。

---

## 7. よくある修正パターン（コピペ用テンプレ）

### Focus Keywordが入っていない場合
→ 対策KWをそのまま入力（「ホームページ制作 大阪」）

### タイトルが長すぎる場合
→ 助詞・接続詞を削る。「について」「することができます」を省略。
→ `【完全解説】` 等の装飾を外す。

### ディスクリプションにKWがない場合
→ 冒頭に「[KW]をお考えの方へ。」を追加。

### 内部リンクがゼロの場合
→ 本文内の関連キーワードにリンクを貼る（同サイト内記事へ）。
→ アンカーテキストには対策KWを含める。

---

## 8. 固定ページの最適化

WP管理画面 → 固定ページ一覧 → 対象ページを編集 → 下部のAIOSEOブロック

投稿記事と設定手順は同じだが、以下の点が異なる。

### 優先して設定するページ

| ページ | Focus Keyword | Schema Type | 備考 |
|--------|--------------|-------------|------|
| トップページ | ホームページ制作 大阪 | Organization + LocalBusiness | 最重要。必ず設定する |
| サービスページ | ホームページ制作 大阪 費用 など | Service | 各サービスごとに個別KWを設定 |
| 会社概要 | 会社名 / ブランド名 | Organization | KWよりブランド認知を優先 |
| 料金ページ | ホームページ制作 料金 | Service | 価格情報をスキーマに含める |
| お問い合わせ | なし | ContactPage | KW不要。インデックス確認のみ |

### トップページのAIOSEO設定手順

1. 固定ページ一覧でトップページ（フロントページ）を開く
2. AIOSEOブロック → General タブ
   - Focus Keyword: `ホームページ制作 大阪`
   - Post Title: 対策KWを前半に配置（32文字以内）
   - Meta Description: 対策KW含む120文字前後
3. Schema タブ → Organization を選択
   - Name: 正式社名
   - URL: サイトURL
   - Logo: ロゴ画像URL
4. Social タブ → OG Image にトップのアイキャッチを設定

### Search Appearance での固定ページ一括設定

WP管理画面 → All in One SEO → Search Appearance → Pages タブ

- 固定ページのタイトルフォーマットをここで一括設定できる
- デフォルトテンプレート: `%post_title% %separator% %site_title%`
- 個別ページの設定が優先されるため、重要ページは個別設定を入れる

---

## 9. Search Statistics（GSC連携）

WP管理画面 → All in One SEO → Search Statistics

GSCと連携することでAIOSEO内から直接順位・クリック数を確認できる。

### 初期連携手順（未連携の場合）

1. Search Statistics を開く
2. 「Connect to Google Search Console」をクリック
3. Googleアカウントでログイン → サイトのプロパティを選択
4. 連携完了後、データが反映されるまで数時間〜1日待つ

### 確認すべき指標

| タブ | 確認項目 | 判断基準 |
|------|---------|---------|
| Overview | クリック数・表示回数・CTR・平均掲載順位 | 前月比でCTRが下がっていたらタイトル改善 |
| Keywords | KWごとの順位・クリック | 4〜10位のKWは上位化しやすいため優先対応 |
| Content Rankings | 記事ごとの順位 | 順位が下落している記事をリライト対象に |
| Keyword Trends | KWの順位推移グラフ | 急落していたらコンテンツ鮮度・競合調査 |

### 活用方法

- 4〜10位のKW（チャンスKW）を抽出 → plan.md でタイトル・本文の改善に活用
- CTRが低い（表示回数は多いがクリックされない）記事 → タイトル・ディスクリプションを修正
- 圏外（11位以下）で検索ボリュームがあるKW → 競合調査→リライト対象

---

## 10. Link Assistant（内部リンク自動提案）

WP管理画面 → All in One SEO → Link Assistant

AIOSEOがサイト内の記事を分析し、内部リンクを追加すべき箇所を自動提案する。

### 確認手順

1. Link Assistant を開く
2. 「Links Report」タブ → 各記事の内部リンク数を一覧確認
   - 内部リンクが0の記事は優先対応
3. 「Suggestions」タブ → AIOSEOが提案するリンク先・アンカーテキストを確認

### 内部リンク追加手順（Suggestions から）

1. Suggestions タブで対象記事を選択
2. 提案されたリンク先とアンカーテキストを確認
3. 「Add Link」をクリック → 自動でリンクが挿入される
4. 挿入後は記事を開いて文脈上不自然でないか確認してから保存

### 判断基準

| 状態 | 対応 |
|------|------|
| 内部リンク 0本 | 最優先。Suggestionsから2〜3本追加 |
| 内部リンク 1〜2本 | 機会があれば追加 |
| 内部リンク 3本以上 | 基本的に放置可 |

### 孤立ページ（Orphan Pages）の確認

Link Assistant → Orphan Pages タブ

- どこからもリンクされていないページが一覧表示される
- 孤立ページはGoogleにクロールされにくいため、親ページ等からリンクを追加する

---

## 11. Redirects（404エラー・リダイレクト管理）

WP管理画面 → All in One SEO → Redirects

### 404エラーの確認

1. Redirects → 「404 Logs」タブ
2. アクセスされているが存在しないURLの一覧を確認
3. 正しいURLへのリダイレクトを設定する

### リダイレクトの追加手順

1. Redirects → 「Add Redirect」ボタン
2. 設定項目:
   - Source URL: リダイレクト元のURL（例: `/old-page/`）
   - Target URL: リダイレクト先のURL（例: `/new-page/`）
   - Redirect Type: `301 Permanent`（恒久移転の場合）
3. 「Add Redirect」で保存

### リダイレクトタイプの選択基準

| タイプ | 用途 |
|--------|------|
| 301 Permanent | ページ移転・URL変更・旧コンテンツ廃止 |
| 302 Temporary | 一時的な転送（イベントページなど） |
| 410 Gone | 完全削除してリダイレクト先もない場合 |

### 定期確認のタイミング

- audit フェーズで毎回 404 Logs を確認する
- 404が10件以上蓄積していたら一括対処する

---

## 12. SEO Audit Checklist

WP管理画面 → All in One SEO → SEO Analysis → SEO Audit Checklist

AIOSEOがサイト全体をスキャンして問題点を自動検出する。

### 確認手順

1. SEO Analysis → SEO Audit Checklist を開く
2. 「Run Site Audit」をクリック（初回または再スキャン時）
3. 結果をカテゴリ別に確認

### カテゴリと確認ポイント

| カテゴリ | 主な確認項目 |
|---------|------------|
| Critical Issues | noindexの誤設定・サイトマップ未生成・robots.txtブロック |
| Warnings | titleタグ重複・ディスクリプション未設定・alt属性なし画像 |
| Recommended Improvements | 内部リンク不足・本文が短いページ |
| Good Results | 問題なし（参考として確認） |

### 対応優先順位

1. Critical Issues → 即対応（インデックスに直接影響）
2. Warnings で複数ページに共通する問題 → 一括対処
3. Recommended Improvements → plan.md に盛り込む

---

## 13. Advanced Settings（noindex・canonical等）

記事・固定ページ編集画面 → AIOSEOブロック → Advanced タブ

### 主な設定項目

| 設定項目 | 用途 | 推奨 |
|---------|------|------|
| Robots Meta: noindex | 検索結果から除外 | 基本はOFF。タグ・著者アーカイブ等にのみON |
| Robots Meta: nofollow | リンクをフォローさせない | 基本はOFF |
| Canonical URL | 正規URLを明示 | 重複コンテンツがある場合のみ設定 |
| Breadcrumbs Custom Label | パンくずの表示名を変更 | 必要に応じて |

### サイト全体のnoindex設定確認

WP管理画面 → All in One SEO → Search Appearance → Content Types

- 投稿・固定ページ以外（タグ・カテゴリ・著者ページ等）が意図せずインデックスされていないか確認
- 不要なアーカイブページは noindex にしてクロールバジェットを節約する

### canonicalの確認が必要なケース

- URLに `?` パラメータが付くページ（フォーム送信後など）
- ページネーション（`/page/2/` など）
- 同一コンテンツが複数URLで表示される場合

→ 該当する場合はcanonicalをAIOSEOのAdvancedタブで設定し、正規URLに統一する

---

## 14. AIO（AI Overview）対策

Googleの検索結果上部に表示されるAI生成の要約枠。ここに引用されるとクリックされなくても認知が上がり、引用元として表示されればブランド信頼度・CTRが向上する。

### AIO引用のされやすい条件

| 条件 | 対応 |
|------|------|
| 質問形式のコンテンツ | FAQPage スキーマ + Q&A本文を充実させる |
| 明確な定義文がある | 「〇〇とは〜です」という一文を冒頭に入れる |
| 箇条書きで要点が整理されている | H2/H3配下に箇条書きで要点をまとめる |
| 権威性・信頼性がある（E-E-A-T） | 実績・事例・会社情報を本文に含める |
| 簡潔な回答が本文中にある | 検索意図の答えを最初の200文字以内に書く |

### コンテンツ改善手順（AIO引用を狙う場合）

1. 対策KWで検索してAIOの文章を確認する
2. AIOが引用しているサイトの記事構成を分析する
3. 自サイトの該当ページに以下を追加・修正する:
   - 冒頭200文字以内に「〇〇とは〜」の定義文
   - FAQセクション（Q&A形式）を本文後半に追加
   - 箇条書きで「〜の3つのポイント」などを整理
4. AIOSEOの Schema タブで `FAQPage` スキーマを追加する（§3 参照）

### 監視方法

- auditフェーズで毎回対策KW3つを検索してAIO表示の有無と引用状況を確認する（audit.md § 7 参照）
- 自サイトが引用されたら引用箇所のテキストを記録し、そのコンテンツを維持・強化する
- 引用が消えたらコンテンツの鮮度・構造を見直す
