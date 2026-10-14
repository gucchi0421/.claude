export const meta = {
  name: 'article-pipeline',
  description: '記事自動生成グラフ: 競合調査・執筆・レビュー・WP投稿を自律実行',
  phases: [
    { title: 'データ収集',   detail: 'SEO分析 + 競合調査を並列実行' },
    { title: '執筆指示書',   detail: 'seo-analyst がキーワードと指示書を作成' },
    { title: '執筆',         detail: 'writer が記事を執筆して .md を保存' },
    { title: 'レビューゲート', detail: 'article_review.sh で評価 → pass/revise/stop を判定' },
    { title: 'WP投稿',       detail: 'MD→HTML変換 → wp-operator が投稿' },
    { title: '通知',         detail: 'Chatwork 完了通知 + SEOログ記録' },
  ],
}

// ──────────────────────────────────────────
// 型付き状態（グラフ全体で共有する実行状態）
// ──────────────────────────────────────────
// args は article-loop スキルから渡される
// { project_dir, seo_config: <settings.seo.json の内容>, gsc_data, ga4_data }
//
// settings.seo.json の構造:
// {
//   "env": "staging" | "production",   ← このフラグで環境を切り替える
//   "production": { site_url, site_name, wp_post_status },
//   "staging":    { site_url, site_name, wp_post_status },
//   "articles_dir", "max_review_retry", "target_keywords", "notify_chatwork"
// }
const cfg    = args?.seo_config || {}
const env    = cfg.env || 'staging'          // デフォルトはステージング（安全側）
const envCfg = cfg[env] || {}

const isStaging = env === 'staging'

const state = {
  env,
  isStaging,
  projectDir:   args?.project_dir      || '.',
  siteUrl:      envCfg.site_url        || '',
  siteName:     envCfg.site_name       || '',
  wpStatus:     envCfg.wp_post_status  || 'draft',
  articlesDir:  cfg.articles_dir       || `${args?.project_dir || '.'}/.claude/articles`,
  maxRetry:     cfg.max_review_retry   || 3,
  notifyCw:     cfg.notify_chatwork    !== false,
  keywords:     cfg.target_keywords    || [],
  // テストモード時の注意:
  // GSC/GA4 データは本番サイトのものであり、ステージングの投稿結果と紐づかない。
  // キーワード選定・競合分析の参考にはなるが、投稿後の効果測定には使えない。
  gscData:      args?.gsc_data         || null,
  ga4Data:      args?.ga4_data         || null,
  // 実行中に更新されるフィールド
  brief:        null,   // seo-analyst が作成した執筆指示書
  attempt:      0,      // 執筆→レビューの試行回数
  feedback:     '',     // reviewer からの差し戻しフィードバック
  reviewResult: null,   // 最新のレビュー結果 JSON
  wpResult:     null,   // WP投稿結果
}

// ──────────────────────────────────────────
// Conditional edge: レビュー結果を3方向に分岐
// ──────────────────────────────────────────
// → "pass"  : WP投稿へ進む
// → "revise": writerへ差し戻し（attempt < maxRetry）
// → "stop"  : 上限超過 → Chatwork通知して終了
function chooseNext(reviewResult, attempt, maxRetry) {
  if (reviewResult?.pass)       return 'pass'
  if (attempt >= maxRetry)      return 'stop'
  return 'revise'
}

// ──────────────────────────────────────────
// Node: データ収集（並列）
// ──────────────────────────────────────────
phase('データ収集')
log(`[${state.env.toUpperCase()}] 対象サイト: ${state.siteUrl} | 記事保存先: ${state.articlesDir}`)

if (state.isStaging) {
  log('⚠️  STAGING MODE: GSC/GA4 データは本番サイト（production）のものです。')
  log('    キーワード選定・競合分析の参考値としては有効ですが、')
  log('    ステージング投稿後の効果測定には使用できません。')
}

