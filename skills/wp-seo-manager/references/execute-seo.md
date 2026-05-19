# execute-seo.md（SEOエンジニア担当）

**前提: ディレクターからバックアップ完了の連絡を受けてから着手する。**

plan.md で生成済みのコンテンツをそのまま投入する。この段階で新たに考えない。

---

## 1. AIOSEOメタ情報の更新

→ aioseo.md § 3（General タブ）の手順で操作する。

ブラウザ → WP管理画面 → 対象記事/ページの編集画面 → AIOSEOブロック → General タブ:

```
Focus Keyword    : plan.md のKWをそのまま入力
Post Title       : plan.md のタイトル案をそのまま入力（32文字以内）
Meta Description : plan.md のディスクリプション案をそのまま入力（120文字前後）
```

入力後、AIOSEOスコアのチェック項目が変化するのを確認する。
→ aioseo.md § 2 のチェック項目を参照して残っている ✗ 項目を確認・対処。

変更記録（context.mdに残す）:
```
[記事名/ページ名]
タイトル: 「変更前」→「変更後」（XX文字）
ディスクリプション: 「変更前」→「変更後」
スコア: XX点 → [更新後に確認]
```

---

## 2. AIOSEO General Settings の調整

auditで要確認が出た場合のみ実施。→ aioseo.md § 1 を参照。

優先して対処:
- Local SEO（LocalBusiness）の設定
- OGP / Twitter Card の有効化
- Sitemapに投稿・固定ページが含まれているか

---

## 3. スキーマ（JSON-LD）の追加

plan.md で指定されたスキーマをAIOSEOで追加する。

**FAQPage スキーマ:**
→ aioseo.md § 3（Schema タブ）の手順で操作。
- 対象記事の編集画面 → AIOSEOブロック → Schema タブ → Add Schema → FAQPage
- plan.md のQ&Aをそのまま入力

**LocalBusiness スキーマ（トップページ）:**
→ aioseo.md § 6（Local SEO設定）の手順で操作。
- AIOSEO → Local SEO → 各項目を入力

**functions.phpへの直接埋め込みが必要な場合:**
→ コーダーに作業を渡す（自分では実施しない）

変更記録:
```
追加スキーマ: [種別]
追加場所: [記事名/ページ名]
方法: AIOSEO管理 / コーダーへ依頼
```

---

## 4. 内部リンクの追加

→ aioseo.md § 10（Link Assistant）を活用する。

1. Link Assistant → Suggestions タブで提案を確認
2. plan.md で指定した内部リンクと照合
3. 「Add Link」で挿入 → 文脈上不自然でないか確認してから保存

手動で追加する場合:
- 対象記事の編集画面で指定箇所にアンカーテキスト付きリンクを挿入
- アンカーテキストは対策KWを含める

変更記録:
```
内部リンク追加: [追加先記事] → [リンク先URL]（アンカー: [テキスト]）
```

---

## 完了後

context.mdに変更記録をすべて記載してディレクターに渡す。
