
# ==============================
# Imports
# ==============================

import datetime
from urllib.parse import urlparse, parse_qs


# ==============================
# Utility Functions
# ==============================

def parse_key_value_pairs(input_str):
    """
    Parse a string of key:value pairs (comma or newline separated) into a dictionary.
    Used for headers and query parameters input.
    """

    if not input_str:
        return {}
    pairs = {}
    for line in input_str.split("\n"):
        for part in line.split(","):
            if ":" in part:
                k, v = part.split(":", 1)
                pairs[k.strip()] = v.strip()
    return pairs

def build_curl(url, method, headers, query, body):
    """
    Build a cURL command string from the given URL, HTTP method, headers, query params, and body.
    Used to show the user an example cURL for their API request.
    """

    import shlex
    curl = ["curl", "-X", method.upper()]
    for k, v in (headers or {}).items():
        curl += ["-H", shlex.quote(f"{k}: {v}")]
    if query:
        from urllib.parse import urlencode, urlparse, urlunparse, parse_qsl
        url_parts = list(urlparse(url))
        orig_query = dict(parse_qsl(url_parts[4]))
        orig_query.update(query)
        url_parts[4] = urlencode(orig_query)
        url = urlunparse(url_parts)
    curl.append(shlex.quote(url))
    if body and method.upper() in ["POST", "PUT", "PATCH"]:
        curl += ["--data", shlex.quote(body)]
    return " ".join(curl)


# ==============================
# Step Functions for CLI Wizard
# ==============================

def step_json_input_source(state, prompt_with_validation, yes_no_prompt, file_or_url_validator, detect_json_source_type):
    """
    Prompt the user for the JSON input source (file path or URL),
    detect its type, and update the state accordingly.
    
    Available inputs:
    - json_input_source: Local file path or URL to JSON data
      • File path: Absolute or relative path to a .json file
      • URL: HTTP/HTTPS URL that returns JSON data
      • API endpoint: REST API that returns JSON array
    
    Behavior: 
    - Validates file existence or URL format
    - Auto-detects source type (File/URL/API)
    - Allows user to override detection for API endpoints
    - Resets dependent configuration when source changes
    """
    
    state["json_input_source"] = prompt_with_validation(
        "📥 Enter the path or URL to the JSON file or API:",
        example="C:/Users/user/Downloads/array.json or https://example.com/data.json or https://api.example.com/data",
        allow_blank=False,
        validator=file_or_url_validator,
        error_message="File does not exist or URL is invalid."
    )
    
    detected_type = detect_json_source_type(state["json_input_source"])
    print(f"Detected source type: {detected_type}")
    is_api = yes_no_prompt("Is this an API endpoint?", default_yes=(detected_type=="API"))
    state["json_source_type"] = "API" if is_api else detected_type
    
    # Reset dependent state if source type changed
    if state["last_json_source_type"] and state["json_source_type"] != state["last_json_source_type"]:
        state["api_method"] = None
        state["api_headers"] = None
        state["api_query"] = None
        state["api_body"] = None
    
    state["last_json_source_type"] = state["json_source_type"]
    state["filename_key"] = None
    state["yaml_key_path"] = None


def step_api_details(state, prompt_with_validation, yes_no_prompt):
    """
    Prompt the user for API details if the source is an API.
    
    Available configuration options:
    - provide_details: Whether to configure API request details manually
    - use_curl: Whether to parse configuration from a cURL command
    - api_method: HTTP method (GET, POST, PUT, DELETE, etc.)
    - api_headers: Request headers as key:value pairs (e.g., Authorization, Content-Type)
    - api_query: Query parameters as key:value pairs (e.g., user_id, filter)
    - api_body: Request body for POST/PUT requests (JSON string or form data)
    
    Flow: If user doesn't want to provide details, use defaults (GET with no auth).
    If they do want to provide details, ask if they prefer cURL or manual entry.
    """
    
    if state["json_source_type"] != "API":
        _reset_api_state(state)
        return
    
    # Ask if user wants to provide API endpoint details
    provide_details = yes_no_prompt(
        "Do you want to provide details for this API endpoint (method, headers, query params)?", 
        default_yes=False
    )
    
    if not provide_details:
        # Use simple defaults for basic API access
        _set_default_api_config(state)
        return
    
    # User wants to provide details - ask for preferred method
    use_curl = yes_no_prompt("Do you want to paste a cURL command instead of entering details manually?", default_yes=False)
    
    if use_curl:
        _configure_api_from_curl(state, prompt_with_validation)
    else:
        _configure_api_manually(state, prompt_with_validation, yes_no_prompt)


