import os
import json
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import AgentState
from utils.llm_client import get_llm
from utils.parser import extract_json

# ============================================
# INTENT-AWARE VALIDATION RULES
# ============================================
VALIDATION_RULES = {
    "static_ui": {
        "require_useState": False,
        "require_onClick": False,
        "require_map": False,
        "require_tailwind": True,
        "skip_llm_validation": True
    },
    "logic_basic": {
        "require_useState": True,
        "require_onClick": True,
        "require_map": False,
        "require_tailwind": True,
        "skip_llm_validation": True
    },
    "crud_basic": {
        "require_useState": True,
        "require_onClick": True,
        "require_map": True,
        "require_tailwind": True,
        "skip_llm_validation": True
    },
    "data_complex": {
        "require_useState": True,
        "require_onClick": True,
        "require_map": True,
        "require_tailwind": True,
        "skip_llm_validation": False
    }
}

def validator_agent(state: AgentState) -> AgentState:
    print("--- VALIDATOR AGENT ---")
    
    code = state["code"]
    plan = state.get("plan", {})
    
    # Get app intent from plan (set by Planner)
    app_intent = plan.get("app_intent", "static_ui")
    rules = VALIDATION_RULES.get(app_intent, VALIDATION_RULES["static_ui"])
    
    print(f"Validating for intent: {app_intent}")
    
    # ============================================
    # 1. Check for Critical Source Files (AI-generated only)
    # NOTE: package.json, vite.config.js, index.html are from template - DO NOT CHECK
    # ============================================
    if "src/App.jsx" not in code and "src/App.tsx" not in code:
        print("Validation Failed: Missing src/App.jsx")
        return {
            "validation": {
                "status": "fail",
                "issues": ["Missing src/App.jsx"],
                "suggested_fixes": ["Generate src/App.jsx"]
            }
        }

    # ============================================
    # 2. Check for Export Style (Mandatory Default Exports)
    # ============================================
    for path, content in code.items():
        if path.endswith(".jsx") or path.endswith(".tsx"):
            if "export default" not in content:
                print(f"Validation Failed: {path} does not use export default")
                return {
                    "validation": {
                        "status": "fail",
                        "issues": [f"{path} does not use export default"],
                        "suggested_fixes": [f"Change {path} to use export default"]
                    }
                }
            if "export {" in content:
                print(f"Validation Failed: {path} uses named exports")
                return {
                    "validation": {
                        "status": "fail",
                        "issues": [f"{path} uses named exports (forbidden)"],
                        "suggested_fixes": [f"Change {path} to use export default"]
                    }
                }
            # Syntax Check: Unmatched Braces
            if content.count("{") != content.count("}"):
                print(f"Validation Failed: {path} has unmatched braces")
                return {
                    "validation": {
                        "status": "fail",
                        "issues": [f"{path} has unmatched braces (syntax error)"],
                        "suggested_fixes": [f"Fix syntax in {path}"]
                    }
                }

    # ============================================
    # 3. Tailwind Usage (Always Required)
    # ============================================
    combined_code = "".join([content for filename, content in code.items() if filename.endswith(".jsx") or filename.endswith(".tsx")])
    
    if rules["require_tailwind"]:
        if "className=" not in combined_code:
            print("Validation Failed: No Tailwind classes found — UI not styled")
            return {
                "validation": {
                    "status": "fail",
                    "issues": ["No Tailwind classes found — UI not styled"],
                    "suggested_fixes": ["Add className attributes with Tailwind classes"]
                }
            }

        if "bg-" not in combined_code and "flex" not in combined_code and "grid" not in combined_code:
            print("Validation Failed: Layout and background styles missing")
            return {
                "validation": {
                    "status": "fail",
                    "issues": ["Layout and background styles missing (no bg-, flex, or grid classes)"],
                    "suggested_fixes": ["Add layout (flex/grid) and background colors"]
                }
            }

    # ============================================
    # 4. Intent-Specific Logic Checks
    # ============================================
    if rules["require_useState"] and "useState" not in combined_code:
        print(f"Validation Failed: {app_intent} app requires useState")
        return {
            "validation": {
                "status": "fail",
                "issues": [f"{app_intent} app requires useState for state management"],
                "suggested_fixes": ["Add useState hooks for managing state"]
            }
        }

    if rules["require_onClick"] and "onClick" not in combined_code:
        print(f"Validation Failed: {app_intent} app requires onClick handlers")
        return {
            "validation": {
                "status": "fail",
                "issues": [f"{app_intent} app requires onClick handlers for interactivity"],
                "suggested_fixes": ["Add onClick handlers to interactive elements"]
            }
        }

    if rules["require_map"] and "map(" not in combined_code and ".map(" not in combined_code:
        print(f"Validation Failed: {app_intent} app requires map() for rendering lists")
        return {
            "validation": {
                "status": "fail",
                "issues": [f"{app_intent} app requires map() for rendering lists"],
                "suggested_fixes": ["Use map() to render lists of items"]
            }
        }

    # ============================================
    # 5. Skip LLM Validation for Simple Apps
    # ============================================
    if rules["skip_llm_validation"]:
        print(f"Skipping LLM validation for {app_intent} app — all checks passed.")
        return {"validation": {"status": "pass", "issues": [], "suggested_fixes": {}}}

    # ============================================
    # 6. LLM-based Validation (Only for Complex Apps)
    # ============================================
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "validator_prompt.txt")
    with open(prompt_path, "r") as f:
        system_prompt = f.read()

    llm = get_llm()
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Project Plan: {json.dumps(plan, indent=2)}\n\nGenerated Code: {json.dumps(code, indent=2)}")
    ]
    
    response = llm.invoke(messages)
    validation_result = extract_json(response.content)
    
    print(f"Validation Status: {validation_result.get('status')}")
    
    return {"validation": validation_result}
