import os
import requests
from dotenv import load_dotenv
from llm import chat_complete
load_dotenv()  # Load environment variables

LLM_API_KEY = os.getenv("LLM_API_KEY")

def generate_content(base_prompt, row_data):
    """Generate customized content using an LLM API based on the provided prompt and row data."""
    # Build a full prompt that combines the base prompt and row-specific data
    row_details = "\n".join([f"{key}: {value}" for key, value in row_data.items()])


    if row_details:
        return chat_complete(base_prompt,row_data)
    else:
        print("Error generating content with LLM API.")
        return base_prompt  # Fallback to the input prompt if API fails

def create_custom_message(template, row_data):
    """Fill placeholders in the template with actual values from row_data."""
    try:
        return template.format(**row_data)
    except KeyError as e:
        print(f"Placeholder error: {e} not found in the row data.")
        return template  # Fallback to the unformatted template if an error occurs
