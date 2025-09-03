import json
import sys
import os
import sqlite3
import google.generativeai as genai

from pypdf import PdfReader
from dotenv import load_dotenv
import requests
import logging
from pydantic import BaseModel, Field


# --- Setup logging ---
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)


# ========== Gemini ==========
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


def load_file(path: str) -> str:
    if not os.path.exists(path):
        logging.error(f"🔴 Error: The file '{path}' does not exist.")
        sys.exit(1)

    logging.info("Loading file: %s", path)
    with open(path, 'r', encoding='utf-8') as file:
        return file.read()


def save_file(path: str, content: str) -> None:
    logging.info("Saving file: %s", path)
    with open(path, 'w', encoding='utf-8') as file:
        file.write(content)
        
        
def generate_article_draft(outline: str, existing_draft: str | None = None, feedback: str | None = None) -> str:
    logging.info("Generating article draft...")
    example_posts_path = "example_posts"

    if not os.path.exists(example_posts_path):
        raise FileNotFoundError(
            f"The directory '{example_posts_path}' does not exist.")
        
    example_posts = []
    for filename in os.listdir(example_posts_path):
        if filename.lower().endswith(".md") or filename.lower().endswith(".mdx"):
            with open(os.path.join(example_posts_path, filename), 'r', encoding='utf-8') as file:
                example_posts.append(file.read())
    
    if not example_posts:
        raise ValueError("No example blog posts found in the 'example_posts' directory.")
    
    example_posts_str = "\n\n".join(
        f"<example-post-{i+1}>\n{post}\n</example-post-{i+1}>"
        for i, post in enumerate(example_posts)
    )
    
    prompt = f"""
                Write a detailed blog post based on the following outline:

                <outline>
                {outline}
                </outline>

                Below are some example blog posts I wrote in the past:
                <example-posts>
                {example_posts_str}
                </example-posts>

                Use the language, tone, style and way of writing from the example posts to generate your draft for the new blog post.
                DON'T use the content from those example posts!

                Return the blog post draft in raw markdown format so that I can directly use it in my markdown-processing pipeline.
                Don't add any additional text or explanations, just return the raw markdown content.
            """
            
    if existing_draft and feedback:
        example_posts_str += f"\n\n<existing-draft>\n{existing_draft}\n</existing-draft>"
        example_posts_str += f"\n\n<feedback>\n{feedback}\n</feedback>"

        prompt = f"""
            Write an improved version of the following blog post draft:

            <existing-draft>
            {existing_draft}
            </existing-draft>

            The following feedback should be taken into account when writing the improved draft:

            <feedback>
            {feedback}
            </feedback>

            The original draft AND your improved version should be based on the following outline:

            <outline>
            {outline}
            </outline>

            Below are some example blog posts I wrote in the past:
            <example-posts>
            {example_posts_str}
            </example-posts>

            Use the language, tone, style and way of writing from the example posts to generate your draft for the new blog post.
            DON'T use the content from those example posts!

            Return the blog post draft in raw markdown format so that I can directly use it in my markdown-processing pipeline.
            Don't add any additional text or explanations, just return the raw markdown content.
        """
        
    
    
            
    
    
        
        

    logging.info("Example posts loaded successfully")
    return example_posts


def main():
    
    api_key = load_api_key()
    configure_genai(api_key)
    
    if len(sys.argv) != 2:
        print("Usage: python main.py <outline_file>")
        sys.exit(1)

    outline_file = sys.argv[1]
    outline = load_file(outline_file)

    blog_post_draft = generate_article_draft(outline)
    print("Generated blog post draft:")
    print(blog_post_draft)

    thumbnail_image = generate_thumbnail(blog_post_draft)
    thumbnail_file = outline_file.replace(".txt", "_thumbnail.jpeg")
    with open(thumbnail_file, "wb") as f:
        f.write(thumbnail_image)
    print(f"Thumbnail saved to '{thumbnail_file}'.")

    output_file = outline_file.replace(".txt", "_draft.md")
    save_file(output_file, blog_post_draft)
    print(f"Blog post draft saved to '{output_file}'.")


if __name__ == "__main__":
    main()