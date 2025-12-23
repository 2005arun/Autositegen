import os
import json
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import AgentState
from utils.llm_client import get_llm
from utils.parser import extract_json

def validator_agent(state: AgentState) -> AgentState:
    print("--- VALIDATOR AGENT ---")
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "validator_prompt.txt")
    with open(prompt_path, "r") as f:
        system_prompt = f.read()

    code = state["code"]
    
    # 1. Check for Critical Source Files
    if "src/App.jsx" not in code and "src/App.tsx" not in code:
        print("Validation Failed: Missing src/App.jsx")
        return {
            "validation": {
                "status": "fail",
                "issues": ["Missing src/App.jsx"],
                "suggested_fixes": ["Generate src/App.jsx"]
            }
        }

    # 3. Check for Export Style (Mandatory Default Exports)
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

    # 2. Check for Tailwind Usage (Strict Style Validation)
    combined_code = "".join([content for filename, content in code.items() if filename.endswith(".jsx") or filename.endswith(".tsx")])
    
    if "className=" not in combined_code:
        print("Validation Failed: No Tailwind classes found — UI not styled")
        return {
            "validation": {
                "status": "fail",
                "issues": ["No Tailwind classes found — UI not styled"],
                "suggested_fixes": ["Add className attributes with Tailwind classes"]
            }
        }

    # Stricter check for layout/backgrounds
    if "bg-" not in combined_code and "flex" not in combined_code and "grid" not in combined_code:
        print("Validation Failed: Layout and background styles missing")
        return {
            "validation": {
                "status": "fail",
                "issues": ["Layout and background styles missing (no bg-, flex, or grid classes)"],
                "suggested_fixes": ["Add layout (flex/grid) and background colors"]
            }
        }

    # 3. LLM-based Behavioral Validation
    plan = state.get("plan", {})
    llm = get_llm()
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Project Plan: {json.dumps(plan, indent=2)}\n\nGenerated Code: {json.dumps(code, indent=2)}")
    ]
    
    response = llm.invoke(messages)
    validation_result = extract_json(response.content)
    
    print(f"Validation Status: {validation_result.get('status')}")
    
    return {"validation": validation_result}
