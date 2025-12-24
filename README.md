# Google Calendar イベント情報取得ツール

Google Calendar APIを使用して、イベントの作成日時・更新日時・作成者などの詳細情報を取得するスクリプトです。

## 取得できる情報

- イベントタイトル・説明
- 開始/終了日時
- **作成日時 (created)**
- **最終更新日時 (updated)**
- **作成者 (creator)**
- 主催者 (organizer)
- 参加者一覧と回答状況
- イベントステータス
- 繰り返し設定

## セットアップ手順

### 1. Google Cloud Console での設定

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成（または既存のプロジェクトを選択）
3. 左メニューから「APIとサービス」→「ライブラリ」を選択
4. 「Google Calendar API」を検索して有効化
5. 「APIとサービス」→「認証情報」を選択
6. 「認証情報を作成」→「OAuthクライアントID」を選択
7. アプリケーションの種類は「デスクトップアプリ」を選択
8. 作成後、JSONファイルをダウンロード
9. ダウンロードしたファイルを `credentials.json` にリネームしてこのディレクトリに配置

### 2. OAuth同意画面の設定

初回利用時は OAuth 同意画面の設定が必要です：

1. 「APIとサービス」→「OAuth同意画面」を選択
2. ユーザータイプは「外部」を選択
3. 必要な情報を入力（アプリ名、メールアドレス等）
4. スコープで「.../auth/calendar.readonly」を追加
5. テストユーザーに自分のGoogleアカウントを追加

### 3. Python環境のセットアップ

```bash
# 仮想環境の作成（推奨）
python3 -m venv venv
source venv/bin/activate

# 依存パッケージのインストール
pip install -r requirements.txt
```

## 使い方

```bash
python get_event_info.py
```

実行すると対話形式で：
1. カレンダーを選択
2. 検索キーワードを入力（オプション）
3. 検索期間を指定
4. イベント一覧から詳細を見たいイベントを選択

## 注意事項

- **修正履歴について**: Google Calendar APIでは完全な修正履歴は取得できません。取得できるのは「最終更新日時」のみです。変更の詳細履歴が必要な場合は、定期的にイベント情報を保存して差分を比較する仕組みを別途構築する必要があります。

- **認証について**: 初回実行時にブラウザが開き、Googleアカウントでの認証が求められます。認証後、`token.json` が作成され、次回以降は自動的にログインされます。

- **スコープ**: このスクリプトは読み取り専用（`calendar.readonly`）のスコープを使用しており、カレンダーの変更は行いません。

## ファイル構成

```
.
├── README.md
├── requirements.txt
├── get_event_info.py      # メインスクリプト
├── credentials.json       # ← 自分で配置（Git管理外）
└── token.json            # ← 自動生成（Git管理外）
```

## トラブルシューティング

### 「credentials.json が見つかりません」エラー
Google Cloud Console から OAuth クライアントIDの JSON をダウンロードし、`credentials.json` という名前で配置してください。

### 認証エラー
`token.json` を削除して再度認証を行ってください。
