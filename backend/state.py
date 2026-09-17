from typing import Any, Dict, TypedDict


class AgentState(TypedDict, total=False):
    user_prompt: str
    plan: Dict[str, Any]
    architecture: Dict[str, Any]
    code: Dict[str, str]
    validation: Dict[str, Any]
    attempt: int
