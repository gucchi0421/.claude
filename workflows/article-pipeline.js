export const meta = {
  name: 'article-pipeline',
  description: 'AIO記事自動生成 v2: リサーチ→執筆→ファクトチェック→品質ゲート→WP下書き保存→Chatwork通知',
  phases: [
    { title: 'リサーチ',       detail: 'Geminiグラウンディングで競合・ニーズ調査' },
    { title: '執筆指示書',     detail: 'seo-analyst がAIO要件込みの指示書を作成' },
    { title: '執筆',           detail: 'Claude Sonnet 5.5 で記事を執筆' },
    { title: 'ファクトチェック', detail: 'GPT-6.1 Sol で別モデル検証' },
    { title: '品質ゲート',     detail: 'article-reviewer が6項目チェック（スコア85点以上で合格）' },
    { title: '画像',           detail: '【手動】CEOがWordPress下書き上でアイキャッチを設定' },
    { title: 'WP下書き保存',   detail: 'wp-operator が REST APIで下書き保存' },
    { title: '通知',           detail: 'Chatworkで下書きURLと承認依頼を送信' },
  ],
}

// ──────────────────────────────────────────
// args 構造:
// {
//   project_dir: string,         // プロジェクト絶対パス
//   seo_config: object,          // settings.seo.json の内容
//   gsc_csv: string|null,        // GA4日次CSVパス（GitHub Actionsが蓄積）
//   ga4_csv: string|null,        // GSC日次CSVパス
// }
//
// settings.seo.json の構造（v2）:
// {
//   "env": "staging" | "production",
//   "production": { "site_url", "site_name", "wp_api_url", "wp_app_password_key" },
//   "staging":    { ... },
//   "articles_dir": "/absolute/path",
//   "max_review_retry": 3,
//   "target_keywords": [],
//   "notify_chatwork": true,
//   "chatwork_room_id": "123456",
//   "image_mode": "manual"       // "manual" | "adobe_stock"（将来）
// }
// ──────────────────────────────────────────

const cfg    = args?.seo_config || {}
const env    = cfg.env || 'staging'
const envCfg = cfg[env] || {}

const state = {
  env,
  isStaging:    env === 'staging',
  projectDir:   args?.project_dir   || '.',
  siteUrl:      envCfg.site_url     || '',
  siteName:     envCfg.site_name    || '',
  wpApiUrl:     envCfg.wp_api_url   || '',
  wpPassKey:    envCfg.wp_app_password_key || 'WP_APP_PASSWORD',
  articlesDir:  cfg.articles_dir    || `${args?.project_dir || '.'}/.claude/articles`,
  maxRetry:     cfg.max_review_retry || 3,
  notifyCw:     cfg.notify_chatwork !== false,
  cwRoomId:     cfg.chatwork_room_id || '',
  imageMode:    cfg.image_mode      || 'manual',
  keywords:     cfg.target_keywords || [],
  gscCsv:       args?.gsc_csv       || null,
  ga4Csv:       args?.ga4_csv       || null,
  // 実行中に更新
  brief:        null,
  attempt:      0,
  feedback:     '',
  reviewResult: null,
  wpResult:     null,
}

// ── Conditional edge: レビュー結果を3方向に分岐 ──
function chooseNext(reviewResult, attempt, maxRetry) {
  if (reviewResult?.pass)     return 'pass'
  if (attempt >= maxRetry)    return 'stop'
  return 'revise'
}

// ──────────────────────────────────────────
// Phase: リサーチ（Gemini グラウンディング優先）
// ──────────────────────────────────────────
phase('リサーチ')
log(`[${state.env.toUpperCase()}] 対象サイト: ${state.siteUrl}`)

const [competitorResult, seoBaseResult] = await parallel([
  // competitor-analyst: AIO調査含む競合リサーチ
  () => agent(
    `competitor-analyst として動いてください。
サイト: ${state.siteUrl} / ${state.siteName}
優先キーワード: ${JSON.stringify(state.keywords)}

以下を調査して返してください：
- 検索上位5サイトの記事構成・見出し・文字数
- Google AI Overview / Perplexity での引用状況と引用記事の共通構造
- コンテンツギャップ（競合が書いていてうちが書いていないテーマ）

結果をJSON形式で返してください:
{ competitor_summary, aio_citation_status, content_gaps, recommended_topics }`,
    { label: 'competitor-analyst', phase: 'リサーチ' }
  ),
  // data-analyst: 蓄積データから伸びしろ分析
  () => agent(
    `data-analyst として動いてください。
サイト: ${state.siteUrl}
GSCデータ（CSV）: ${state.gscCsv ? `パス: ${state.gscCsv}` : 'null（WebSearchで推定）'}
GA4データ（CSV）: ${state.ga4Csv ? `パス: ${state.ga4Csv}` : 'null'}

以下を分析して返してください：
- PV上位の記事とその流入キーワード
- 順位11〜30位で改善余地のあるキーワード
- 最近30日で伸びているページ

データがnullの場合はWebSearchでサイト概要を把握して推定してください。
結果をJSON形式で返してください:
{ top_pages, improvement_keywords, growing_pages }`,
    { label: 'data-analyst', phase: 'リサーチ' }
  ),
])

