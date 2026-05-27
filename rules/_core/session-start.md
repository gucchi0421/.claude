# セッション管理

## コンテキスト管理

- 作業完了後は `/clear` を促すこと
- 長いセッション（50メッセージ超）では `/compact` を提案すること

## セッション開始時

1. auto memory を確認して前回の作業コンテキストを把握する
2. プロジェクトの CLAUDE.md があれば参照する
3. プロジェクトの `.claude/logs/summary/` に当日または直近のサマリーファイルがあれば読んで前回の作業を把握する
4. Serena MCP が有効か確認する → 使えなければインストールを提案する（手順は `rules/_core/token-efficiency.md` 参照）
5. コーディングタスクがある場合は `mcp__serena__initial_instructions` を呼んでから着手する

## ファイル編集の大前提

**`~/.claude/` 配下のファイルを編集する場合、必ず `/home/k-taniguchi/documents/dotfiles/packages/claude/.claude/` で作業すること。**
`~/.claude/` は dotfiles リポジトリへのシンボリックリンクであり、直接編集するとリポジトリ管理外になる。
プログラム内の参照・実行パスは `~/.claude/` のまま使用してよい。

## セルフ修正ルール

ユーザーから行動を修正された場合、以下の手順を必ず実行する：

1. `~/documents/dotfiles/packages/claude/.claude/rules/` の該当ファイルを更新する
2. 該当ファイルがなければ新規作成する
3. 更新後、~/documents/dotfiles/packages/claude/.claudeディレクトリのリポジトリで `git commit` → `git push` まで実行する

これにより同じミスの繰り返しを防ぎ、Claude を「育てる」感覚で設定を積み上げていく

## セッション終了時（自動）

Stop hook により `~/.claude/scripts/session_review.sh` が自動実行され、セッションログを Gemini で分析してルール改善提案を `~/documents/dotfiles/packages/claude/.claude/settions/pending_proposals.json` に保存する。

## セッション開始時の提案チェック

1. `~/.claude/logs/pending_proposals.json` が存在するか確認する
2. 存在する場合、中身を読んでユーザーに提案内容を伝える
3. ユーザーが承認したら `rules/` の該当ファイルを直接編集して git commit → git push する
4. 適用後は `pending_proposals.json` を削除する
5. 拒否された場合もファイルを削除する
