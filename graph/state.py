from typing import TypedDict, Dict, Any, Optional

class AgentState(TypedDict):
    user_prompt: str
    plan: Dict[str, Any]
    architecture: Dict[str, Any]
    code: Dict[str, str]  # Filename -> Content
    validation: Dict[str, Any]