// ──────────────────────────────────────────
// Phase: 執筆指示書（AIO要件を必須項目として含める）
// ──────────────────────────────────────────
phase('執筆指示書')

state.brief = await agent(
  `seo-analyst として動いてください。
サイト: ${state.siteUrl} / ${state.siteName}

【競合調査結果（AIO引用状況含む）】
${JSON.stringify(competitorResult, null, 2)}

【サイトデータ分析結果】
${JSON.stringify(seoBaseResult, null, 2)}

AIO（AI検索引用）を最優先に考慮してキーワードを選定し、執筆指示書を作成してください。

必ず含める項目：
- 記事タイトル（候補2〜3案）
- 推奨スラッグ（英数字ハイフン）
- 狙うメインキーワードと検索意図
- 推奨文字数（2,500字以上）と記事構成（H2/H3の見出し案）
- AIO対応必須要素（冒頭結論の概要・FAQ問題案3〜5問・使うべき定義/数値/比較表・出典候補URL）
- 競合との差別化ポイント
- 内部リンク候補（絶対URL 2〜3本）
- 注意事項・禁止表現

結果をJSON形式で返してください:
{ title, slug, main_keyword, search_intent, word_count, structure, aio_requirements, differentiators, internal_link_candidates, notes }`,
  { label: 'seo-analyst', phase: '執筆指示書' }
)

const slug        = state.brief?.slug    || 'article'
const articlePath = `${state.articlesDir}/${slug}.md`

// ──────────────────────────────────────────
// Phase: 執筆 + ファクトチェック + 品質ゲート（ループ）
// ──────────────────────────────────────────
let edge = 'revise'

while (edge === 'revise') {
  // ── 執筆（Claude Sonnet 5.5）──
  phase('執筆')
  state.attempt++

  await agent(
    `writer として動いてください。
ARTICLES_DIR: ${state.articlesDir}

【執筆指示書】
${JSON.stringify(state.brief, null, 2)}

${state.feedback ? `【前回レビューのフィードバック（試行${state.attempt - 1}回目）】\n${state.feedback}\n` : ''}

AIO要件（冒頭結論・FAQ 3〜5問・定義/数値/比較表・出典URL・著者情報）を必ず満たして執筆し、
${articlePath} に保存してください。

この後 GPT-6.1 Sol によるファクトチェックが入ります。
断言できない情報は「〜とされています」と書き、数値・固有名詞には出典URLを付けてください。

保存完了後、"保存完了" とだけ返してください。`,
    { label: `writer (試行${state.attempt}回目)`, phase: '執筆' }
  )

  // ── ファクトチェック（GPT-6.1 Sol）──
  phase('ファクトチェック')

  const factResult = await agent(
    `fact-checker として動いてください。
記事ファイル: ${articlePath}

以下の観点でファクトチェックを行ってください（執筆とは別モデルで相互検証）：
- 数値・統計・固有名詞の正確性
- 出典URLが実在し、記述内容と対応しているか
- 「〜とされています」表現の適切性
- 誇大表現・景品表示法上の問題となりそうな断言

問題があれば記事ファイルに【要確認: ...】コメントを追記してください。
問題なければ "ファクトチェック完了" とだけ返してください。`,
    { label: `fact-checker (試行${state.attempt}回目)`, phase: 'ファクトチェック' }
  )

  // ── 品質ゲート ──
  phase('品質ゲート')

  const reviewRaw = await agent(
    `以下のコマンドを実行してレビュー結果のJSONだけをそのまま返してください：

ARTICLE=$(cat "${articlePath}")
bash ~/.claude/scripts/article_review.sh "$ARTICLE" "AIO要件（冒頭結論・FAQ・出典URL・著者情報）も含めて品質ゲート6項目を評価すること。メインキーワード: ${state.brief?.main_keyword}"

stdoutのJSONオブジェクトのみを返してください。余計な説明は不要です。`,
    { label: `review-gate (試行${state.attempt}回目)`, phase: '品質ゲート' }
  )

  state.reviewResult = typeof reviewRaw === 'string'
    ? JSON.parse(reviewRaw.match(/\{[\s\S]*\}/)?.[0] || '{"pass":false,"score":0}')
    : reviewRaw

  log(`レビュースコア: ${state.reviewResult?.score ?? '?'} / 合否: ${state.reviewResult?.pass ? 'PASS ✅' : 'FAIL ❌'} (試行${state.attempt}/${state.maxRetry}回)`)

  edge = chooseNext(state.reviewResult, state.attempt, state.maxRetry)
  state.feedback = state.reviewResult?.improvement || ''

  if (edge === 'stop') {
    if (state.notifyCw) {
      await agent(
        `notifier として動いてください。
Chatworkのルームに以下のメッセージを送信してください：

[記事生成 ⚠️ 要確認] ${state.siteName}
${state.maxRetry}回レビューを実施しましたが合格できませんでした。
記事ファイル: ${articlePath}
最終スコア: ${state.reviewResult?.score ?? '?'}点
主な問題: ${state.reviewResult?.issues?.map(i => i.message).join(' / ') || '不明'}

手動での確認・修正をお願いします。`,
        { label: 'notifier（上限超過）', phase: '通知' }
      )
    }
    return { success: false, reason: 'max_retry_exceeded', score: state.reviewResult?.score, file: articlePath }
  }
}

