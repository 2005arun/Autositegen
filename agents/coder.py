import os
import json
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import AgentState
from utils.llm_client import get_llm
from utils.parser import extract_json

def coder_agent(state: AgentState) -> AgentState:
    print("--- CODER AGENT ---")
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "coder_prompt.txt")
    with open(prompt_path, "r") as f:
        system_prompt = f.read()

    architecture = state["architecture"]
    plan = state.get("plan", {})
    
    # Load blueprint if selected
    blueprint_content = ""
    if "blueprint" in plan and plan["blueprint"] != "custom":
        blueprint_path = os.path.join(os.path.dirname(__file__), "..", "blueprints", f"{plan['blueprint']}.json")
        if os.path.exists(blueprint_path):
            with open(blueprint_path, "r") as f:
                blueprint_content = f.read()

    llm = get_llm()
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Architecture: {json.dumps(architecture, indent=2)}\n\nBlueprint: {blueprint_content}")
    ]
    
    response = llm.invoke(messages)
    code = extract_json(response.content)
    
    return {"code": code}
