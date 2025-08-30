import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai
import requests


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

    
def get_html_from_website(url: str) -> str:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Error fetching the URL {url}: {e}")
        return ""


def extract_core_website_content(html: str) -> str:
    logging.info("🚀 Sending request to Gemini API...")
    prompt = f"""
        You are an expert web content extractor. Your task is to extract the core content from a given HTML page.
        The core content should be the main text, excluding navigation, footers, and other non-essential elements like scripts etc.

        Here is the HTML content:
        <html>
        {html}
        </html>

        Please extract the core content and return it as plain text.
    """
    
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    logging.info("🟢 Response received from Gemini API")
    return response.text


def summarize_content(content: str) -> str:
    prompt = f"""
    You are an expert summarizer. Your task is to summarize the provided content into a concise and clear summary.

    Here is the content to summarize:
    <content>
    {content}
    </content>

    Please provide a brief summary of the main points in the content in Vietnamese language. Prefer bullet points and avoid unncessary explanations.
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    logging.info("🟢 Response received from Gemini API")
    return response.text

def generate_x_post(summary: str) -> str:
    prompt = f"""
    You are an expert content creator. Your task is to generate a social media post based on the provided summary.

    Here is the summary to base the post on:
    <summary>
    {summary}
    </summary>

    Please create a catchy and engaging social media post in Vietnamese language.
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    logging.info("🟢 Response received from Gemini API")
    return response.text

def main():
    api_key = load_api_key()
    configure_genai(api_key)
    
    website_url = input("Website URL: ")
    logging.info("🚀 Fetching website HTML...")
    try:
        html_content = get_html_from_website(website_url)
        logging.info("🟢 Website HTML fetched successfully.")
    except Exception as e:
        logging.error(f"🔴 An error occurred while fetching the website: {e}")
        return

    if not html_content:
        logging.error("🔴 Failed to fetch the website content. Exiting.")
        return

    logging.info("🚀 Extracting core content from the website...")
    core_content = extract_core_website_content(html_content)
    logging.info("🟢 Core content extracted successfully.")

    logging.info("🚀 Summarizing the core content...")
    summary = summarize_content(core_content)
    logging.info("🟢 Summary generated successfully.")
    logging.info(summary)

    logging.info("🚀 Generating X post based on the summary...")
    x_post = generate_x_post(summary)
    logging.info("🟢 X post generated successfully.")
    x_post_file = "generated_x_post.txt"
    with open(x_post_file, "w", encoding="utf-8") as f:
        f.write(x_post)
    logging.info(f"🟢 X Post saved to {x_post_file}")

if __name__ == "__main__":
    main()
# https://vietnamnet.vn/dan-xe-phao-quan-su-khung-hung-huc-khi-the-trong-buoi-tong-duyet-dieu-binh-2437891.html