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
        self.long_term_memory_file = "longTermMemory.json"
        self.load_long_term_memory()
        
        self.history = self.long_term_memory.copy()
        
        self.memory_items = 0

    # def refresh_memory(self):
    #     self.history.pop(len(self.long_term_memory) + 1)
            
    def load_long_term_memory(self):
        if os.path.exists(self.long_term_memory_file):
            with open(self.long_term_memory_file, "r") as file:
                self.long_term_memory = json.load(file)
        else:
            self.long_term_memory = []

    def save_long_term_memory(self):
        with open(self.long_term_memory_file, "w") as file:
            json.dump(self.long_term_memory, file)

    def save_message_forever(self, message, role):
        history_item = {"role": role, "content": str(message)}
        self.long_term_memory.append(history_item)
        self.save_long_term_memory()
        
        return f"Remembered: {message}"

    def save_message(self, message, role):
        history_item = {"role": role, "content": str(message)}
        self.history.append(history_item)
        
        self.memory_items += 1
        
    def get_history(self):
        return self.history

    def clear_history(self):
        self.history = []


history = ConversationHistory()


def get_current_weather(location):
    
    url = (
        f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHERMAP_API_KEY}"
    )
    response = requests.get(url)
    data = response.json()

    # Extract the temperature in Kelvin
    kelvin_temp = data["main"]["temp"]

    # Convert Kelvin to Celsius
    celsius_temp = kelvin_temp - 273.15

    return f"The temperature in: {location} is: {round(celsius_temp, 2)}"


def chat(message = None):

    if message != None:
        history.save_message(message, "user")

    messages = history.get_history()

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
                },
                 {
                    "type": "function",
                    "function": {
                        "name": "remember_data",
                        "description": "Save data to long term memory when asked to remember something",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "memory": {
                                    "type": "string",
                                    "description": "What to remember, e.g 'Remember that i like ice cream'",
                                },
                            },
                            "required": ["memory"],
                        },
                    },
                }
            ],
        )
        .choices[0]
    )

    if response.message.content is not None:
        responseContent = response.message.content
        history.save_message(responseContent, "assistant")
    elif response.message.tool_calls:

        available_functions = {
            "get_current_weather": get_current_weather,
            "remember_data": history.save_message_forever
        }

        tool = response.message.tool_calls[0]
        function_to_call = available_functions[tool.function.name]
        if tool.function.name == "get_current_weather":
            function_response = function_to_call(
                json.loads(tool.function.arguments)["location"]
            )
        elif tool.function.name == "remember_data":
            function_response = function_to_call(
                json.loads(tool.function.arguments)["memory"], "assistant"
            )
        
        history.save_message(function_response, "assistant")
        responseContent = function_response
    else:
        responseContent = "No response available"
        history.save_message(responseContent, "assistant")

    return responseContent


while True:
    user_message = input("User: ")

    if user_message.lower() == "quit" or user_message.lower() == "exit":
        break

    response = chat(user_message)

    print(f"LLM: {response}")