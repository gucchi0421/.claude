# Git ワークフロー

## コミット形式

Conventional Commits 形式を使う。

```
<type>(<scope>): <summary>

<body（日本語で "なぜ" を説明）>
```

**type**: `feat` / `fix` / `docs` / `style` / `refactor` / `test` / `chore` / `ci`

- summary は英語（動詞原形で始める）
- body は日本語。何をしたかでなく、なぜしたかを書く

## 禁止事項

- `git push --force` / `git push -f` → 絶対禁止
- `git reset --hard` → ユーザー確認後のみ
- `--no-verify` → 禁止（hook をスキップしない）
- 自動コミット・自動 push → 確認なしに実行しない
- main / master への直接 push → 禁止

## ブランチ命名

`feat/` / `fix/` / `chore/` / `refactor/` + 内容を kebab-case で。

例: `feat/add-contact-form`, `fix/mobile-nav-overflow`
