# Line Guardrail Hands-ON

このプロジェクトは AWS Bedrock AgentCore を使用したガードレールシステムです。

## 🚀 GitHub Codespaces での開発

### 開始方法

1. **Codespaces の起動**

```
GitHub リポジトリページで "Code" > "Codespaces" > "Create codespace on main" をクリック
```

2. **AWS 認証情報の設定**

```bash
# .env ファイルを編集
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-west-2
# 必要に応じて
AWS_SESSION_TOKEN=your_session_token
```

## AI エージェントデプロイ

動作確認

```bash
# ベーシックエージェントの実行
uv run agent_basic.py
```

エージェントデプロイ

```bash
export $(cat /workspaces/line-guardrail/.env | grep -v ^# | xargs)

agentcore configure --entrypoint agent.py --name linebot
agentcore launch
```

## 🚀 SAM デプロイ

### 環境変数の設定

`.env`ファイルに以下の 3 つの環境変数を追加：

```bash
BEDROCK_AGENT_RUNTIME_ARN=your_bedrock_agent_runtime_arn
LINE_CHANNEL_SECRET=your_line_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
```

### デプロイ実行

```bash
cd api
make deploy
```

## 🛡️ ガードレール管理

### 犬ダメガードレール作成

#### テスト用（DRAFT）

```bash
uv run scripts/create_dog_guardrail.py
```

#### 本番用（バージョン作成）

```bash
uv run scripts/create_dog_guardrail.py --create-version
```

### 美容室ガードレール

```bash
 uv run scripts/create_beauty_salon_guardrail.py
```

### コンテキストグラウンディングチェックガードレール

```bash
 uv run scripts/create_contextual_grounding_guardrail.py --create-version
```

### ガードレール管理

#### 一覧表示

```bash
uv run scripts/manage_guardrails.py --list
```

#### 削除

```bash
# ID指定削除
uv run scripts/manage_guardrails.py --delete GUARDRAIL_ID

# 名前指定削除
uv run scripts/manage_guardrails.py --delete-by-name "NekoNekoShopGuardrail"
```

## 📦 依存関係

- Python 3.13+
- strands-agents
- boto3
- bedrock-agentcore
- bedrock-agentcore-starter-toolkit
- aws-lambda-powertools