// NOTE: MCP（GSC/GA4）はメインClaudeしか呼べない。
// Loopモード時は args.gsc_data / ga4_data が null になるため
// WebSearch ベースで推定する。手動実行時はメインClaudeが渡す。
const [competitorResult, seoBaseResult] = await parallel([
  () => agent(
    `competitor-analyst として動いてください。
サイト: ${state.siteUrl}
サイト名: ${state.siteName}
優先キーワード: ${JSON.stringify(state.keywords)}

以下を調査して返してください：
- 検索上位5サイトの記事構成・見出し・文字数
- 競合が狙っているキーワード群
- コンテンツギャップ（競合が書いていてうちが書いていないテーマ）

結果をJSON形式で返してください:
{ competitor_summary, content_gaps, recommended_topics }`,
    { label: 'competitor-analyst', phase: 'データ収集' }
  ),
  () => agent(
    `data-analyst として動いてください。
サイト: ${state.siteUrl}
GSCデータ: ${JSON.stringify(state.gscData)}
GA4データ: ${JSON.stringify(state.ga4Data)}

以下を分析して返してください：
- PV上位の記事とその流入キーワード
- 順位が11〜30位で改善余地のあるキーワード
- 最近30日で伸びているページ

データがnullの場合はWebSearchでサイト概要を把握して推定してください。
結果をJSON形式で返してください:
{ top_pages, improvement_keywords, growing_pages }`,
    { label: 'data-analyst', phase: 'データ収集' }
  ),
])

// ──────────────────────────────────────────
// Node: 執筆指示書作成
// ──────────────────────────────────────────
phase('執筆指示書')

state.brief = await agent(
  `seo-analyst として動いてください。
サイト: ${state.siteUrl} / ${state.siteName}

【競合調査結果】
${JSON.stringify(competitorResult, null, 2)}

【サイトデータ分析結果】
${JSON.stringify(seoBaseResult, null, 2)}

上記をもとに、今回執筆すべき記事の執筆指示書を作成してください。

必ず含める項目：
- 記事タイトル（候補2〜3案）
- 推奨スラッグ（英数字ハイフン）
- 狙うメインキーワードと検索意図
- 推奨文字数と記事構成（H2/H3の見出し案）
- 競合との差別化ポイント
- 注意事項・禁止表現

結果をJSON形式で返してください:
{ title, slug, main_keyword, search_intent, structure, word_count, differentiators, notes }`,
  { label: 'seo-analyst', phase: '執筆指示書' }
)

const slug        = state.brief?.slug    || 'article'
const articlePath = `${state.articlesDir}/${slug}.md`
const htmlPath    = `${state.articlesDir}/${slug}.html`

// ──────────────────────────────────────────
// Node: 執筆（ループはこのノード内部に閉じる）
// ──────────────────────────────────────────
// ゲートが "revise" を返すたびにこのブロックへ戻る。
// ループ自体はグラフの外ではなく、write→gate のエッジサイクルとして表現する。
let edge = 'revise'

while (edge === 'revise') {
  phase('執筆')
  state.attempt++

  await agent(
    `writer として動いてください。
ARTICLES_DIR: ${state.articlesDir}

【執筆指示書】
${JSON.stringify(state.brief, null, 2)}

${state.feedback ? `【前回レビューのフィードバック（試行${state.attempt - 1}回目）】\n${state.feedback}\n` : ''}

以下の仕様で記事を執筆し、${articlePath} に保存してください：
- 出力はMarkdown（.md）のみ
- Frontmatterに title / slug / post_type: post / post_author: 1 を含める
- 文字数: ${state.brief?.word_count || '3000〜5000'}字
- 指示書の見出し構成に従う
- 競合との差別化ポイントを必ず盛り込む

保存完了後、"保存完了" とだけ返してください。`,
    { label: `writer (試行${state.attempt}回目)`, phase: '執筆' }
  )

  // ── Gate: article_review.sh で評価 ──
  // Codex → Gemini → article-reviewer の優先順位で自動実行される。
  // エージェントへの直接投げは禁止（ログ全文がコンテキストに乗りトークン爆増するため）。
  phase('レビューゲート')

  const reviewRaw = await agent(
    `以下のコマンドを実行してレビュー結果のJSONだけをそのまま返してください：

ARTICLE=$(cat "${articlePath}")
bash ~/.claude/scripts/article_review.sh "$ARTICLE" "メインキーワード: ${state.brief?.main_keyword} / 検索意図: ${state.brief?.search_intent}"

stdoutのJSONオブジェクトのみを返してください。余計な説明は不要です。`,
    { label: `review-gate (試行${state.attempt}回目)`, phase: 'レビューゲート' }
  )

  // JSON文字列をパース
  state.reviewResult = typeof reviewRaw === 'string'
    ? JSON.parse(reviewRaw.match(/\{[\s\S]*\}/)?.[0] || '{"pass":false,"score":0}')
    : reviewRaw

  log(`レビュースコア: ${state.reviewResult?.score ?? '?'} / 合否: ${state.reviewResult?.pass ? 'PASS ✅' : 'FAIL ❌'} (試行${state.attempt}/${state.maxRetry}回)`)

  // Conditional edge で次のノードを決定
  edge = chooseNext(state.reviewResult, state.attempt, state.maxRetry)
  state.feedback = state.reviewResult?.improvement || ''

  if (edge === 'stop') {
    // 上限超過 → Chatwork通知して終了
    await agent(
      `notifier として動いてください。
Chatworkに以下のメッセージを送信してください：

[記事生成ループ ⚠️ 要確認] ${state.siteName}
${state.maxRetry}回レビューを実施しましたが合格できませんでした。
記事ファイル: ${articlePath}
最終スコア: ${state.reviewResult?.score ?? '?'}点
主な問題: ${state.reviewResult?.issues?.map(i => i.message).join(' / ') || '不明'}

手動での確認・修正をお願いします。`,
      { label: 'notifier (上限超過)', phase: 'レビューゲート' }
    )
    return {
      success: false,
      reason:  'max_retry_exceeded',
      score:   state.reviewResult?.score,
      file:    articlePath,
    }
  }
}
// edge === 'pass' でループを抜けてWP投稿へ

