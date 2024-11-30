import os
import json

from groq import Groq
from toolhouse import Toolhouse
from bs4 import BeautifulSoup
MODEL="llama3-70b-8192"

# Initialize Groq client (make sure you set up your GROQ_API_KEY in your environment)
client = Groq(api_key="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")

def searchSuperMarkets(location,lang):
    print('Starting search')
    print()
    th = Toolhouse(api_key='th--MZTludQ7gxl4B7kIhQmpBxHqdsi3KVFooCkINRoto4')
    messages = [{
    "role": "user",
    "content":
        f"Cerca in internet i supermercati a {location} (min 10)"

    }]
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        # Passes Code Execution as a tool
        tools=th.get_tools(),
    )
    
    print(response)
    print()
    tool_run = th.run_tools(response)
    print()
    print(tool_run)
    messages.extend(tool_run)
    print()
    messages.append({
        'role':'user',
        'content':'Genera SOLO una lista con risultati dettagliati in un formato JSON strutturato: {"{description: <description>, name: <name>, url: <link to the supermarket>}"}'
    })
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
    )
    print(response.choices[0].message.content)
    
if __name__ == "__main__":
    searchSuperMarkets('udine', 'italiano')