import os
import anthropic
from dotenv import load_dotenv

load_dotenv(".env.local")  # loads ANTHROPIC_API_KEY and LINEAR_MCP_TOKEN
client = anthropic.Anthropic()

response = client.beta.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "What tools do you have available?"}],
    mcp_servers=[
        {
            "type": "url",
            "url": "https://mcp.linear.app/mcp",
            "name": "linear",
            "authorization_token": os.environ["LINEAR_MCP_TOKEN"],
        }
    ],
    tools=[
        {
            "type": "mcp_toolset",
            "mcp_server_name": "linear",
        }
    ],
    betas=["mcp-client-2025-11-20"],
)

print(response)
