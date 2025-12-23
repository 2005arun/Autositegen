import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("Warning: GROQ_API_KEY not found in environment variables.")
    
    # Added max_retries to handle rate limits automatically
    return ChatGroq(
        model="llama-3.3-70b-versatile", 
        temperature=0,
        max_retries=5,
        request_timeout=60
    )
