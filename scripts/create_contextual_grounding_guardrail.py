import argparse
import os
import sys
from typing import Dict, Any

import boto3
from botocore.exceptions import ClientError


# Configuration
GUARDRAIL_NAME = "contextual-grounding-guardrail"
GUARDRAIL_DESCRIPTION = "コンテキストグラウンディングチェック専用ガードレール - 参照情報に基づいた回答かを検証"
BLOCKED_INPUT_MESSAGE = "この質問には参照情報に基づいた回答を提供できません。"
BLOCKED_OUTPUT_MESSAGE = "この回答は参照情報に基づいていない、または関連性が低いため提供できません。"
DEFAULT_GROUNDING_THRESHOLD = 0.75
DEFAULT_RELEVANCE_THRESHOLD = 0.75


def create_contextual_grounding_guardrail(
    name: str = GUARDRAIL_NAME,
    grounding_threshold: float = DEFAULT_GROUNDING_THRESHOLD,
    relevance_threshold: float = DEFAULT_RELEVANCE_THRESHOLD
) -> Dict[str, Any]:
    """
    Create a Bedrock guardrail specifically for contextual grounding checks.

    Args:
        name: Guardrail name
        grounding_threshold: Grounding score threshold (0.0-1.0)
        relevance_threshold: Relevance score threshold (0.0-1.0)

    Returns:
        Dict containing guardrail creation response

    Raises:
        ClientError: If AWS API call fails
        Exception: For other unexpected errors
    """
    # Initialize Bedrock client
    region = os.getenv("AWS_REGION", "us-west-2")
    client = boto3.client("bedrock", region_name=region)

    # Validate thresholds
    if not (0.0 <= grounding_threshold <= 1.0):
        raise ValueError("Grounding threshold must be between 0.0 and 1.0")
    if not (0.0 <= relevance_threshold <= 1.0):
        raise ValueError("Relevance threshold must be between 0.0 and 1.0")

    # Create guardrail command parameters with contextual grounding policy only
    params = {
        "name": name,
        "description": GUARDRAIL_DESCRIPTION,
        "blockedInputMessaging": BLOCKED_INPUT_MESSAGE,
        "blockedOutputsMessaging": BLOCKED_OUTPUT_MESSAGE,
        "contextualGroundingPolicyConfig": {
            "filtersConfig": [
                {
                    "type": "GROUNDING",
                    "threshold": grounding_threshold
                },
                {
                    "type": "RELEVANCE",
                    "threshold": relevance_threshold
                }
            ]
        }
    }

    try:
        print(f"🚀 Creating contextual grounding guardrail '{name}'...")
        print(f"📍 Region: {region}")
        print(f"⚖️  Grounding threshold: {grounding_threshold}")
        print(f"🔗 Relevance threshold: {relevance_threshold}")
        print(f"💬 Block message: {BLOCKED_OUTPUT_MESSAGE}")

        response = client.create_guardrail(**params)

        print("\n✅ Contextual grounding guardrail created successfully!")
        print(f"📋 Guardrail ID: {response['guardrailId']}")
        print(f"📋 Guardrail ARN: {response['guardrailArn']}")
        print(f"🔢 Version: {response['version']}")

        # Display configuration details
        print(f"\n📋 Configuration Summary:")
        print(f"   Grounding Check: Enabled (threshold: {grounding_threshold})")
        print(f"   Relevance Check: Enabled (threshold: {relevance_threshold})")
        print(f"   Topic Policy: Disabled")
        print(f"   Word Policy: Disabled")
        print(f"   PII Policy: Disabled")

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
        description="Create AWS Bedrock Contextual Grounding Guardrail",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python create_contextual_grounding_guardrail.py                                    # Default settings
  python create_contextual_grounding_guardrail.py --create-version                  # Create with version
  python create_contextual_grounding_guardrail.py --grounding-threshold 0.8         # Custom grounding threshold
  python create_contextual_grounding_guardrail.py --relevance-threshold 0.7         # Custom relevance threshold
  python create_contextual_grounding_guardrail.py --name "my-custom-guardrail"      # Custom name
        """
    )

    parser.add_argument(
        "--name",
        default=GUARDRAIL_NAME,
        help=f"Guardrail name (default: {GUARDRAIL_NAME})"
    )

    parser.add_argument(
        "--grounding-threshold",
        type=float,
        default=DEFAULT_GROUNDING_THRESHOLD,
        help=f"Grounding score threshold 0.0-1.0 (default: {DEFAULT_GROUNDING_THRESHOLD})"
    )

    parser.add_argument(
        "--relevance-threshold",
        type=float,
        default=DEFAULT_RELEVANCE_THRESHOLD,
        help=f"Relevance score threshold 0.0-1.0 (default: {DEFAULT_RELEVANCE_THRESHOLD})"
    )

    parser.add_argument(
        "--create-version",
        action="store_true",
        help="Create a version after creating the guardrail (required for production use)"
    )

    args = parser.parse_args()

    try:
        # Create the guardrail
        guardrail_response = create_contextual_grounding_guardrail(
            name=args.name,
            grounding_threshold=args.grounding_threshold,
            relevance_threshold=args.relevance_threshold
        )
        guardrail_id = guardrail_response['guardrailId']

        # Create version if requested
        if args.create_version:
            print()  # Add space between operations
            create_guardrail_version(guardrail_id)

        print(f"\n🎉 Contextual grounding guardrail setup complete!")
        print(f"📋 Guardrail ID: {guardrail_id}")
        if args.create_version:
            print("✅ Ready for production use!")
        else:
            print("⚠️  DRAFT status - use --create-version for production")

        print(f"\n🔧 Usage in code:")
        print(f"   guardrailIdentifier=\"{guardrail_id}\"")
        print(f"   guardrailVersion=\"{'1' if args.create_version else 'DRAFT'}\"")

        return 0

    except Exception as e:
        print(f"\n💥 Failed to create guardrail: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())