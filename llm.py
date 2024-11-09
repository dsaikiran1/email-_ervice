import os
import requests
from dotenv import load_dotenv
from groq import Groq
from openai import api_key
import json

load_dotenv()  # Load environment variables

LLM_API_KEY = os.getenv("LLM_API_KEY")
dic = {
    "name":"ishita",
    "work":"data base administrator",
    "speciality":"astronaut",
    "age":89
}
def chat_complete(message,dic):
    dic['base_prompt'] = message
    dict_str = json.dumps(dic)

    client = Groq(
        api_key=os.environ.get('LLM_API_KEY'),
    )
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role":"user",
                "content":dict_str
            }
        ],
        model="mixtral-8x7b-32768",
    )
    return chat_completion.choices[0].message.content
