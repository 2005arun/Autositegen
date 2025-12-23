import json
import os
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import AgentState
from utils.llm_client import get_llm
from utils.parser import extract_json

def planner_agent(state: AgentState) -> AgentState:
    print("--- PLANNER AGENT ---")
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "planner_prompt.txt")
    with open(prompt_path, "r") as f:
        system_prompt = f.read()

    user_input = state["user_prompt"]
    
    # Load blueprints
    blueprints_dir = os.path.join(os.path.dirname(__file__), "..", "blueprints")
    blueprints = {}
    if os.path.exists(blueprints_dir):
        for f in os.listdir(blueprints_dir):
            if f.endswith(".json"):
                with open(os.path.join(blueprints_dir, f), "r") as bf:
                    blueprints[f.replace(".json", "")] = bf.read()
    
    llm = get_llm()
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"User Request: {user_input}\n\nAvailable Blueprints: {json.dumps(blueprints, indent=2)}")
    ]
    
    response = llm.invoke(messages)
    plan = extract_json(response.content)
    
    return {"plan": plan}
