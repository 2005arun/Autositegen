import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

PLANNING_MODEL = "openai/gpt-oss-20b"
CODING_MODEL = "openai/gpt-oss-120b"


def get_llm(model: str = CODING_MODEL):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("Warning: GROQ_API_KEY not found in environment variables.")
    
    return ChatGroq(
        model=model,
        temperature=0,
        max_retries=5,
        request_timeout=60,
        max_tokens=12000,
    )