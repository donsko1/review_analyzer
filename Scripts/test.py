from pathlib import Path
import json
import pandas as pd
from openai import OpenAI
from typing import List, Dict
from Configs import AI_TOKEN


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=AI_TOKEN
)

model = "deepseek/deepseek-chat"
system_prompt = "Ты учитель начальных классов. Отвечай так, чтобы все было понятно даже детям"
completion = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Что такое суперпозиция в квантовой физике?"}
    ]
)
print(completion.choices[0].message.content)