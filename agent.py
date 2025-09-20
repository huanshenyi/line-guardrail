from dotenv import load_dotenv
from strands import Agent
from bedrock_agentcore.runtime import BedrockAgentCoreApp

load_dotenv()

agent = Agent("us.anthropic.claude-sonnet-4-20250514-v1:0")
app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload):
     """Process user input and return a response"""
     prompt = payload.get("prompt", "Hello")
     result = agent(prompt)
     return {"result": result.message}

if __name__ == "__main__":
    app.run()
