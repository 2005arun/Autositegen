import json
import os
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import AgentState
from utils.llm_client import PLANNING_MODEL, get_llm
from utils.parser import extract_json

# ============================================
# LLM-BASED INTENT CLASSIFIER
# ============================================
VALID_INTENTS = ["static_ui", "logic_basic", "crud_basic", "data_complex"]

INTENT_CLASSIFICATION_PROMPT = """You are an expert app classifier. Analyze the user's request and classify it into exactly ONE of these categories:

1. **static_ui** - Simple static pages with no interactivity
   Examples: portfolio, landing page, resume, about me, blog, company website, personal website
   
2. **logic_basic** - Apps with computation/logic but no data persistence
   Examples: calculator, unit converter, BMI calculator, quiz, counter, flames game, tip calculator
   
3. **crud_basic** - Apps that create, read, update, delete data (stored in state)
   Examples: todo list, budget tracker, expense tracker, notes app, task manager, shopping list, contact form, booking form
   
4. **data_complex** - Apps with complex data display, filtering, or multiple views
   Examples: food ordering app, e-commerce store, restaurant menu, product catalog, dashboard, analytics, data visualization

RULES:
- Respond with ONLY the category name (one of: static_ui, logic_basic, crud_basic, data_complex)
- No explanation, no punctuation, just the category name
- If unsure, choose the simpler category
- Consider what STATE and INTERACTIVITY the app needs

User Request: {prompt}

Category:"""


def classify_app_intent(prompt: str) -> str:
    """
    Classifies user prompt into an app intent level using LLM.
    Falls back to static_ui if classification fails.
    """
    try:
        llm = get_llm(PLANNING_MODEL)
        messages = [
            SystemMessage(content="You are a precise app classifier. Respond with only the category name."),
            HumanMessage(content=INTENT_CLASSIFICATION_PROMPT.format(prompt=prompt))
        ]
        
        response = llm.invoke(messages)
        intent = response.content.strip().lower().replace(".", "").replace(",", "")
        
        # Validate the response
        if intent in VALID_INTENTS:
            print(f"LLM classified intent: {intent}")
            return intent
        else:
            # Try to extract valid intent from response
            for valid_intent in VALID_INTENTS:
                if valid_intent in intent:
                    print(f"LLM classified intent (extracted): {valid_intent}")
                    return valid_intent
            
            print(f"LLM returned invalid intent '{intent}', defaulting to static_ui")
            return "static_ui"
            
    except Exception as e:
        print(f"Intent classification failed: {e}, defaulting to static_ui")
        return "static_ui"

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

    llm = get_llm(PLANNING_MODEL)
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

