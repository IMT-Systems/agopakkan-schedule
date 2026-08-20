# あごぱっかーん 出店スケジュールカレンダー

このフォルダは、`index.html`（Googleカレンダー連携付きの出店スケジュールページ）を生成するソース一式です。

## ファイル構成

- `build_html_calendar.py` — `index.html` を生成するビルドスクリプト（Python 3）
- `events.py` — フォールバック用の予定データ（Googleカレンダー未連携時 / 8月分）
- `config.py` — Googleカレンダー連携用の設定（APIキー・カレンダーID）
- `assets/` — 埋め込み画像（アバター・IMT-Systemsロゴ）のbase64データと元画像
- `index.html` — 生成済みの最終ファイル（このままGitHub Pagesなどにデプロイ可能）

## 使い方

デザインや文言、日付ごとの予定（`events.py`）を編集したら、以下を実行して `index.html` を再生成してください。

```bash
python3 build_html_calendar.py
```

Python 3が入っていれば追加のライブラリは不要です（標準ライブラリのみ使用）。

## Googleカレンダー連携

`config.py` の `GOOGLE_CALENDAR_API_KEY` にAPIキーを設定して `python3 build_html_calendar.py` を実行すると、ページを開くたび／月を切り替えるたびにGoogleカレンダーの最新の予定を自動取得します（未設定の間は8月のみ `events.py` のフォールバック予定を表示し、他の月は空欄です）。

### APIキーの取得手順

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセスし、プロジェクトを作成（または既存のものを選択）
2. 「APIとサービス」→「ライブラリ」で **Google Calendar API** を検索して有効化
3. 「APIとサービス」→「認証情報」→「認証情報を作成」→「APIキー」で新規キーを発行
4. 発行したキーを選択し、「アプリケーションの制限」で **HTTPリファラー** を設定し、公開するドメイン（GitHub Pagesの `https://ユーザー名.github.io/*` など）に限定。「APIの制限」で **Google Calendar API のみ** に絞る（公開ページに埋め込むキーなので、悪用防止のため必ず制限をかけてください）
5. 対象のGoogleカレンダー（`config.py` の `GOOGLE_CALENDAR_ID`）の設定画面で「予定の公開設定」→「一般公開して誰でも利用できるようにする」を有効化（非公開のままだとAPIキーだけでは予定を取得できません）
6. `config.py` の `GOOGLE_CALENDAR_API_KEY` に取得したキーを貼り付け、`python3 build_html_calendar.py` を再実行して `index.html` を更新

## デプロイ

`index.html` をGitHubリポジトリのルート（または任意のフォルダ）に置き、GitHub Pagesを有効化すれば公開できます。
