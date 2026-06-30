# Discord AI Secretary Bot

Discord AI Secretary Botは、Discordサーバー内の会話をGoogle Gemini APIで要約し、会話からタスクを抽出してSQLiteに保存するMVP Botです。

## 主な機能

- `/ping` でBotの稼働確認
- `/summarize count` で現在のチャンネルの直近メッセージを要約
- `/tasks extract count` で会話からタスクを抽出して保存
- `/tasks list` で未完了タスクを一覧表示
- `/tasks done task_id` でタスクを完了に変更

## セットアップ

### 1. リポジトリを取得

```bash
git clone https://github.com/your-name/discord-ai-secretary-bot.git
cd discord-ai-secretary-bot
```

### 2. 仮想環境を作成

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS / Linux:

```bash
source .venv/bin/activate
```

### 3. 依存関係をインストール

```bash
pip install -r requirements.txt
```

### 4. `.env` を設定

`.env.example` をコピーして `.env` を作成します。

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

`.env` に以下を設定してください。

```env
DISCORD_BOT_TOKEN=your_discord_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_PATH=data/bot.db
```

`.env` は `.gitignore` に含まれているため、GitHubに公開しないでください。

## Discord Developer Portalの設定

1. [Discord Developer Portal](https://discord.com/developers/applications)でApplicationを作成します。
2. Botを作成し、Tokenを発行して `DISCORD_BOT_TOKEN` に設定します。
3. BotのPrivileged Gateway Intentsで `Message Content Intent` を有効にします。
4. OAuth2 URL Generatorで以下を選択します。
   - Scopes: `bot`, `applications.commands`
   - Bot Permissions: `Read Message History`, `Send Messages`, `Use Slash Commands`
5. 生成されたURLからBotをサーバーに招待します。

## 起動方法

```bash
python run.py
```

起動時にSlash Commandを同期します。Discord側に反映されるまで少し時間がかかる場合があります。

## コマンド一覧

| コマンド | 説明 |
| --- | --- |
| `/ping` | `Pong!` を返します。 |
| `/summarize count` | 現在のチャンネルの直近メッセージを要約します。`count` は10から200、デフォルト50です。 |
| `/tasks extract count` | 現在のチャンネルの直近メッセージからタスクを抽出して保存します。`count` は10から200、デフォルト100です。 |
| `/tasks list` | 現在のサーバーの未完了タスクを最大20件表示します。 |
| `/tasks done task_id` | 指定したIDの未完了タスクを完了にします。 |

## 使用例

会話を要約する:

```text
/summarize count:50
```

タスクを抽出する:

```text
/tasks extract count:100
```

未完了タスクを確認する:

```text
/tasks list
```

タスクを完了にする:

```text
/tasks done task_id:1
```

## テスト

外部APIには接続せず、JSONパースとSQLite処理だけをテストします。

```bash
pytest
```

## 今後のロードマップ

- タスクの担当者をDiscordユーザーに紐付ける
- 期限の自然言語解析を強化する
- タスクの削除・再オープン機能を追加する
- チャンネル別の表示フィルターを追加する
- 定期要約機能を追加する

## ライセンス

MIT License
