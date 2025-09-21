#!/usr/bin/env python3
"""
AWS Bedrock Dog Guardrail Creation Script

This script creates a specific guardrail for blocking dog-related content
in a cat shop application using AWS Bedrock.
"""

import argparse
import os
import sys
from typing import Dict, Any

import boto3
from botocore.exceptions import ClientError


# Configuration
BLOCKED_WORDS = ["dog", "犬"]
BLOCKED_MESSAGE = "ここはねこねこショップだから犬の物禁止"
GUARDRAIL_NAME = "NekoNekoShopGuardrail"
GUARDRAIL_DESCRIPTION = "Blocks dog-related content for cat shop"


def create_dog_guardrail() -> Dict[str, Any]:
    """
    Create a Bedrock guardrail specifically for blocking dog-related content.

    Returns:
        Dict containing guardrail creation response

    Raises:
        ClientError: If AWS API call fails
        Exception: For other unexpected errors
    """
    # Initialize Bedrock client
    region = os.getenv("AWS_REGION", "us-west-2")
    client = boto3.client("bedrock", region_name=region)

    # Prepare word configurations
    words_config = []
    for word in BLOCKED_WORDS:
        word_config = {
            "text": word
        }
        words_config.append(word_config)

    # Create guardrail command parameters
    params = {
        "name": GUARDRAIL_NAME,
        "description": GUARDRAIL_DESCRIPTION,
        "blockedInputMessaging": BLOCKED_MESSAGE,
        "blockedOutputsMessaging": BLOCKED_MESSAGE,
        "wordPolicyConfig": {
            "wordsConfig": words_config
        }
    }

    try:
        print(f"🚀 Creating guardrail '{GUARDRAIL_NAME}'...")
        print(f"📍 Region: {region}")
        print(f"🚫 Blocked words: {', '.join(BLOCKED_WORDS)}")
        print(f"💬 Block message: {BLOCKED_MESSAGE}")

        response = client.create_guardrail(**params)

        print("\n✅ Guardrail created successfully!")
        print(f"📋 Guardrail ID: {response['guardrailId']}")
        print(f"📋 Guardrail ARN: {response['guardrailArn']}")
        print(f"🔢 Version: {response['version']}")

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
        print(f"📋 Status: {response['status']}")

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
        description="Create AWS Bedrock Dog Guardrail",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python create_dog_guardrail.py                # Create DRAFT guardrail only
  python create_dog_guardrail.py --create-version  # Create DRAFT + Version (for production)
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
        guardrail_response = create_dog_guardrail()
        guardrail_id = guardrail_response['guardrailId']

        # Create version if requested
        if args.create_version:
            print()  # Add space between operations
            create_guardrail_version(guardrail_id)

        print(f"\n🎉 Dog guardrail setup complete!")
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