Jarvis
This project contains the code for a Python project that aims to create a Jarvis-like AI assistant capable of accessing a user's calendar, providing advice, and displaying real-time world data.

To address concerns about storing every single word exchanged with the large language model (LLM) forever, I have implemented a persistent storage method. This method enables the LLM to determine whether a user's input should be saved permanently. If storage is necessary, the prompts are saved to a JSON file, which is later used to update the LLM's "memory." Non-persistent information is stored in a variable with a limited capacity of X prompts, preventing potential memory issues when using the model continuously for extended periods.

About the Developer
I am developing this project in my spare time as a working student. Although my availability is limited, I strive to contribute as much as possible.
