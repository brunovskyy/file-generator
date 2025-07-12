
import json
import requests
from pathlib import Path
from urllib.parse import urlparse
import sys
import logging
import datetime
from dataclasses import dataclass, asdict, field

# Local imports
import scripts.json_md.cli_steps as cli_steps
from scripts.json_md.step_helpers import *
from scripts.json_md.config import ExportConfig, APP_SETTINGS, DEFAULT_FILENAME_KEYS
from scripts.json_md.validators import file_or_url_validator, output_dir_validator

# ==============================
# Logging Configuration
# ==============================

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# ==============================

# ==============================
# Configurable variables / Defaults (now in dataclass)
# ==============================

@dataclass
class ExportConfig:
    json_input_path_or_url: str = None
    output_directory_path: str = None
    flatten_repetition: bool = True
    filename_key: str = None
    transaction_identifier: str = None
    yaml_key_path: str = None
    api_method: str = None
    api_headers: dict = None
    api_query: dict = None
    api_body: dict = None
    summary_dict: dict = field(default_factory=dict)

def export_json_list_to_markdown_files(
    json_input_path_or_url,
    output_directory_path,
    flatten_repetition=True,
    filename_key=None,
    transaction_identifier=None,
    yaml_key_path=None,
    api_method=None,
    api_headers=None,
    api_query=None,
    api_body=None,
    summary_dict=None
):
    """
    Exports a list of JSON objects to individual markdown files in the specified directory.
    Also writes a README.md summary file with settings and cURL if API.
    
    """
    
    try:
        json_data_list = load_json_from_source(json_input_path_or_url, api_method, api_headers, api_query, api_body)
    except Exception as error:
        logging.error(f"Aborting export: Could not load JSON. {error}")
        sys.exit(1)

    if not isinstance(json_data_list, list):
        logging.error("The JSON root must be a list of objects (array of dictionaries). Aborting.")
        sys.exit(1)

    # If output_directory_path is None, set default to Downloads/transaction_identifier
    
    if not output_directory_path:
        user_home = Path.home()
        downloads_dir = user_home / "Downloads"
        if not transaction_identifier:
            transaction_identifier = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_path = downloads_dir / str(transaction_identifier)
        logging.info(f"No output directory provided. Using default: {output_path}")
    else:
        output_path = Path(output_directory_path).expanduser().resolve()

    try:
        output_path.mkdir(parents=True, exist_ok=True)
    except Exception as error:
        logging.error(f"Could not create output directory '{output_path}': {error}")
        sys.exit(1)

    for object_index, json_object in enumerate(json_data_list):
        # Determine base filename
        base_filename = None
        if filename_key:
            base_filename = json_object.get(filename_key)
        if not base_filename:
            # Try common alternatives
            for alt_key in ["name", "title"]:
                if json_object.get(alt_key):
                    base_filename = json_object[alt_key]
                    break
        if not base_filename:
            # Fallback to timestamp with index
            base_filename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f") + f"_{object_index+1}"

        safe_filename = f"{sanitize_filename_for_filesystem(base_filename)}.md"
        markdown_content = convert_json_object_to_markdown(json_object, object_index, flatten_repetition, yaml_key_path)

        try:
            with open(output_path / safe_filename, "w", encoding="utf-8") as markdown_file:
                markdown_file.write(markdown_content)
            logging.info(f"✅ Exported: {safe_filename}")
        except Exception as error:
            logging.error(f"Failed to write file '{safe_filename}': {error}")

    # Write README.md summary

    if summary_dict:
        readme_lines = ["# Export Summary\n"]
        readme_lines.append("## Settings\n")
        for k, v in summary_dict.items():
            if k == "cURL":
                continue
            readme_lines.append(f"- **{k}:** {v}")
        if "cURL" in summary_dict:
            readme_lines.append("\n## Example cURL\n")
            readme_lines.append(f"```bash\n{summary_dict['cURL']}\n```")
        with open(output_path / "README.md", "w", encoding="utf-8") as f:
            f.write("\n".join(readme_lines))

