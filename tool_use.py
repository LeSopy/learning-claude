from anthropic import Anthropic, beta_tool
import json
from dotenv import load_dotenv

load_dotenv(".env.local")  # loads ANTHROPIC_API_KEY
client = Anthropic()

# The tools array tells Claude what's available:
# a name, a description, and a JSON schema for the inputs.
# tools = [
#     {
#         "name": "get_weather",
#         "description": "Get the current weather for a city.",
#         "input_schema": {
#             "type": "object",
#             "properties": {
#                 "city": {
#                     "type": "string",
#                     "description": "The city to get weather for",
#                 }
#             },
#             "required": ["city"],
#         },
#     },
#     {
#         "name": "get_forecast",
#         "description": "Get a 3-day forecast for a city",
#         "input_schema": {
#             "type": "object",
#             "properties": {
#                 "city": {
#                     "type": "string",
#                 }
#             },
#             "required": ["city"],
#         },
#     },
# ]


# run_tool is just a hardcoded lookup.
# In a real app, this would hit your database, an API, whatever.
# def run_tool(name, tool_input):
#     match name:
#         case "get_weather":
#             if tool_input["city"] == "austin":
#                 return f"Weather in {tool_input['city']}: 95F, sunny"
#             else:
#                 return f"Weather in {tool_input['city']}: 54F, snow flurries"
#         case "get_forecast":
#             if tool_input["city"] == "austin":
#                 return f"Weather in {tool_input['city']} for the next 3 days : 71F, 68F, and 77F"
#             else:
#                 return f"Weather in {tool_input['city']} for the next 3 days : 48F, 45F, and 52F"
#         case _:
#             raise ValueError(f"Unknown tool: {name}")


# messages = [
#     {
#         "role": "user",
#         "content": "I'm packing for a three-day trip to Denver. What's the weather today and over the next few days?",
#     }
# ]

# The agent loop. Each iteration sends messages to Claude
# and switches on the response's stop reason.
# while True:
#     response = client.messages.create(
#         model="claude-opus-5-5",
#         max_tokens=524,
#         tools=tools,
#         messages=messages,
#     )

#     print(f"Stop reason: {response.stop_reason}")

#     if response.stop_reason == "end_turn":
#         # Claude is done. Print the final text and break.
#         for block in response.content:
#             if block.type == "text":
#                 print(block.text)
#         break

#     elif response.stop_reason == "tool_use":
#         # Find the tool use blocks in the response and run each one.
#         tool_results = []
#         for block in response.content:
#             if block.type == "tool_use":
#                 result = run_tool(block.name, block.input)
#                 print(f"Tool call: {block.name} {block.input} -> {result}")
#                 tool_results.append(
#                     {
#                         "type": "tool_result",
#                         "tool_use_id": block.id,
#                         "content": result,
#                     }
#                 )

#         # Push the assistant's response and our tool results
#         # back into messages, then loop again so Claude can answer.
#         print(f" reponse format : {response.content}")
#         messages.append({"role": "assistant", "content": response.content})
#         messages.append({"role": "user", "content": tool_results})

#     else:
#         # Any other stop reason, such as max_tokens or refusal.
#         # Nothing in messages has changed, so stop here. Looping
#         # again would pay for the same request over and over.
#         print(f"Stopped early: {response.stop_reason}")
#         break


@beta_tool
def get_weather(location: str) -> str:
    """Get the current weather for a given location.

    Args:
        location: The city to get weather for
    Returns:
        A JSON-encoded string with the location, temperature, and weather condition.
    """
    if location.lower() == "austin":
        return json.dumps(
            {
                "location": location,
                "temperature": "78°F",
                "condition": "Sunny",
            }
        )
    else:
        return json.dumps(
            {"location": location, "temperature": "54F", "condition": "snow flurries"}
        )


@beta_tool
def get_forecast(location: str) -> str:
    """
    Get a 3-day forecast for a city

    Args:
        location: The city to get forecast for
    Returns:
        A JSON-encoded string with the location, temperature, and weather condition.
    """
    if location.lower() == "austin":
        return json.dumps(
            {
                "location": location,
                "forecast": ["71F", "68F", "77F"],
                "condition": "sunny",
            }
        )
    else:
        return json.dumps(
            {
                "location": location,
                "forecast": ["48F", "45F", "52F"],
                "condition": "warm",
            }
        )


# Use the tool_runner to automatically handle tool calls
runner = client.beta.messages.tool_runner(
    model="claude-opus-5-5",
    max_tokens=824,
    tools=[get_weather, get_forecast],
    messages=[
        {
            "role": "user",
            "content": "I'm packing for a three-day trip to Denver. What's the \
         weather today and over the next few days?",
        }
    ],
)

final_message = runner.until_done()
for block in final_message.content:
    if block.type == "text":
        print(block.text)
