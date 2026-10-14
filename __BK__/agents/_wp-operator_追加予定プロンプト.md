# wp-operator 追加予定プロンプト

## サイトマップping送信（記事公開後）

本番サイト移行後に `wp-operator.md` の「記事投稿時の必須手順」に追加する。

```markdown
### 5. サイトマップping送信

記事公開後に必ず実行する。`.claude/settings.seo.json` の `sitemap_url` を使う。存在しない場合は `gsc_site_url + "sitemap.xml"` を使う。

```bash
curl -s "https://www.google.com/ping?sitemap={sitemap_url}"
```
```

## 追加タイミング

- テストサイト（e-webseisaku.com.web-checker5.net）から本番（www.e-webseisaku.com）に移行したとき
