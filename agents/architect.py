import os
import json
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import AgentState
from utils.llm_client import get_llm
from utils.parser import extract_json

def architect_agent(state: AgentState) -> AgentState:
    print("--- ARCHITECT AGENT ---")
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "architect_prompt.txt")
    with open(prompt_path, "r") as f:
        system_prompt = f.read()

    plan = state["plan"]
    
    llm = get_llm()
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Project Plan: {json.dumps(plan, indent=2)}")
    ]
    
    response = llm.invoke(messages)
    architecture = extract_json(response.content)
    
    return {"architecture": architecture}
