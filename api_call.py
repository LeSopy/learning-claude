from dotenv import load_dotenv

from anthropic import Anthropic

load_dotenv(".env.local")

client = Anthropic()

message = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=200,
    messages=[{"role": "user", "content": "Hello, Claude"}],
)

print(message.content[0].text)
