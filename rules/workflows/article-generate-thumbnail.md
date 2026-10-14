# アイキャッチ画像設定ルール（v2）

## 現在の方針：手動設定

アイキャッチ画像は **CEOが WordPress 下書き上で手動設定** する。

Chatworkに届く承認依頼メッセージに「アイキャッチ画像を設定してください」と記載されている。
CEOが下書きを確認する際に画像を設定し、その後ステータスを「予約投稿」に変更することで承認完了となる。

**将来的に Adobe Stock API / SVG自動生成に差し替え予定。**
`article-pipeline.js` の画像phaseに差し替えポイントのプレースホルダーが用意されている。

---

## 将来の自動化計画

### 第一候補：フラットベクターSVG生成

記事内容に合わせたフラットベクター（SVG）イラストを1案生成する。
既存のサイトデザイン方針（AIっぽさを回避）に合致する。

差し替えポイント：`article-pipeline.js` の以下のコメント箇所

```js
// ── TODO: Adobe Stock API差し替えポイント ──
// image_mode === "adobe_stock" の場合の実装はここに追加する
```

### 第二候補：Adobe Stock API

候補3枚を抽出してWordPress下書きに添付し、CEOが選定する。

- Adobe Developer Console での登録・API利用申請が必要
- settings.seo.json の `image_mode: "adobe_stock"` で切り替える

---

## 補助ツール（手動でローカル生成したい場合）

以前から使っていた Pollinations.ai スクリプトは、
手動でローカル生成したい場合の補助ツールとして引き続き使用できる。

```bash
python3 ~/.claude/scripts/article_generate_thumbnail.py \
  --title "記事タイトル" \
  --slug {slug} \
  --scene "（英語シーン描写・50語以上）" \
  --style ghibli
```

保存先は自動的に `$(pwd)/.claude/articles/{slug}.jpg` になる。
生成後は WordPress メディアライブラリに手動でアップロードして設定する。

スクリプトの詳細は `__BK__/scripts/article_generate_thumbnail.py` を参照。
