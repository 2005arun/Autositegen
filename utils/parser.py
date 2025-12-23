import json
import re

def extract_json(text: str) -> dict:
    """
    Extracts JSON from a string, handling markdown code blocks.
    """
    text = text.strip()
    
    # Try to find JSON block
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        text = match.group(1)
    else:
        # Look for just { ... }
        match = re.search(r"(\{.*\})", text, re.DOTALL)
        if match:
            text = match.group(1)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Attempt to fix common JSON issues
        # 1. Fix unescaped newlines in strings
        # This is a naive fix and might not work for all cases
        try:
            # Remove control characters
            text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
            return json.loads(text)
        except:
            pass
            
        print(f"FAILED TO PARSE JSON. Raw text:\n{text}\n")
        raise ValueError(f"Could not extract JSON from text.")
