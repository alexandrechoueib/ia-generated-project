import os
import sys
from xai_sdk import Client
from xai_sdk.chat import user

argv = sys.argv[1:]

print(argv)

def grok(model:str, content:str) -> str:
    client = Client(api_key=os.getenv("XAI_API_KEY"))
    chat = client.chat.create(model="grok-4-6")
    chat.append(user(msg))
    return chat.sample().content



