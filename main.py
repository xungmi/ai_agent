import os
from dotenv import load_dotenv
import google.generativeai as genai

def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("⚠️ GEMINI_API_KEY is not configured in .env")
    genai.configure(api_key=api_key)
    
    user_topic = input("Topic of X post: ")
    
    prompt = f"""
    You are an expert social media manager.
    Write a short, engaging X (formerly Twitter) post about the following topic.
    Keep it concise, avoid hashtags, use max 1–2 emojis, and format with line breaks if needed.

    <TOPIC>
    {user_topic}
    </TOPIC>
    """

    model = genai.GenerativeModel("gemini-1.5-flash") 

    response = model.generate_content(prompt)

    print("\n✅ X Post Generated:")
    print(response.text)

if __name__ == "__main__":
    main()
