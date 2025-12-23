import os
import sys
import argparse
import json
import re
import shutil
import subprocess
from graph.flow import create_graph
from utils.file_writer import write_files

BASE_DIR = "generated-sites"
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates", "react-vite-tailwind")

def get_next_app_dir(app_name):
    """
    Creates a new unique directory for the app.
    """
    os.makedirs(BASE_DIR, exist_ok=True)
    existing = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]
    app_id = len(existing) + 1
    
    # Clean app name
    safe_name = re.sub(r'[^a-zA-Z0-9]', '-', app_name.lower()).strip('-')
    if not safe_name:
        safe_name = "app"
        
    return os.path.join(BASE_DIR, f"app-{app_id:03d}-{safe_name}")

def bootstrap_project(output_dir):
    """
    Copies the fixed React+Vite+Tailwind template to the output directory.
    """
    print(f"Bootstrapping project in {output_dir}...")
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    
    shutil.copytree(
        TEMPLATE_DIR,
        output_dir,
        dirs_exist_ok=True
    )
    print("Template copied successfully.")

def npm_install(project_dir):
    """
    Runs npm install in the project directory.
    """
    print(f"Running npm install in {project_dir}...")
    try:
        subprocess.run(
            ["npm", "install"],
            cwd=project_dir,
            check=True,
            shell=True if sys.platform == "win32" else False
        )
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running npm install: {e}")

def apply_fixes(code, validation):
    """
    Simple fix applicator: currently only updates package.json if suggested.
    """
    suggested_fixes = validation.get("suggested_fixes", {})
    
    # Handle package.json fixes (dependency merging)
    if isinstance(suggested_fixes, dict) and "package.json" in suggested_fixes and "package.json" in code:
        try:
            # Safe load
            pkg_raw = code["package.json"]
            if isinstance(pkg_raw, str):
                current_pkg = json.loads(pkg_raw)
            elif isinstance(pkg_raw, dict):
                current_pkg = pkg_raw
            else:
                current_pkg = {} # Should not happen if validator passed

            fix_pkg = suggested_fixes["package.json"]
            
            # Merge devDependencies
            if "devDependencies" in fix_pkg:
                current_pkg.setdefault("devDependencies", {})
                current_pkg["devDependencies"].update(fix_pkg["devDependencies"])
                
            # Merge dependencies
            if "dependencies" in fix_pkg:
                current_pkg.setdefault("dependencies", {})
                current_pkg["dependencies"].update(fix_pkg["dependencies"])
                
            code["package.json"] = json.dumps(current_pkg, indent=2)
            print("Auto-fixed package.json dependencies.")
        except Exception as e:
            print(f"Failed to apply package.json fixes: {e}")

    # Handle script fixes (legacy list-based)
    if isinstance(suggested_fixes, list):
        if any("scripts" in fix or "vite" in fix.lower() for fix in suggested_fixes):
            if "package.json" in code:
                try:
                    # Safe load
                    pkg_raw = code["package.json"]
                    if isinstance(pkg_raw, str):
                        pkg = json.loads(pkg_raw)
                    elif isinstance(pkg_raw, dict):
                        pkg = pkg_raw
                    else:
                        pkg = {}

                    pkg["scripts"] = {
                        "dev": "vite",
                        "build": "vite build",
                        "preview": "vite preview"
                    }
                    code["package.json"] = json.dumps(pkg, indent=2)
                    print("Auto-fixed package.json scripts.")
                except:
                    pass
    return code

def main():
    parser = argparse.ArgumentParser(description="Autosite: AI Website Generator")
    parser.add_argument("prompt", nargs="?", help="The prompt for the website you want to build")
    args = parser.parse_args()

    user_prompt = args.prompt
    if not user_prompt:
        print("Please provide a prompt. Example: python main.py 'Create a portfolio website'")
        return

    print(f"Starting Autosite with prompt: {user_prompt}")
    
    app = create_graph()
    
    initial_state = {"user_prompt": user_prompt}
    
    # Run the graph
    result = app.invoke(initial_state)
    
    print("\n--- GENERATION COMPLETE ---")
    
    code = result.get("code")
    validation = result.get("validation")

    if code:
        if validation and validation.get("status") == "fail":
            print("\nValidation Failed. Attempting auto-fixes...")
            code = apply_fixes(code, validation)
            
        # Determine app name for folder creation
        app_name = "generated-app"
        if result.get("plan") and "app_name" in result["plan"]:
            app_name = result["plan"]["app_name"]
            
        output_dir = get_next_app_dir(app_name)
        
        # 1. Bootstrap Project
        bootstrap_project(output_dir)
        
        # 2. Write Generated Files (Overwriting template placeholders)
        print(f"Writing generated files to: {output_dir}")
        write_files(code, output_dir)
        
        # 3. Auto-run npm install
        npm_install(output_dir)
        
        print(f"\nDONE! Your app is ready in: {output_dir}")
        print(f"Run: cd {output_dir} && npm run dev")
        
        if validation:
            print("\nValidation Report:")
            print(json.dumps(validation, indent=2))
    else:
        print("Error: No code was generated.")

if __name__ == "__main__":
    main()
