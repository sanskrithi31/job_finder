import os
from groq import Groq
client = Groq(api_key = "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")

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role":"user",
            "content" : "Please tell me about Lenovo in 100 lines."
        }
    ],
    model="llama-3.3-70b-versatile"
)

print(chat_completion.choices[0].message.content)