// ──────────────────────────────────────────
// Node: MD→HTML変換 → WP投稿
// ──────────────────────────────────────────
phase('WP投稿')

await agent(
  `以下のコマンドを実行してください：
python3 ~/.claude/scripts/article_md_to_html.py "${articlePath}" "${htmlPath}"

完了したら "変換完了" とだけ返してください。`,
  { label: 'md→html変換', phase: 'WP投稿' }
)

state.wpResult = await agent(
  `wp-operator として動いてください。
ARTICLES_DIR: ${state.articlesDir}
ENV: ${state.env}

接続情報は ${state.projectDir}/.claude/settings.ssh.json の "${state.env}" キーを参照してください。

以下の記事ファイルをWordPressに投稿してください：
HTMLファイル: ${htmlPath}
投稿ステータス: ${state.wpStatus}
${state.isStaging ? '※ STAGING環境への投稿です。本番サイトには影響しません。' : '※ PRODUCTION環境への投稿です。公開されます。'}

完了後、以下をJSON形式で返してください:
{ post_id, post_url, status }`,
  { label: `wp-operator [${state.env}]`, phase: 'WP投稿' }
)

// ──────────────────────────────────────────
// Node: 通知 + SEOログ
// ──────────────────────────────────────────
phase('通知')

if (state.notifyCw) {
  await agent(
    `notifier として動いてください。
Chatworkに以下の完了報告を送信してください：

[記事生成ループ ✅ 完了] ${state.siteName}
記事タイトル: ${state.brief?.title || '（未取得）'}
URL: ${state.wpResult?.post_url || '（未取得）'}
ステータス: ${state.wpStatus}
レビュースコア: ${state.reviewResult?.score ?? '?'}点
試行回数: ${state.attempt}/${state.maxRetry}回`,
    { label: 'notifier (完了通知)', phase: '通知' }
  )
}

await agent(
  `以下のコマンドを実行してください：
python3.12 ~/.claude/scripts/log_seo.py \\
  --type "記事投稿" \\
  --url "${state.wpResult?.post_url || state.siteUrl}" \\
  --keywords "${state.brief?.main_keyword || ''}" \\
  --summary "${state.brief?.title || 'ループ自動生成記事'}" \\
  --agent "article-loop" \\
  --result "post_id=${state.wpResult?.post_id || '?'} score=${state.reviewResult?.score ?? '?'} attempt=${state.attempt}"`,
  { label: 'seo-log', phase: '通知' }
)

log(`✅ 完了: ${state.brief?.title} → ${state.wpResult?.post_url}`)

return {
  success:  true,
  title:    state.brief?.title,
  slug:     slug,
  post_id:  state.wpResult?.post_id,
  post_url: state.wpResult?.post_url,
  score:    state.reviewResult?.score,
  attempts: state.attempt,
}
