#!/bin/bash
# 引数1: rewrite（下書きリライト）/ new-article（新規記事）/ seo（SEO改善）/ pdca（構造改善）/ patrol（記事パトロール・自動修正）/ link（内部リンク巡回）
# 引数2: PROJECT_DIR（プロジェクトの絶対パス）
TASK="${1:-rewrite}"
PROJECT_DIR="${2:?PROJECT_DIR が指定されていません。例: bash run-seo-agent.sh rewrite /home/k-taniguchi/documents/claude/e-webseisaku.com}"

TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
export SCHEDULE_LOG_FILE="$PROJECT_DIR/.claude/logs/schedule/${TIMESTAMP}_${TASK}.md"

mkdir -p "$(dirname "$SCHEDULE_LOG_FILE")"
cd "$PROJECT_DIR"

# タスクログのヘッダーを作成
cat >> "$SCHEDULE_LOG_FILE" <<EOF
# $(date '+%Y-%m-%d %H:%M:%S') — ${TASK}

EOF

echo "=== $(date '+%Y-%m-%d %H:%M:%S') 開始 [task: $TASK] ===" >> "$SCHEDULE_LOG_FILE"

case "$TASK" in
  rewrite)
    PROMPT="下書き記事を1本リライトして公開してほしいのだ。.claude/logs/schedule/index.mdを読んで前回の引き継ぎを確認してから進めてほしいのだ。【役割分担】記事の執筆・リライトは必ずwriterエージェントが担当する。wp-operatorはWP投稿のみ担当し、記事本文を自分で書かない。writerエージェントには必ず ARTICLES_DIR=${PROJECT_DIR}/.claude/articles を渡すこと。完了後は/schedule-agent-summaryでログを残してほしいのだ。"
    ;;
  new-article)
    PROMPT="GSCデータを分析して完全新規の記事を1本執筆・公開してほしいのだ。既存の下書きや投稿を流用・更新するのは禁止なのだ。必ず新しい投稿IDで wp post create から始めること。.claude/logs/schedule/index.mdを読んで前回の引き継ぎを確認してから進めてほしいのだ。【役割分担】記事の執筆はwriterエージェントが担当する。wp-operatorはWP投稿のみ担当し、記事本文を自分で書かない。writerエージェントには必ず ARTICLES_DIR=${PROJECT_DIR}/.claude/articles を渡すこと。完了後は/schedule-agent-summaryでログを残してほしいのだ。"
    ;;
  seo)
    PROMPT="GSCクイックウィン分析してタイトル・ディスクリプション・AIOSEOを改善してほしいのだ。サイトのグローバル設定、記事ごとのAIOSEO設定も範囲内なのだ。.claude/logs/schedule/index.mdを読んで前回の引き継ぎを確認してから進めてほしいのだ。完了後は/schedule-agent-summaryでログを残してほしいのだ。"
    ;;
  pdca)
    PROMPT="GSC・GA4データを分析して、流入改善につながるサイト構造・導線の修正を1件実施してほしい。対象はSSH接続先(ssh webchecker5)のWordPressテストサイト。.claude/logs/schedule/index.mdを読んで前回の引き継ぎを確認してから進めること。分析→仮説→実施の流れで根拠のある修正をすること。【重要】タイトル・AIOSEOのメタ情報変更はseoタスクが担当するため禁止。このタスクはPHP/CSS/テンプレートレベルの構造改善に集中すること。修正例：表示回数が多くCTRが低い記事をサイドバーや一覧上部に露出する／滞在時間が長いのに内部リンクが少ない記事にリンクカードを追加する／流入はあるがCTAが弱い記事の導線強化／ウィジェット・サイドバー構成の改善／など。テーマファイル(PHP/CSS)の直接編集もOK。必ずバックアップ(.bak)を取ってから編集すること。完了後は/schedule-agent-summaryでログを残すこと。"
    ;;
  patrol)
    PROMPT="公開済み記事のパトロール・自動修正を実施してほしいのだ。article-patrolerエージェントを使って以下を実行すること。PROJECT_DIR=${PROJECT_DIR} を渡すこと。【パトロール内容】1) article-index.json（${PROJECT_DIR}/.claude/data/article-index.json）を読み込み、patrolled_at が null または最も古い記事から最大15件をバッチ処理する。2) 各記事についてSSH経由でWP-CLIを使い本文HTMLを取得し、以下をチェック・自動修正する：壊れた内部リンク（インデックスに存在しないURL）の削除、article-link-card__title のテキストとインデックスのタイトルの不一致修正、フルHTML（DOCTYPE/html/head/body）混入の修正、インデックスのtitle/slugとWP実データの乖離修正。3) 修正後はWP-CLIで記事を更新し、article-index.json の patrolled_at と patrol_issues を更新する。完了後は/schedule-agent-summaryでログを残してほしいのだ。"
    ;;
  link)
    PROMPT="公開済み記事の内部リンクを巡回追加してほしいのだ。article-linkerエージェントを使って以下を実行すること。PROJECT_DIR=${PROJECT_DIR} を渡すこと。【処理内容】1) article-index.json（${PROJECT_DIR}/.claude/data/article-index.json）を読み込み、last_linked が null または最も古い記事から最大10件をバッチ処理する。2) 各記事について関連記事を最大3件選定し、link-card形式でH2セクション末尾に追加する。3) 関連記事側にも逆方向リンクを追加する（双方向リンク）。4) article-index.json の existing_internal_links と last_linked を更新する。完了後は/schedule-agent-summaryでログを残してほしいのだ。"
    ;;
esac

PID_FILE="$PROJECT_DIR/.claude/logs/schedule/${TASK}.pid"
echo $$ > "$PID_FILE"

# 60秒ごとにハートビートをログに記録（バックグラウンド）
(
  while kill -0 $$ 2>/dev/null; do
    sleep 60
    kill -0 $$ 2>/dev/null && echo "  [$(date '+%H:%M:%S')] 処理中..." >> "$SCHEDULE_LOG_FILE"
  done
) &
HEARTBEAT_PID=$!

/home/k-taniguchi/.local/bin/claude --dangerously-skip-permissions --permission-mode bypassPermissions -p "$PROMPT" >> "$SCHEDULE_LOG_FILE" 2>&1

kill "$HEARTBEAT_PID" 2>/dev/null
rm -f "$PID_FILE"
echo "=== $(date '+%Y-%m-%d %H:%M:%S') 終了 ===" >> "$SCHEDULE_LOG_FILE"
