import argparse
import os
import sys
from typing import Dict, Any

import boto3
from botocore.exceptions import ClientError


# Configuration
GUARDRAIL_NAME = "beauty-salon-guardrail"
GUARDRAIL_DESCRIPTION = "美容室予約システム用のガードレール - 予約関連以外の話題とPII情報をブロック"
BLOCKED_INPUT_MESSAGE = "申し訳ございませんが、用途以外の回答ができません。美容室の予約に関するご質問をお願いいたします。"
BLOCKED_OUTPUT_MESSAGE = "申し訳ございませんが、用途以外の回答ができません。美容室の予約に関するご質問をお願いいたします。"


def create_beauty_salon_guardrail() -> Dict[str, Any]:
    """
    Create a comprehensive Bedrock guardrail for beauty salon reservation systems.

    Returns:
        Dict containing guardrail creation response

    Raises:
        ClientError: If AWS API call fails
        Exception: For other unexpected errors
    """
    # Initialize Bedrock client
    region = os.getenv("AWS_REGION", "us-west-2")
    client = boto3.client("bedrock", region_name=region)

    topics_config = [
        {
            "name": "GeneralChit-Chat",
            "type": "DENY",
            "definition": "日常会話、雑談、世間話、趣味の話題など、美容室の予約や施術に関係のない一般的な会話内容",
            "examples": [
                "今日の天気はどうですか？",
                "最近のニュースについて教えて",
                "おすすめの映画は何ですか？",
                "料理のレシピを教えて",
                "政治について話しましょう"
            ]
        },
        {
            "name": "Technology-Programming",
            "type": "DENY",
            "definition": "プログラミング、IT技術、ソフトウェア開発、コンピューター関連の質問や話題",
            "examples": [
                "Pythonのコードを書いて",
                "データベースの設計方法",
                "機械学習について教えて",
                "ウェブサイトの作り方",
                "AIの仕組みについて"
            ]
        },
        {
            "name": "Academic-Research",
            "type": "DENY",
            "definition": "学術研究、論文執筆、大学の課題、学習の代行など教育・研究関連の依頼",
            "examples": [
                "論文を書いて",
                "宿題を手伝って",
                "研究データの分析",
                "レポートの作成"
            ]
        }
    ]

    # Define PII entities configuration
    pii_entities_config = [
        {"type": "PASSWORD", "action": "BLOCK"},
        {"type": "CREDIT_DEBIT_CARD_NUMBER", "action": "BLOCK"},
        {"type": "CREDIT_DEBIT_CARD_CVV", "action": "BLOCK"},
        {"type": "US_SOCIAL_SECURITY_NUMBER", "action": "BLOCK"},
        {"type": "US_PASSPORT_NUMBER", "action": "BLOCK"},
        {"type": "DRIVER_ID", "action": "BLOCK"},
        {"type": "US_BANK_ACCOUNT_NUMBER", "action": "BLOCK"},
        {"type": "US_BANK_ROUTING_NUMBER", "action": "BLOCK"},
        {"type": "PIN", "action": "BLOCK"},
        {"type": "AWS_ACCESS_KEY", "action": "BLOCK"},
        {"type": "AWS_SECRET_KEY", "action": "BLOCK"}
    ]

    # Define regex patterns for Japanese PII
    regexes_config = [
        {
            "name": "Japanese-MyNumber",
            "description": "マイナンバー",
            "pattern": "\\b\\d{4}[-\\s]?\\d{4}[-\\s]?\\d{4}\\b",
            "action": "BLOCK"
        }
    ]

    # Create guardrail command parameters
    params = {
        "name": GUARDRAIL_NAME,
        "description": GUARDRAIL_DESCRIPTION,
        "blockedInputMessaging": BLOCKED_INPUT_MESSAGE,
        "blockedOutputsMessaging": BLOCKED_OUTPUT_MESSAGE,
        "topicPolicyConfig": {
            "topicsConfig": topics_config
        },
        "sensitiveInformationPolicyConfig": {
            "piiEntitiesConfig": pii_entities_config,
            "regexesConfig": regexes_config
        }
    }

    try:
        print(f"🚀 Creating beauty salon guardrail '{GUARDRAIL_NAME}'...")
        print(f"📍 Region: {region}")
        print(f"🚫 Blocked topics: {len(topics_config)} categories")
        print(f"🔒 PII entities: {len(pii_entities_config)} types")
        print(f"📝 Custom regex patterns: {len(regexes_config)} patterns")

        response = client.create_guardrail(**params)

        print("\n✅ Beauty salon guardrail created successfully!")
        print(f"📋 Guardrail ID: {response['guardrailId']}")
        print(f"📋 Guardrail ARN: {response['guardrailArn']}")
        print(f"🔢 Version: {response['version']}")

        # Display configuration details
        print(f"\n📋 Configuration Summary:")
        print(f"   Blocked Topics:")
        for topic in topics_config:
            print(f"   - {topic['name']}: {topic['definition'][:50]}...")
        print(f"   PII Protection: {len(pii_entities_config)} standard types + Japanese MyNumber")

        return response

    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"❌ AWS API Error ({error_code}): {error_message}")
        raise

    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        raise


def create_guardrail_version(guardrail_id: str) -> Dict[str, Any]:
    """
    Create a version of an existing guardrail.

    Args:
        guardrail_id: The guardrail ID to create a version for

    Returns:
        Dict containing guardrail version creation response

    Raises:
        ClientError: If AWS API call fails
        Exception: For other unexpected errors
    """
    region = os.getenv("AWS_REGION", "us-west-2")
    client = boto3.client("bedrock", region_name=region)

    try:
        print(f"📦 Creating version for guardrail: {guardrail_id}")

        response = client.create_guardrail_version(
            guardrailIdentifier=guardrail_id
        )

        print("✅ Guardrail version created successfully!")
        print(f"📋 Version: {response['version']}")

        return response

    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"❌ AWS API Error creating version ({error_code}): {error_message}")
        raise

    except Exception as e:
        print(f"❌ Unexpected error creating version: {str(e)}")
        raise


def main() -> int:
    """
    Main function for command line execution.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(
        description="Create AWS Bedrock Beauty Salon Guardrail",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python create_beauty_salon_guardrail.py                # Create DRAFT guardrail only
  python create_beauty_salon_guardrail.py --create-version  # Create DRAFT + Version (for production)
        """
    )

    parser.add_argument(
        "--create-version",
        action="store_true",
        help="Create a version after creating the guardrail (required for production use)"
    )

    args = parser.parse_args()

    try:
        # Create the guardrail
        guardrail_response = create_beauty_salon_guardrail()
        guardrail_id = guardrail_response['guardrailId']

        # Create version if requested
        if args.create_version:
            print()  # Add space between operations
            create_guardrail_version(guardrail_id)

        print(f"\n🎉 Beauty salon guardrail setup complete!")
        if args.create_version:
            print("✅ Ready for production use!")
        else:
            print("⚠️  DRAFT status - use --create-version for production")

        return 0

    except Exception as e:
        print(f"\n💥 Failed to create guardrail: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())