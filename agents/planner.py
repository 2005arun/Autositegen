import json
import os
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import AgentState
from utils.llm_client import get_llm
from utils.parser import extract_json

# ============================================
# RULE-BASED INTENT CLASSIFIER (NOT LLM)
# ============================================
def classify_app_intent(prompt: str) -> str:
    """
    Classifies user prompt into an app intent level.
    This is RULE-BASED, not LLM-based, for reliability.
    """
    prompt = prompt.lower()

    if any(k in prompt for k in ["calculator", "flames", "counter", "converter", "quiz"]):
        return "logic_basic"

    if any(k in prompt for k in ["budget", "todo", "planner", "tracker", "expense", "task", "note", "list"]):
        return "crud_basic"

    if any(k in prompt for k in ["food", "ecommerce", "zomato", "shop", "store", "order", "restaurant"]):
        return "data_complex"

    if any(k in prompt for k in ["portfolio", "landing", "website", "blog", "resume", "about me"]):
        return "static_ui"

    return "static_ui"  # Default to simplest

# ============================================
# DEFAULT BLUEPRINTS PER INTENT LEVEL
# ============================================
DEFAULT_BLUEPRINTS = {
    "static_ui": {
        "features": ["display content", "navigation"],
        "state": [],
        "ui": ["hero section", "content sections", "footer"],
        "forbidden": ["auth", "charts", "backend", "complex router"]
    },
    "logic_basic": {
        "features": ["input handling", "calculation", "result display"],
        "state": ["inputValue", "result"],
        "ui": ["input form", "calculate button", "result display"],
        "forbidden": ["auth", "charts", "backend"]
    },
    "crud_basic": {
        "features": ["add item", "list items", "delete item", "calculate total"],
        "state": ["items", "inputValue"],
        "ui": ["form", "list or table", "summary card"],
        "forbidden": ["auth", "charts", "backend", "complex router"]
    },
    "data_complex": {
        "features": ["list data", "filter data", "detail view", "cart/selection"],
        "state": ["items", "selectedItem", "cart"],
        "ui": ["card grid", "filter bar", "detail modal", "summary"],
        "forbidden": ["auth", "real backend"]
    }
}

def planner_agent(state: AgentState) -> AgentState:
    print("--- PLANNER AGENT ---")
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "planner_prompt.txt")
    with open(prompt_path, "r") as f:
        system_prompt = f.read()

    user_input = state["user_prompt"]
    
    # STEP 1: Rule-based Intent Classification
    app_intent = classify_app_intent(user_input)
    print(f"App Intent: {app_intent}")
    
    # STEP 2: Get Default Blueprint for this intent
    default_blueprint = DEFAULT_BLUEPRINTS.get(app_intent, DEFAULT_BLUEPRINTS["static_ui"])
    
    # STEP 3: Build context for LLM
    intent_context = f"""
APP INTENT LEVEL: {app_intent}

DEFAULT BLUEPRINT:
- Features: {', '.join(default_blueprint['features'])}
- State Variables: {', '.join(default_blueprint['state']) if default_blueprint['state'] else 'None required'}
- UI Elements: {', '.join(default_blueprint['ui'])}
- FORBIDDEN (do NOT include): {', '.join(default_blueprint['forbidden'])}

IMPORTANT: Only implement the features above. Do NOT add authentication, charts, or backend unless explicitly requested.
"""
    
    # Load custom blueprints (for specific app types like calculator)
    blueprints_dir = os.path.join(os.path.dirname(__file__), "..", "blueprints")
    blueprints = {}
    if os.path.exists(blueprints_dir):
        for f_name in os.listdir(blueprints_dir):
            if f_name.endswith(".json"):
                with open(os.path.join(blueprints_dir, f_name), "r") as bf:
                    blueprints[f_name.replace(".json", "")] = bf.read()

    llm = get_llm()
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"User Request: {user_input}\n\n{intent_context}\n\nAvailable Blueprints: {json.dumps(blueprints, indent=2)}")
    ]
    
    response = llm.invoke(messages)
    plan = extract_json(response.content)
    
    # Inject app_intent into the plan for downstream agents
    plan["app_intent"] = app_intent
    plan["default_blueprint"] = default_blueprint
    
    return {"plan": plan}

