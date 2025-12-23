import os

def write_files(file_dict: dict, base_path: str = "generated_site"):
    """
    Writes files to disk based on a dictionary of {filename: content}.
    """
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    for filename, content in file_dict.items():
        # Construct full path
        # Remove leading slashes to avoid absolute path issues
        clean_filename = filename.lstrip("/\\")
        full_path = os.path.join(base_path, clean_filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Sanity Check: Validate JSX before writing
        if filename.endswith(".jsx") or filename.endswith(".tsx"):
            if "export default" not in content:
                print(f"Warning: {filename} missing export default")
            
            # Basic brace matching check
            if content.count("{") != content.count("}"):
                print(f"Error: Unmatched braces in {filename}. Skipping write to prevent crash.")
                continue # Skip writing broken file
                
            if content.count("(") != content.count(")"):
                print(f"Error: Unmatched parentheses in {filename}. Skipping write to prevent crash.")
                continue

        with open(full_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content.strip() + "\n")
            
    print(f"Successfully wrote {len(file_dict)} files to {base_path}")
