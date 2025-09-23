import boto3
import json
import os
import uuid
from typing import Dict, Any

from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    ShowLoadingAnimationRequest,
    TextMessage
)

# Initialize LINE Bot API configuration globally
LINE_CONFIGURATION = None
if 'LINE_CHANNEL_ACCESS_TOKEN' in os.environ:
    LINE_CONFIGURATION = Configuration(access_token=os.environ['LINE_CHANNEL_ACCESS_TOKEN'])

def show_loading_animation_sdk(user_id: str, duration_seconds: int = 60) -> bool:
    """
    Send a loading animation to the user via LINE Messaging API
    """
    try:
        if LINE_CONFIGURATION:
            with ApiClient(LINE_CONFIGURATION) as api_client:
                line_bot_api = MessagingApi(api_client)
                loading_request = ShowLoadingAnimationRequest(
                    chat_id=user_id,
                    loadingSeconds=duration_seconds
                )
                line_bot_api.show_loading_animation(loading_request)
                return True
    except Exception as e:
        print(f"ERROR: Failed to send loading animation: {str(e)}")
        return False

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for Bedrock AgentCore with LINE Message API support
    """
    
    try:
        # Parse request body
        if 'body' not in event:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Missing request body'})
            }
        
        # Parse JSON body
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        
        # Check if this is a LINE webhook event
        if 'events' in body and len(body['events']) > 0:
            return handle_line_webhook(body)
        
        # Original API Gateway handling
        prompt = body.get('prompt', 'Hello')
        
        # Call bedrock-agentcore
        result = call_bedrock_agentcore(prompt)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'result': result
            })
        }
        
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Invalid JSON in request body'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }

def handle_line_webhook(body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle LINE webhook events
    """
    try:
        if body['events'][0]['type'] == 'message':
            if body['events'][0]['message']['type'] == 'text':
                message = body['events'][0]['message']['text']
                user_id = body['events'][0]['source'].get('userId', 'unknown')
                # Show loading animation
                show_loading_animation_sdk(user_id, duration_seconds=45)
                
                # Call bedrock-agentcore
                result = call_bedrock_agentcore(message)
                
                # Send reply via LINE
                if LINE_CONFIGURATION:
                    try:
                        with ApiClient(LINE_CONFIGURATION) as api_client:
                            line_bot_api = MessagingApi(api_client)
                            line_bot_api.reply_message_with_http_info(
                                ReplyMessageRequest(
                                    reply_token=body['events'][0]['replyToken'],
                                    messages=[TextMessage(text=str(result))]
                                )
                            )
                    except Exception as line_error:
                        print(f"ERROR: Failed to send LINE message: {str(line_error)}")
    
    except Exception as e:
        print(f"ERROR: LINE webhook processing failed: {str(e)}")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Success!')
    }

def call_bedrock_agentcore(prompt: str) -> str:
    """
    Call Bedrock AgentCore and return the result
    """
    # Initialize the Bedrock AgentCore client
    agent_core_client = boto3.client('bedrock-agentcore')
    
    # Get agent runtime ARN from environment
    agent_arn = os.environ.get('BEDROCK_AGENT_RUNTIME_ARN')
    if not agent_arn:
        return 'Agent runtime ARN not configured'
    
    # Prepare the payload
    payload = json.dumps({"prompt": prompt}).encode()
    
    # Invoke the agent
    response = agent_core_client.invoke_agent_runtime(
        agentRuntimeArn=agent_arn,
        contentType="application/json",
        payload=payload,
        traceId=str(uuid.uuid4()).replace('-', ''),
    )
    
    # Process the response
    result = process_response(response)
    
    # Extract text content from the result
    if isinstance(result, dict) and 'result' in result:
        inner_result = result['result']
        if isinstance(inner_result, dict) and 'content' in inner_result:
            content = inner_result['content']
            if isinstance(content, list) and len(content) > 0:
                first_item = content[0]
                if isinstance(first_item, dict) and 'text' in first_item:
                    return first_item['text']
    
    # Fallback to string conversion
    return str(result)

def process_response(response: Dict[str, Any]) -> Any:
    """
    Process and return the response from Bedrock AgentCore
    """
    try:
        # Handle standard JSON response
        if response.get("contentType") == "application/json":
            content = []
            response_data = response.get("response", [])
            
            for chunk in response_data:
                decoded_chunk = chunk.decode('utf-8')
                content.append(decoded_chunk)
            
            full_content = ''.join(content)
            return json.loads(full_content)
        
        # Handle other content types
        else:
            return response
            
    except Exception as e:
        return f"Error processing response: {str(e)}"
