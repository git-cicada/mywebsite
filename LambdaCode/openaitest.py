from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

def generate_quote(api_key: str) -> str:
    """Generate a daily quote using OpenAI"""
    client = OpenAI(api_key=api_key)
    
    prompt = "Give me an inspiring motivational quote for the day. Keep it short and positive."

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # cheaper & fast
        messages=[{"role": "user", "content": prompt}],
        max_tokens=50,
        temperature=0.8
    )

    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set.")
    print("Generating quote...")
    quote = generate_quote(api_key)
    print("Quote of the Day:")
    print(quote)