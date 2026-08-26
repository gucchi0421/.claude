#!/bin/bash
# 引数1: rewrite（下書きリライト）/ new-article（新規記事）/ seo（SEO改善）/ pdca（構造改善）/ patrol（記事パトロール・自動修正）/ link（内部リンク巡回）
# 引数2: PROJECT_DIR（プロジェクトの絶対パス）
TASK="${1:-rewrite}"
PROJECT_DIR="${2:?PROJECT_DIR が指定されていません。例: bash run_seo_agent.sh rewrite /home/k-taniguchi/documents/claude/e-webseisaku.com}"

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
    PROMPT="既存記事を1本選んでリライトし、同じIDに上書き公開してほしいのだ。.claude/logs/schedule/index.mdを読んで前回の引き継ぎを確認してから進めてほしいのだ。【リライト対象の選び方】以下のいずれかから優先度の高い1本を選ぶこと。①下書き（draft）状態の古いコラム記事（wp post list --post_type=column --post_status=draft）②公開中（publish）だが投稿日が古い記事・または内容のアップデートが激しいテーマ（Web制作トレンド・SEO・AI・法律・料金相場など）は数か月でも対象になる（wp post list --post_type=column --post_status=publish --orderby=date --order=ASC）。【絶対ルール】リライト後は必ず元の記事ID（EXISTING_POST_ID）に wp post update で上書きすること。wp post create で新規投稿するのは絶対に禁止。URLが変わると被リンク・検索順位がゼロリセットされる。wp-operatorに渡すときは EXISTING_POST_ID={対象のWP投稿ID} を必ず明示すること。また元記事の投稿日（post_date）が5年以上前の場合は、wp post update で本文を更新するときに --post_date=\"先月のランダムな日付（YYYY-MM-DD HH:MM:SS形式）\" も合わせて指定して投稿日を更新すること。日付は先月1日〜末日の範囲でランダムに散らすこと。【役割分担】記事の執筆・リライトは必ずwriterエージェントが担当する。wp-operatorはWP投稿のみ担当し、記事本文を自分で書かない。writerエージェントには必ず ARTICLES_DIR=${PROJECT_DIR}/.claude/articles を渡すこと。完了後は/schedule-agent-summaryでログを残してほしいのだ。"
    ;;
  new-article)
    PROMPT="GSCデータとGA4データを分析して完全新規の記事を1本執筆・公開してほしいのだ。既存の下書きや投稿を流用・更新するのは禁止なのだ。必ず新しい投稿IDで wp post create から始めること。.claude/logs/schedule/index.mdを読んで前回の引き継ぎを確認してから進めてほしいのだ。

【重複チェック（必須・最優先）】キーワードを選定する前に、必ず ${PROJECT_DIR}/.claude/data/article-index.json を読み込んで既存記事の全タイトルとkeywordsを把握すること。このJSONがサイトの正の記事一覧であり、GSC・GA4に反映されていない最新の新規記事も含まれている。以下の条件に該当するキーワードは選定禁止：
①選定しようとしているメインキーワード（例：「ホームページ制作 大阪 費用」）が既存記事のkeywordsフィールドに含まれている
②選定しようとしている記事のタイトルと既存記事のタイトルが主題レベルで被っている
重複が疑われる場合は必ずキーワードを変えて再選定すること。article-index.json に存在しないテーマ・切り口・ロングテールを選ぶこと。

【役割分担】記事の執筆はwriterエージェントが担当する。wp-operatorはWP投稿のみ担当し、記事本文を自分で書かない。writerエージェントには必ず ARTICLES_DIR=${PROJECT_DIR}/.claude/articles を渡すこと。完了後は/schedule-agent-summaryでログを残してほしいのだ。"
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

printf '%s' "$PROMPT" | /home/k-taniguchi/.local/bin/claude --dangerously-skip-permissions --permission-mode bypassPermissions -p >> "$SCHEDULE_LOG_FILE" 2>&1

kill "$HEARTBEAT_PID" 2>/dev/null
rm -f "$PID_FILE"
echo "=== $(date '+%Y-%m-%d %H:%M:%S') 終了 ===" >> "$SCHEDULE_LOG_FILE"
