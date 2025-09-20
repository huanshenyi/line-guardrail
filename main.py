from dotenv import load_dotenv
from strands import Agent

load_dotenv()

agent = Agent("us.anthropic.claude-sonnet-4-20250514-v1:0")
agent("LINE Developer Communityって何？")