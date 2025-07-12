from pathlib import Path
import json

# function prompt_with_validation
# Ask the user for input with validation and optional example, error message, and blank allowance.

def prompt_with_validation(prompt_text, example=None, allow_blank=False, validator=None, error_message=None):
    while True:
        print("\n" + prompt_text)
        if example:
            print(f"   Example: {example}")
        user_input = input(" > ").strip()
        if not user_input and allow_blank:
            return None
        if not user_input and not allow_blank:
            print("   This field is required. Please enter a value.")
            continue
        if validator and not validator(user_input):
            print(f"   {error_message or 'Invalid input.'}")
            continue
        return user_input

# function yes_no_prompt
# Ask the user a yes/no question and return True/False based on their answer.

def yes_no_prompt(prompt_text, default_yes=True):
    while True:
        print(f"\n{prompt_text} Choose y or n (y/n)")
        user_input = input(" > ").strip().lower()
        if not user_input:
            return default_yes
        if user_input in ["y", "yes"]:
            return True
        if user_input in ["n", "no"]:
            return False
        print("   Please enter 'y' or 'n'.")

    
# function file_or_url_validator
# Validate if the given path is a file or a URL.

def file_or_url_validator(path):
    if path.startswith("http://") or path.startswith("https://"):
        return True
    try:
        p = Path(path).expanduser().resolve()
        return p.exists()
    except Exception:
        return False

# function output_dir_validator
# Validate if the given path is a valid output directory or can be created.

def output_dir_validator(path):
    try:
        p = Path(path).expanduser().resolve()
        return p.parent.exists() or not path
    except Exception:
        return False
    
# function detect_json_source_type
# Detect if the source string is a file, URL, or API endpoint.

def detect_json_source_type(source):
    if not source:
        return "Unknown"
    if source.startswith("http://") or source.startswith("https://"):
        if "/api/" in source or source.rstrip("/").endswith("/api"):
            return "API"
        else:
            return "URL"
    else:
        return "File"


# Determines if a value is simple enough to be embedded directly in YAML.
def is_simple_yaml_value(value):
    if isinstance(value, (str, int, float, bool, type(None))):
        return True
    if isinstance(value, list):
        return all(isinstance(item, (str, int, float, bool, type(None))) for item in value) and len(value) <= 5
    if isinstance(value, dict):
        return all(is_simple_yaml_value(inner_val) for inner_val in value.values()) and len(value) <= 5
    return False

# Traverse a dict using a dot-separated key path (e.g., 'columns' or 'foo.bar'). Returns the value or None if not found.
def get_value_by_key_path(obj, key_path):
    if not key_path:
        return obj
    keys = key_path.split('.')
    current = obj
    for k in keys:
        if isinstance(current, dict) and k in current:
            current = current[k]
        else:
            return None
    return current

# Converts a single JSON object to a markdown string with a YAML front matter block. If yaml_key_path is set, only the contents of that key/path are used for the YAML front matter.
def convert_json_object_to_markdown(json_object, object_index, flatten_repetition=True, yaml_key_path=None):
    yaml_property_dict = get_value_by_key_path(json_object, yaml_key_path)
    markdown_detail_sections = []

    # If the yaml_property_dict is a string (e.g., columns: "{id,name}"), try to parse as CSV or show as a single value
    if isinstance(yaml_property_dict, str):
        val = yaml_property_dict.strip()
        if val.startswith('{') and val.endswith('}'):
            val = val[1:-1]
        keys = [k.strip() for k in val.split(',') if k.strip()]
        yaml_property_dict = {k: None for k in keys}

    if not isinstance(yaml_property_dict, dict):
        yaml_property_dict = {yaml_key_path or 'value': yaml_property_dict}

    yaml_block = "---\n"
    for yaml_key, yaml_value in yaml_property_dict.items():
        if flatten_repetition and is_simple_yaml_value(yaml_value):
            yaml_block += f"{yaml_key}: {json.dumps(yaml_value, ensure_ascii=False)}\n"
        else:
            # For complex values, add as markdown section
            markdown_detail_sections.append(f"## {yaml_key}\n\n```")
            markdown_detail_sections.append(json.dumps(yaml_value, indent=2, ensure_ascii=False))
            markdown_detail_sections.append("```\n")
    yaml_block += "---\n\n"

    return yaml_block + "\n".join(markdown_detail_sections)

# Loads JSON from a local file or a URL (optionally as an API call).
import requests
def load_json_from_source(source, api_method=None, api_headers=None, api_query=None, api_body=None):
    if source is None:
        raise ValueError("No JSON input source provided.")
    if source.startswith("http://") or source.startswith("https://"):
        method = api_method or "GET"
        headers = api_headers or {}
        params = api_query or {}
        data = api_body or None
        resp = requests.request(method, source, headers=headers, params=params, data=data)
        resp.raise_for_status()
        return resp.json()
    else:
        with open(source, "r", encoding="utf-8") as f:
            return json.load(f)

# Remove illegal characters from filenames for cross-platform compatibility.
import re
def sanitize_filename_for_filesystem(filename):
    filename = str(filename)
    filename = re.sub(r'[\\/:*?"<>|]', '_', filename)
    filename = filename.strip()
    if not filename:
        filename = "untitled"
    return filename
