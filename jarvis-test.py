import openai
import requests
import json

import os
from dotenv import load_dotenv

load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")

OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

client = openai.OpenAI(
    base_url=OPENAI_BASE_URL,
    api_key=OPENAI_API_KEY,
)


class ConversationHistory:
    def __init__(self):
        self.history = []

    def save_message(self, message, role, tool_call_id=False):
        if tool_call_id:
            history_item = {"role": role, "content": str(message), "tool_call_id": tool_call_id}
        else:
            history_item = {"role": role, "content": str(message)}
        self.history.append(history_item)
        
    def save_tool_call(self, tool_call_response):
        self.history.append(tool_call_response)
    def get_history(self):
        return self.history

    def clear_history(self):
        self.history = []


history = ConversationHistory()


def get_current_weather(location):
    # print(location)
    
    url = (
        f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHERMAP_API_KEY}"
    )
    response = requests.get(url)
    data = response.json()

    # Extract the temperature in Kelvin
    kelvin_temp = data["main"]["temp"]

    # Convert Kelvin to Celsius
    celsius_temp = kelvin_temp - 273.15

    return f"location: {location} temperature: {round(celsius_temp, 2)}"


def chat(message = None):

    if message != None:
        history.save_message(message, "user")

    messages = history.get_history()
    
    print(messages)

    response = (
        client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "get_current_weather",
                        "description": "Get the current weather in a given location",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "The city and state, e.g. San Francisco, CA",
                                },
                            },
                            "required": ["location"],
                        },
                    },
                }
            ],
        )
        .choices[0]
        .message
    )

    # print(response)
    
    responseContent = response.content

    if response.tool_calls:
        history.save_tool_call(response)

        available_functions = {
            "get_current_weather": get_current_weather,
        }

        tool = response.tool_calls[0]
        function_to_call = available_functions[tool.function.name]
        function_response = function_to_call(
            json.loads(tool.function.arguments)["location"]
        )
        
        history.save_message(function_response, "tool", tool.id)

        chat()

    history.save_message(responseContent, "assistant")

    return responseContent


while True:
    user_message = input("User: ")

    if user_message.lower() == "quit" or user_message.lower() == "exit":
        break

    response = chat(user_message)

    print(f"LLM: {response}")
