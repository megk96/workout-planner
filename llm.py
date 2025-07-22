import os
import requests
from prompts import workout_email_prompt
from dotenv import load_dotenv
load_dotenv()
GROQ_API_URL = os.getenv("GROQ_API_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DEFAULT_MODEL = "llama-3.3-70b-versatile"

def query_groq(prompt: str, model: str = DEFAULT_MODEL) -> str:
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a friendly fitness assistant writing motivational daily workout emails.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.7,
        "max_tokens": 500,
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=payload)
    
    # Debug
    print("📨 Groq response:", response.status_code, response.text)

    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]




def compose_email(workout):
    prompt = workout_email_prompt(workout)
    text = query_groq(prompt)
    return {
        "subject": f"Day {workout['day_number']}: {workout['title']}",
        "body": text.strip()
    }
