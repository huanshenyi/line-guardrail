# Line Guardrail

このプロジェクトは AWS Bedrock AgentCore を使用したガードレールシステムです。

## 🚀 GitHub Codespaces での開発

### 開始方法

1. **Codespaces の起動**

   ```
   GitHub リポジトリページで "Code" > "Codespaces" > "Create codespace on main" をクリック
   ```

2. **自動セットアップ**

   - Python 3.13 環境
   - uv パッケージマネージャー
   - AWS CLI
   - SAM CLI
   - 必要な依存関係

3. **AWS 認証情報の設定**
   ```bash
   # .env ファイルを編集
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_REGION=us-west-2
   ```

### 開発コマンド

```bash
# ベーシックエージェントの実行
uv run agent_basic.py

# エージェントのデプロイ
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
python scripts/create_dog_guardrail.py
```

#### 本番用（バージョン作成）
```bash
python scripts/create_dog_guardrail.py --create-version
```

### ガードレール管理

#### 一覧表示
```bash
python scripts/manage_guardrails.py --list
```

#### 削除
```bash
# ID指定削除
python scripts/manage_guardrails.py --delete GUARDRAIL_ID

# 名前指定削除
python scripts/manage_guardrails.py --delete-by-name "NekoNekoShopGuardrail"
```

## 📦 依存関係

- Python 3.13+
- strands-agents
- boto3 (AWS SDK)
- bedrock-agentcore
- bedrock-agentcore-starter-toolkit
- aws-lambda-powertools

## 🔧 ローカル開発

### uv のインストール

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

詳細: https://docs.astral.sh/uv/getting-started/installation/

### セットアップ

```bash
# 依存関係のインストール
uv sync

# 環境変数の設定
cp .env.template .env
# .env ファイルを編集
```