def _reset_api_state(state):
    """Reset all API-related state variables"""
    state["api_method"] = None
    state["api_headers"] = None
    state["api_query"] = None
    state["api_body"] = None


def _set_default_api_config(state):
    """Set default API configuration for simple GET requests"""
    state["api_method"] = "GET"
    state["api_headers"] = {}
    state["api_query"] = {}
    state["api_body"] = None


def _configure_api_from_curl(state, prompt_with_validation):
    """Parse API configuration from a cURL command"""
    curl_str = prompt_with_validation(
        "Paste your cURL command:",
        example="curl -X GET 'https://api.example.com/data' -H 'Authorization: Bearer token123'",
        allow_blank=False
    )
    
    import shlex
    try:
        curl_parts = shlex.split(curl_str)
    except ValueError as e:
        print(f"Error parsing cURL command: {e}")
        print("Falling back to default GET configuration.")
        _set_default_api_config(state)
        return
    
    # Initialize with defaults
    state["api_method"] = "GET"
    state["api_headers"] = {}
    state["api_query"] = {}
    state["api_body"] = None
    
    i = 0
    while i < len(curl_parts):
        part = curl_parts[i]
        if part == "-X" and i+1 < len(curl_parts):
            state["api_method"] = curl_parts[i+1].upper()
            i += 2
        elif part == "-H" and i+1 < len(curl_parts):
            header = curl_parts[i+1]
            if ":" in header:
                key, value = header.split(":", 1)
                state["api_headers"][key.strip()] = value.strip()
            i += 2
        elif part in ["--data", "--data-raw", "--data-binary"] and i+1 < len(curl_parts):
            state["api_body"] = curl_parts[i+1]
            i += 2
        elif part.startswith("http://") or part.startswith("https://"):
            # Extract query parameters from URL
            url = part
            parsed = urlparse(url)
            if parsed.query:
                state["api_query"] = {k: v[0] if isinstance(v, list) and len(v)==1 else v 
                                    for k, v in parse_qs(parsed.query).items()}
            i += 1
        else:
            i += 1


def _configure_api_manually(state, prompt_with_validation, yes_no_prompt):
    """Configure API details through manual prompts"""
    # HTTP Method
    state["api_method"] = prompt_with_validation(
        "🌐 Enter HTTP method:",
        example="GET, POST, PUT, DELETE",
        allow_blank=True
    ) or "GET"
    state["api_method"] = state["api_method"].upper()
    
    # Headers
    has_headers = yes_no_prompt(
        "🔑 Does this API require headers (e.g., Authorization, Content-Type)?", 
        default_yes=False
    )
    if has_headers:
        api_headers_str = prompt_with_validation(
            "Enter API headers as key:value pairs (comma or newline separated):",
            example="Authorization: Bearer token123, Content-Type: application/json",
            allow_blank=True
        )
        state["api_headers"] = parse_key_value_pairs(api_headers_str)
    else:
        state["api_headers"] = {}
    
    # Query Parameters
    has_query = yes_no_prompt(
        "🧩 Does this API require query parameters (e.g., filters, pagination)?", 
        default_yes=False
    )
    if has_query:
        api_query_str = prompt_with_validation(
            "Enter API query parameters as key:value pairs (comma or newline separated):",
            example="user_id: 123, page: 1, limit: 50",
            allow_blank=True
        )
        state["api_query"] = parse_key_value_pairs(api_query_str)
    else:
        state["api_query"] = {}
    
    # Request Body (for POST/PUT/PATCH)
    if state["api_method"] in ["POST", "PUT", "PATCH"]:
        has_body = yes_no_prompt(
            "📝 Does this request require a body (JSON data, form data)?", 
            default_yes=False
        )
        if has_body:
            state["api_body"] = prompt_with_validation(
                "Enter request body:",
                example='{"filter": "active", "sort": "name"}',
                allow_blank=True
            )
        else:
            state["api_body"] = None
    else:
        state["api_body"] = None


