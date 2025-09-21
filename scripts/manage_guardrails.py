#!/usr/bin/env python3
"""
AWS Bedrock Guardrail Management Script

This script provides management functionality for AWS Bedrock guardrails,
including listing, deleting, and viewing details of existing guardrails.
"""

import argparse
import os
import sys
from typing import List, Dict, Any, Optional

import boto3
from botocore.exceptions import ClientError


def get_bedrock_client():
    """
    Get configured Bedrock client.

    Returns:
        boto3 Bedrock client
    """
    region = os.getenv("AWS_REGION", "us-west-2")
    return boto3.client("bedrock", region_name=region)


def list_guardrails() -> List[Dict[str, Any]]:
    """
    List all guardrails in the account.

    Returns:
        List of guardrail summaries

    Raises:
        ClientError: If AWS API call fails
    """
    try:
        client = get_bedrock_client()
        response = client.list_guardrails()

        guardrails = response.get('guardrails', [])

        print(f"📋 Found {len(guardrails)} guardrail(s):")
        print()

        for guardrail in guardrails:
            print(f"🛡️  Name: {guardrail['name']}")
            print(f"   ID: {guardrail['id']}")
            print(f"   Status: {guardrail['status']}")
            print(f"   Version: {guardrail['version']}")
            print(f"   Description: {guardrail.get('description', 'N/A')}")
            print(f"   Created: {guardrail['createdAt']}")
            print()

        return guardrails

    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"❌ AWS API Error ({error_code}): {error_message}")
        raise


def get_guardrail_details(guardrail_id: str, version: Optional[str] = None) -> Dict[str, Any]:
    """
    Get detailed information about a specific guardrail.

    Args:
        guardrail_id: The guardrail ID
        version: The guardrail version (optional, defaults to latest)

    Returns:
        Dict containing guardrail details

    Raises:
        ClientError: If AWS API call fails
    """
    try:
        client = get_bedrock_client()

        params = {"guardrailIdentifier": guardrail_id}
        if version:
            params["guardrailVersion"] = version

        response = client.get_guardrail(**params)

        guardrail = response
        print(f"🛡️  Guardrail Details:")
        print(f"   Name: {guardrail['name']}")
        print(f"   ID: {guardrail['guardrailId']}")
        print(f"   ARN: {guardrail['guardrailArn']}")
        print(f"   Status: {guardrail['status']}")
        print(f"   Version: {guardrail['version']}")
        print(f"   Description: {guardrail.get('description', 'N/A')}")
        print(f"   Created: {guardrail['createdAt']}")
        print(f"   Updated: {guardrail['updatedAt']}")

        # Show word policy if exists
        if 'wordPolicyConfig' in guardrail:
            words_config = guardrail['wordPolicyConfig'].get('wordsConfig', [])
            if words_config:
                blocked_words = [word['text'] for word in words_config]
                print(f"   Blocked Words: {', '.join(blocked_words)}")

        return guardrail

    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"❌ AWS API Error ({error_code}): {error_message}")
        raise


def delete_guardrail(guardrail_id: str) -> None:
    """
    Delete a guardrail by ID.

    Args:
        guardrail_id: The guardrail ID to delete

    Raises:
        ClientError: If AWS API call fails
    """
    try:
        client = get_bedrock_client()

        print(f"🗑️  Deleting guardrail: {guardrail_id}")

        response = client.delete_guardrail(guardrailIdentifier=guardrail_id)

        print("✅ Guardrail deleted successfully!")

    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"❌ AWS API Error ({error_code}): {error_message}")
        raise


def delete_guardrail_by_name(name: str) -> None:
    """
    Delete a guardrail by name.

    Args:
        name: The guardrail name to delete

    Raises:
        ClientError: If AWS API call fails
        ValueError: If guardrail with name not found
    """
    try:
        # First, find the guardrail by name
        guardrails = list_guardrails()

        matching_guardrail = None
        for guardrail in guardrails:
            if guardrail['name'] == name:
                matching_guardrail = guardrail
                break

        if not matching_guardrail:
            raise ValueError(f"Guardrail with name '{name}' not found")

        # Delete the found guardrail
        delete_guardrail(matching_guardrail['id'])

    except ValueError as e:
        print(f"❌ Error: {str(e)}")
        raise


def main() -> int:
    """
    Main function for command line execution.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(
        description="Manage AWS Bedrock Guardrails",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python manage_guardrails.py --list
  python manage_guardrails.py --details GUARDRAIL_ID
  python manage_guardrails.py --delete GUARDRAIL_ID
  python manage_guardrails.py --delete-by-name "NekoNekoShopGuardrail"
        """
    )

    parser.add_argument("--list", action="store_true", help="List all guardrails")
    parser.add_argument("--details", metavar="ID", help="Show details for a specific guardrail")
    parser.add_argument("--delete", metavar="ID", help="Delete guardrail by ID")
    parser.add_argument("--delete-by-name", metavar="NAME", help="Delete guardrail by name")
    parser.add_argument("--version", metavar="VERSION", help="Guardrail version (for --details)")

    args = parser.parse_args()

    # Check if no arguments provided
    if not any([args.list, args.details, args.delete, args.delete_by_name]):
        parser.print_help()
        return 1

    try:
        if args.list:
            list_guardrails()

        elif args.details:
            get_guardrail_details(args.details, args.version)

        elif args.delete:
            # Confirm deletion
            response = input(f"Are you sure you want to delete guardrail '{args.delete}'? (y/N): ")
            if response.lower() in ['y', 'yes']:
                delete_guardrail(args.delete)
            else:
                print("❌ Deletion cancelled")
                return 1

        elif args.delete_by_name:
            # Confirm deletion
            response = input(f"Are you sure you want to delete guardrail '{args.delete_by_name}'? (y/N): ")
            if response.lower() in ['y', 'yes']:
                delete_guardrail_by_name(args.delete_by_name)
            else:
                print("❌ Deletion cancelled")
                return 1

        return 0

    except Exception as e:
        print(f"\n💥 Operation failed: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())