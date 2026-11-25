import anthropic
from dotenv import load_dotenv

load_dotenv(".env.local")  # loads ANTHROPIC_API_KEY
client = anthropic.Anthropic()

# The tools array tells Claude what's available:
# a name, a description, and a JSON schema for the inputs.
tools = [
    {
        "name": "get_weather",
        "description": "Get the current weather for a city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city to get weather for",
                }
            },
            "required": ["city"],
        },
    }
    {
        "name": "lookup_building_code",
        "description": "Look up a specific building code section by its identifier. Returns the full text of that code section.",
        "input_schema": {
            "type": "object",
            "properties": {
            "section": {
                "type": "string",
                "description": "The building code section to look up"
            }
            },
            "required": ["section"]
        }
    }
]


# run_tool is just a hardcoded lookup.
# In a real app, this would hit your database, an API, whatever.
def run_tool(name, tool_input):
    match name :
        case "get_weather" :
            return f"Weather in {tool_input['city']}: 95F, sunny"
        case "lookup_building_code" :
            return f"Weather in {tool_input['city']} for the next 3 days : 38F, 45F, and 52F, sunny"
        case _ : 
            raise ValueError(f"Unknown tool: {name}")


messages = [{"role": "user", "content": "What should I wear in Austin today?"}]

# The agent loop. Each iteration sends messages to Claude
# and switches on the response's stop reason.
while True:
    response = client.messages.create(
        model="claude-opus-5-5",
        max_tokens=524,
        tools=tools,
        messages=messages,
    )

    print(f"Stop reason: {response.stop_reason}")

    if response.stop_reason == "end_turn":
        # Claude is done. Print the final text and break.
        for block in response.content:
            if block.type == "text":
                print(block.text)
        break

    elif response.stop_reason == "tool_use":
        # Find the tool use blocks in the response and run each one.
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = run_tool(block.name, block.input)
                print(f"Tool call: {block.name} {block.input} -> {result}")
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    }
                )

        # Push the assistant's response and our tool results
        # back into messages, then loop again so Claude can answer.
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

    else:
        # Any other stop reason, such as max_tokens or refusal.
        # Nothing in messages has changed, so stop here. Looping
        # again would pay for the same request over and over.
        print(f"Stopped early: {response.stop_reason}")
        break