def step_transaction_identifier(state, prompt_with_validation):
    """
    Prompt the user for a transaction identifier for the output folder.
    
    Available inputs:
    - transaction_identifier: String to identify this export batch
      • Custom name: Any descriptive text (e.g., "Customer Data Export")
      • Auto-generated: Leave blank for timestamp-based name (YYYY-MM-DD_HH-MM-SS)
    
    Purpose: Used as folder name for organizing multiple export batches
    """
    
    state["transaction_identifier"] = prompt_with_validation(
        "📝 Enter a transaction identifier for the output folder (leave blank for timestamp):",
        example="Customer Data Export 2025-07-12 or Document Batch v2",
        allow_blank=True
    )
    if not state["transaction_identifier"]:
        state["transaction_identifier"] = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def step_output_directory(state, prompt_with_validation, output_dir_validator):
    """
    Prompt the user for the output directory for markdown files.
    
    Available inputs:
    - output_directory_path: Absolute path where markdown files will be saved
      • Custom path: Any valid directory path (e.g., "C:/Users/user/Documents/exports")
      • Default path: Leave blank for ~/Downloads/{transaction_identifier}
      • Relative path: Will be resolved relative to user's home directory
    
    Behavior: Creates directory if it doesn't exist, validates parent directory exists
    """
    
    state["output_directory_path"] = prompt_with_validation(
        f"📂 Enter the output directory (leave blank for ~/Downloads/{state['transaction_identifier']}):",
        example=f"C:/Users/user/Documents/exports or ~/Documents/{state['transaction_identifier']}",
        allow_blank=True,
        validator=output_dir_validator,
        error_message="Parent directory does not exist."
    )
    if not state["output_directory_path"]:
        state["output_directory_path"] = None


def step_flatten_repetition(state, yes_no_prompt):
    """
    Ask the user if repeated items and simple arrays/objects should be flattened and embedded in YAML.
    
    Available inputs:
    - flatten_repetition: Boolean flag for content processing
      • True (Yes): Flattens nested objects and arrays into YAML front matter for cleaner markdown
      • False (No): Preserves original JSON structure in markdown content
    
    Effect on output:
    - Yes: Complex nested data becomes YAML metadata, simpler markdown content
    - No: Full JSON structure preserved as markdown text blocks
    """
    
    state["flatten_repetition"] = yes_no_prompt(
        "🔧 Flatten repeated items and embed simple arrays/objects in YAML front matter?",
        default_yes=True
    )


def step_filename_key(state, prompt_with_validation):
    """
    Prompt the user for the key to use for exported file names.
    
    Available inputs:
    - filename_key: JSON object key to use for generating filenames
      • Specific key: Use value from this key (e.g., "id", "slug", "name")
      • Auto-detect: Leave blank to try common keys ("name", "title") then fallback to timestamp
      • Fallback: If key not found or blank, uses timestamp + index
    
    Examples: If JSON has {"id": "user123", "name": "John"}, using "id" creates "user123.md"
    """
    
    state["filename_key"] = prompt_with_validation(
        "🔑 Enter the key to use for exported file names (leave blank to auto-detect):",
        example="id, slug, name, title, or any JSON key that contains filename-suitable values",
        allow_blank=True
    )
    if not state["filename_key"]:
        state["filename_key"] = None


def step_yaml_key_path(state, prompt_with_validation):
    """
    Prompt the user for the key or dot-separated path to use for YAML front matter in the markdown files.
    
    Available inputs:
    - yaml_key_path: Specify which JSON data becomes YAML front matter
      • All fields: Leave blank to include all JSON fields in YAML front matter
      • Single key: Use one top-level key (e.g., "metadata", "properties")
      • Nested path: Use dot notation for nested data (e.g., "user.profile", "config.settings")
    
    Examples:
    - Blank: All JSON becomes YAML
    - "metadata": Only the metadata object becomes YAML
    - "user.profile": Only user.profile object becomes YAML front matter
    """
    
    state["yaml_key_path"] = prompt_with_validation(
        "📝 Enter the key or dot-separated path to use for YAML front matter (leave blank for all):",
        example="metadata, config.settings, user.profile, or leave blank to include all fields",
        allow_blank=True
    )
    if not state["yaml_key_path"]:
        state["yaml_key_path"] = None