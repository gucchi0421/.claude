---
paths:
  - "**/ga4_settings.json"
---

# GA4 Data API フィールドリファレンス

公式ドキュメント: https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema

---

## Dimensions（ディメンション）

### 日時
| フィールド名 | 説明 |
|---|---|
| `date` | YYYYMMDD 形式の日付 |
| `dateHour` | YYYYMMDDHH 形式（時間単位） |
| `dateHourMinute` | YYYYMMDDHHmm 形式（分単位） |
| `year` | 年（YYYY） |
| `month` | 月（MM） |
| `week` | 週番号 |
| `dayOfWeek` | 曜日（0=日〜6=土） |
| `hour` | 時間（00〜23） |
| `minute` | 分（00〜59） |

### ページ・コンテンツ
| フィールド名 | 説明 |
|---|---|
| `pagePath` | ホスト名を除いたURLパス |
| `pagePathPlusQueryString` | クエリ文字列を含むURLパス |
| `pageTitle` | ページタイトル |
| `pageLocation` | 完全なURL |
| `landingPage` | セッション最初のページパス |
| `exitPage` | セッション最後のページパス |
| `contentGroup` | コンテンツグループ |

### トラフィック参照元
| フィールド名 | 説明 |
|---|---|
| `sessionSource` | セッションの参照元 |
| `sessionMedium` | セッションのメディア |
| `sessionCampaignName` | セッションのキャンペーン名 |
| `sessionCampaignId` | セッションのキャンペーンID |
| `sessionDefaultChannelGroup` | セッションのデフォルトチャネルグループ |
| `sessionSourceMedium` | 参照元 / メディアの複合 |
| `sessionSourcePlatform` | セッションのソースプラットフォーム |
| `source` | ユーザーの参照元 |
| `medium` | ユーザーのメディア |
| `sourceMedium` | 参照元 / メディアの複合（ユーザー） |
| `defaultChannelGroup` | デフォルトチャネルグループ（ユーザー） |
| `campaignName` | キャンペーン名（ユーザー） |
| `firstUserSource` | 初回訪問の参照元 |
| `firstUserMedium` | 初回訪問のメディア |
| `firstUserCampaignName` | 初回訪問のキャンペーン名 |
| `firstUserDefaultChannelGroup` | 初回訪問のチャネルグループ |
| `firstUserSourceMedium` | 初回訪問の参照元 / メディア |

### デバイス
| フィールド名 | 説明 |
|---|---|
| `deviceCategory` | デバイス種別（desktop / mobile / tablet） |
| `browser` | ブラウザ名 |
| `browserVersion` | ブラウザバージョン |
| `operatingSystem` | OS名 |
| `operatingSystemVersion` | OSバージョン |
| `mobileDeviceBranding` | モバイル端末ブランド |
| `mobileDeviceModel` | モバイル端末モデル |
| `screenResolution` | 画面解像度 |

### 地理情報
| フィールド名 | 説明 |
|---|---|
| `country` | 国名 |
| `countryId` | ISO 3166 国コード |
| `region` | 都道府県・州 |
| `city` | 市区町村 |
| `cityId` | 市区町村ID |
| `continent` | 大陸 |
| `subContinent` | サブ大陸 |
| `language` | 言語 |

### ユーザー属性
| フィールド名 | 説明 |
|---|---|
| `userAgeBracket` | 年齢層 |
| `userGender` | 性別 |
| `newVsReturning` | 新規 / リピーター（new / returning） |
| `audienceName` | オーディエンス名 |

### イベント・プラットフォーム
| フィールド名 | 説明 |
|---|---|
| `eventName` | イベント名 |
| `platform` | プラットフォーム（web / iOS / Android） |
| `streamId` | データストリームID |
| `streamName` | データストリーム名 |

---

## Metrics（指標）

### ユーザー
| フィールド名 | 説明 |
|---|---|
| `activeUsers` | アクティブユーザー数 |
| `newUsers` | 新規ユーザー数 |
| `totalUsers` | 総ユーザー数 |
| `active7DayUsers` | 7日間アクティブユーザー数 |
| `active28DayUsers` | 28日間アクティブユーザー数 |
| `crashAffectedUsers` | クラッシュが発生したユーザー数 |
| `dauPerMau` | DAU / MAU 比率 |
| `dauPerWau` | DAU / WAU 比率 |
| `wauPerMau` | WAU / MAU 比率 |

### セッション
| フィールド名 | 説明 |
|---|---|
| `sessions` | セッション数 |
| `sessionsPerUser` | ユーザーあたりのセッション数 |
| `bounceRate` | 直帰率（0〜1） |
| `engagedSessions` | エンゲージドセッション数 |
| `engagementRate` | エンゲージメント率（0〜1） |
| `averageSessionDuration` | 平均セッション時間（秒） |
| `userEngagementDuration` | 合計エンゲージメント時間（秒） |
| `sessionKeyEventRate` | セッションのキーイベント率 |

### ページ・スクリーン
| フィールド名 | 説明 |
|---|---|
| `screenPageViews` | ページビュー数 |
| `screenPageViewsPerSession` | セッションあたりのページビュー数 |
| `screenPageViewsPerUser` | ユーザーあたりのページビュー数 |
| `scrolledUsers` | 90%以上スクロールしたユーザー数 |

### イベント
| フィールド名 | 説明 |
|---|---|
| `eventCount` | イベント数 |
| `eventCountPerUser` | ユーザーあたりのイベント数 |
| `eventsPerSession` | セッションあたりのイベント数 |
| `keyEvents` | キーイベント数（旧: conversions） |
| `userKeyEventRate` | キーイベント率（ユーザー） |

### 収益・EC
| フィールド名 | 説明 |
|---|---|
| `purchaseRevenue` | 購入収益 |
| `totalRevenue` | 合計収益（購入 + 広告 + サブスク） |
| `transactions` | トランザクション数 |
| `transactionsPerPurchaser` | 購入者あたりのトランザクション数 |
| `averagePurchaseRevenue` | 平均購入収益 |
| `averagePurchaseRevenuePerUser` | ユーザーあたりの平均購入収益 |
| `totalPurchasers` | 購入者数 |
| `itemRevenue` | アイテム収益 |
| `itemsAddedToCart` | カートに追加されたアイテム数 |
| `itemsPurchased` | 購入されたアイテム数 |
| `itemsViewed` | 閲覧されたアイテム数 |

### 広告
| フィールド名 | 説明 |
|---|---|
| `advertiserAdClicks` | 広告クリック数 |
| `advertiserAdImpressions` | 広告表示回数 |
| `advertiserAdCost` | 広告費用 |
| `advertiserAdCostPerClick` | クリック単価（CPC） |
| `advertiserAdCostPerKeyEvent` | キーイベント単価（CPA） |
| `returnOnAdSpend` | 広告費用対効果（ROAS） |
| `totalAdRevenue` | 広告収益 |

---

## Realtime API のみ対応フィールド

**Dimensions**: `appVersion`, `audienceId`, `audienceName`, `minutesAgo`  
**Metrics**: `activeUsers`, `eventCount`, `keyEvents`, `screenPageViews`

---

## カスタムフィールドの指定方法

```json
"dimensions": ["customEvent:parameter_name"],
"metrics": ["customEvent:parameter_name"]
```

- イベントスコープ: `customEvent:parameter_name`
- ユーザースコープ: `customUser:parameter_name`