// ──────────────────────────────────────────
// Phase: 画像
// image_mode: "manual" → スキップ（CEOが下書き確認時に手動設定）
// image_mode: "adobe_stock" → TODO: Adobe Stock API連携（将来実装）
// ──────────────────────────────────────────
phase('画像')

if (state.imageMode === 'manual') {
  log('📷 画像モード: 手動設定。CEOがWordPress下書き上でアイキャッチを設定してください。')
  // ── TODO: Adobe Stock API差し替えポイント ──
  // image_mode === "adobe_stock" の場合の実装はここに追加する
  // await agent(`Adobe Stock APIで候補3枚を取得...`, ...)
} else {
  log(`⚠️ 未対応の image_mode: ${state.imageMode}。手動設定にフォールバックします。`)
}

// ──────────────────────────────────────────
// Phase: WP下書き保存（REST API）
// ──────────────────────────────────────────
phase('WP下書き保存')

state.wpResult = await agent(
  `wp-operator として動いてください。
ARTICLES_DIR: ${state.articlesDir}
ENV: ${state.env}

接続情報は ${state.projectDir}/.claude/settings.seo.json の "${state.env}" キーを参照してください（WP REST API使用）。

以下の記事ファイルをWordPressに**下書き（draft）として保存**してください：
Markdownファイル: ${articlePath}

注意：
- status は必ず "draft"（自動公開禁止）
- アイキャッチ画像は手動設定のため featured_media はセットしない
- 保存完了後、post_id と下書きプレビューURLを返してください

結果をJSON形式で返してください:
{ post_id, draft_url, status }`,
  { label: `wp-operator [${state.env}]`, phase: 'WP下書き保存' }
)

// ──────────────────────────────────────────
// Phase: 通知（Chatworkで承認依頼）
// ──────────────────────────────────────────
phase('通知')

if (state.notifyCw) {
  await agent(
    `notifier として動いてください。
Chatworkに以下の承認依頼を送信してください：

[記事生成完了 ✅ 承認依頼] ${state.siteName}

記事タイトル: ${state.brief?.title || '（未取得）'}
下書きURL: ${state.wpResult?.draft_url || '（未取得）'}
レビュースコア: ${state.reviewResult?.score ?? '?'}点

━━━━━━━━━━━━━━━━━━━━━━
✅ 確認・承認の手順
1. 上記URLで下書きをご確認ください
2. アイキャッチ画像を手動で設定してください
3. 問題なければステータスを「予約投稿」に変更してください → 自動公開されます
4. 修正がある場合はWordPress上で直接編集後に「予約投稿」に変更してください

⚠️ 48時間以内にご対応をお願いします（超過した場合は再通知します）`,
    { label: 'notifier（承認依頼）', phase: '通知' }
  )
}

log(`✅ 完了: ${state.brief?.title} → 下書きURL: ${state.wpResult?.draft_url}`)

return {
  success:   true,
  title:     state.brief?.title,
  slug,
  post_id:   state.wpResult?.post_id,
  draft_url: state.wpResult?.draft_url,
  score:     state.reviewResult?.score,
  attempts:  state.attempt,
  image_mode: state.imageMode,
}
