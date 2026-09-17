import json
import re

def extract_json(text: str) -> dict:
    """
    Extracts JSON from a string, handling markdown code blocks.
    """
    text = text.strip()
    
    decoder = json.JSONDecoder()
    candidates = [text]
    if "```" in text:
        for block in text.split("```")[1::2]:
            block = block.strip()
            block = re.sub(r"^(json|javascript|js)\s*\r?\n", "", block, flags=re.IGNORECASE)
            candidates.append(block)

    for candidate in candidates:
        candidate = candidate.strip()
        try:
            value, _ = decoder.raw_decode(candidate)
            if isinstance(value, dict):
                return value
        except json.JSONDecodeError:
            pass

        for index, character in enumerate(candidate):
            if character != "{":
                continue
            try:
                value, _ = decoder.raw_decode(candidate[index:])
                if isinstance(value, dict):
                    return value
            except json.JSONDecodeError:
                continue

    raise ValueError("Could not extract a valid JSON object from model output.")