# ==============================
# CLI Application Class
# ==============================

class DocumentCreatorApp:

    """Main application class for the Document Creator CLI"""
    
    def __init__(self):
        self.config = ExportConfig()
        self.extra_state = {
            "json_source_type": None,
            "last_json_source_type": None,
            "curl_cmd": None,
            "json_input_source": None,
            "api_method": None,
            "api_headers": None,
            "api_query": None,
            "api_body": None,
            "transaction_identifier": None,
            "output_directory_path": None,
            "flatten_repetition": True,
            "filename_key": None,
            "yaml_key_path": None
        }
        self.steps = self._define_steps()
    
    def _define_steps(self):
        """Define configuration steps with metadata"""
        return [
            {
                "name": "JSON input source",
                "func": lambda c, e: cli_steps.step_json_input_source(
                    e, prompt_with_validation, yes_no_prompt, file_or_url_validator, detect_json_source_type
                ),
                "key": "json_input_path_or_url",
                "resets": ["filename_key", "yaml_key_path", "api_method", "api_headers", "api_query", "api_body"],
                "copy_from_extra": [("json_input_source", "json_input_path_or_url")]
            },
            {
                "name": "API details",
                "func": lambda c, e: cli_steps.step_api_details(e, prompt_with_validation, yes_no_prompt),
                "key": None,
                "copy_from_extra": ["api_method", "api_headers", "api_query", "api_body"]
            },
            {
                "name": "Transaction identifier",
                "func": lambda c, e: cli_steps.step_transaction_identifier(e, prompt_with_validation),
                "key": "transaction_identifier",
                "copy_from_extra": ["transaction_identifier"]
            },
            {
                "name": "Output directory",
                "func": lambda c, e: cli_steps.step_output_directory(e, prompt_with_validation, output_dir_validator),
                "key": "output_directory_path",
                "copy_from_extra": [("output_directory_path", "output_directory_path")]
            },
            {
                "name": "Flatten repetition",
                "func": lambda c, e: cli_steps.step_flatten_repetition(e, yes_no_prompt),
                "key": "flatten_repetition",
                "format": lambda v: 'Yes' if v else 'No',
                "copy_from_extra": ["flatten_repetition"]
            },
            {
                "name": "Filename key",
                "func": lambda c, e: cli_steps.step_filename_key(e, prompt_with_validation),
                "key": "filename_key",
                "format": lambda v: v or '[auto]',
                "copy_from_extra": ["filename_key"]
            },
            {
                "name": "YAML key path",
                "func": lambda c, e: cli_steps.step_yaml_key_path(e, prompt_with_validation),
                "key": "yaml_key_path",
                "format": lambda v: v or '[all]',
                "copy_from_extra": ["yaml_key_path"]
            }
        ]
    
    def _execute_steps(self, start_step=0):
        """Execute configuration steps starting from a given step"""
        for idx in range(start_step, len(self.steps)):
            self.steps[idx]["func"](self.config, self.extra_state)
            # Copy values from extra_state to config if specified
            if "copy_from_extra" in self.steps[idx]:
                for key_mapping in self.steps[idx]["copy_from_extra"]:
                    if isinstance(key_mapping, tuple):
                        source_key, target_key = key_mapping
                        if source_key in self.extra_state:
                            setattr(self.config, target_key, self.extra_state[source_key])
                    else:
                        if key_mapping in self.extra_state:
                            setattr(self.config, key_mapping, self.extra_state[key_mapping])
    
    def _build_curl_if_api(self):
        """Build cURL command if using API source"""
        self.extra_state["curl_cmd"] = None
        if self.extra_state.get("json_source_type") == "API":
            self.extra_state["curl_cmd"] = cli_steps.build_curl(
                self.config.json_input_path_or_url,
                self.config.api_method or "GET",
                self.config.api_headers,
                self.config.api_query,
                self.config.api_body
            )
    
    def _format_step_value(self, step, value):
        """Format a step value for display"""
        key = step.get("key")
        if key == "output_directory_path":
            value = value or f"[default: ~/Downloads/{self.config.transaction_identifier}]"
        if "format" in step:
            value = step["format"](value)
        return value
    
    def _show_summary(self):
        """Display current configuration summary"""
        print("\nSummary of your selections:")
        for step in self.steps:
            key = step.get("key")
            if not key:
                continue
            val = getattr(self.config, key)
            formatted_val = self._format_step_value(step, val)
            print(f"  {step['name']}: {formatted_val}")
        
        if self.extra_state.get("json_source_type") == "API":
            print(f"  API Method: {self.config.api_method}")
            print(f"  API Headers: {self.config.api_headers if self.config.api_headers else '[none]'}")
            print(f"  API Query Params: {self.config.api_query if self.config.api_query else '[none]'}")
            print(f"  Example cURL: {self.extra_state['curl_cmd']}")
    
    def _get_step_to_edit(self):
        """Get user choice for which step to edit"""
        print("\nWhich step would you like to edit?")
        step_names = [step['name'] for step in self.steps]
        for name in step_names:
            print(f"  - {name}")
        
        while True:
            step_choice = input("Enter step name to edit (case-insensitive): ").strip().lower()
            if not step_choice:
                print("Invalid input. Please enter a step name.")
                continue
            
            matched = [i for i, step in enumerate(self.steps) if step['name'].lower() == step_choice]
            if not matched:
                print(f"Step '{step_choice}' not found. Please enter a valid step name.")
                continue
            
            return matched[0]
    
    def _reset_dependent_steps(self, step_index):
        """Reset dependent configuration values when editing a step"""
        for reset_key in self.steps[step_index].get("resets", []):
            setattr(self.config, reset_key, None)
            # Also reset in extra_state
            if reset_key in self.extra_state:
                self.extra_state[reset_key] = None
    
    def _prepare_summary_dict(self):
        """Prepare summary dictionary for README generation"""
        summary_dict = {}
        
        # Add step values
        for step in self.steps:
            key = step.get("key")
            if not key:
                continue
            val = getattr(self.config, key)
            formatted_val = self._format_step_value(step, val)
            summary_dict[step["name"]] = formatted_val
        
        # Add all config fields
        for k, v in asdict(self.config).items():
            if k not in summary_dict:
                summary_dict[k] = v
        
        # Add extra state
        for k, v in self.extra_state.items():
            if k not in summary_dict:
                summary_dict[k] = v
        
        return summary_dict
    
    def run_interactive_setup(self):
        """Run the interactive CLI setup process"""
        current_step = 0
        
        while True:
            # Execute steps from current position
            self._execute_steps(current_step)
            
            # Build cURL if needed
            self._build_curl_if_api()
            
            # Show summary and get confirmation
            self._show_summary()
            
            if yes_no_prompt("Proceed with these settings?", default_yes=True):
                break
            
            # User wants to edit - get step choice
            current_step = self._get_step_to_edit()
            self._reset_dependent_steps(current_step)
    
    def run(self):
        """Main application entry point"""
        try:
            logging.info("Starting Document Creator CLI...")
            
            # Run interactive setup
            self.run_interactive_setup()
            
            # Prepare final configuration
            self.config.summary_dict = self._prepare_summary_dict()
            
            # Execute export
            logging.info("Starting export process...")
            export_json_list_to_markdown_files(**asdict(self.config))
            
            logging.info("Export completed successfully!")
            
        except KeyboardInterrupt:
            logging.info("\nOperation cancelled by user.")
            sys.exit(0)
        except Exception as e:
            logging.error(f"Application error: {e}")
            sys.exit(1)


# ==============================
# Application Entry Point
# ==============================

def main():
    """Main entry point for the application"""
    app = DocumentCreatorApp()
    app.run()


if __name__ == "__main__":
    main()
