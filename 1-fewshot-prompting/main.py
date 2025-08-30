import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai

# --- Setup logging ---
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)


def load_api_key() -> str:
    logging.info("🔑 Loading API key...")
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logging.error("🔴 GEMINI_API_KEY not found in .env")
        raise ValueError("⚠️ GEMINI_API_KEY is not configured in .env")
    logging.info("🟢 API key loaded successfully")
    return api_key


def configure_genai(api_key: str):
    logging.info("⚙️ Configuring Gemini client...")
    genai.configure(api_key=api_key)
    logging.info("🟢 Gemini client configured")


def get_user_topic() -> str:
    logging.info("📝 Asking user for topic...")
    topic = input("Topic of X post: ")
    logging.info(f"📦 User topic received: {topic}")
    return topic


def build_prompt(user_topic: str) -> str:
    logging.info("🛠️ Building prompt...")
    prompt = f"""
    You are an expert social media manager.
    Write a short, engaging X (formerly Twitter) post about the following topic.
    Keep it concise, avoid hashtags, use max 1–2 emojis, and format with line breaks if needed.

    Here are some examples (topic → generated post):

    <example>
      <topic>AI transforms healthcare</topic>
      <generated-post>AI is reshaping healthcare 🏥 Faster diagnoses, smarter hospitals, and better treatments.</generated-post>
    </example>

    <example>
      <topic>Remote work is the new normal</topic>
      <generated-post>Work from anywhere 🌍 Remote work is here to stay, bringing flexibility and global collaboration.</generated-post>
    </example>

    Please use the tone, structure, and style of the examples above 
    (but not the content) to generate a new post for the topic below.

    <TOPIC>
    {user_topic}
    </TOPIC>
    """
    logging.info("🟢 Prompt built successfully")
    return prompt


def generate_post(prompt: str) -> str:
    logging.info("🚀 Sending request to Gemini API...")
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    logging.info("🟢 Response received from Gemini API")
    return response.text


def main():
    logging.info("🚀 Starting X post generator workflow...")
    api_key = load_api_key()
    configure_genai(api_key)

    user_topic = get_user_topic()
    prompt = build_prompt(user_topic)
    post = generate_post(prompt)

    logging.info("✅ X Post Generated:")
    print(post)  # vẫn print kết quả cuối cho dễ copy


if __name__ == "__main__":
    main()
