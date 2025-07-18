"""
Enhanced CLI User Interface
Provides professional CLI navigation with arrow keys, live previews, and polished UX.
"""

import sys
import json
from typing import List, Dict, Any, Optional, Tuple, Callable
from pathlib import Path

try:
    from pick import pick
    PICK_AVAILABLE = True
except ImportError:
    PICK_AVAILABLE = False

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.columns import Columns
    from rich.text import Text
    from rich.table import Table
    from rich.progress import Progress, BarColumn, TextColumn
    from rich.layout import Layout
    from rich.live import Live
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

try:
    import colorama
    from colorama import Fore, Back, Style
    colorama.init()
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False


class EnhancedCLI:
    """Enhanced CLI interface with arrow key navigation and rich formatting."""
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.step_history = []
        self.current_step = 0
        
    def show_banner(self):
        """Display application banner with styling."""
        if RICH_AVAILABLE:
            banner = Panel.fit(
                "[bold cyan]DocGenius[/bold cyan]\n[white]Professional Document Generator[/white]\n[dim]Navigate with ↑↓ arrows, Enter to select[/dim]",
                style="blue"
            )
            self.console.print(banner)
        else:
            print("\n" + "="*60)
            print("🚀 DocGenius - Professional Document Generator")
            print("="*60)
            
    def show_step_progress(self, current_step: str, total_steps: int, step_number: int):
        """Show progress through the configuration steps."""
        if RICH_AVAILABLE:
            # Create visual progress indicators
            indicators = []
            for i in range(total_steps):
                if i < step_number - 1:
                    indicators.append("[bold green]●[/bold green]")
                elif i == step_number - 1:
                    indicators.append("[bold yellow]●[/bold yellow]")
                else:
                    indicators.append("[dim white]○[/dim white]")
            
            progress_text = f"Step {step_number}/{total_steps}: {current_step}"
            progress_display = " ".join(indicators) + f"\n{progress_text}"
            
            progress_bar = Panel(
                progress_display,
                title="Progress",
                border_style="blue"
            )
            self.console.print(progress_bar)
        else:
            print(f"\n📊 Step {step_number}/{total_steps}: {current_step}")
            print("─" * 50)
    
    def multi_select_step(self, 
                         title: str, 
                         options: List[str], 
                         config: Dict[str, Any],
                         preview_func: Optional[Callable] = None,
                         allow_multiple: bool = False,
                         required: bool = True,
                         back_option: bool = True) -> Tuple[int, List[str], str]:
        """
        Unified multi-selection interface for all steps.
        
        Args:
            title: Step title
            options: List of available options
            config: Current configuration
            preview_func: Optional function for live preview
            allow_multiple: Whether multiple selections are allowed
            required: Whether at least one selection is required
            back_option: Whether to include back navigation option
            
        Returns:
            Tuple of (action_code, selected_options, action_type)
            action_code: -1 = exit/back, 0+ = continue
            selected_options: List of selected option strings  
            action_type: "continue", "back", "exit", "preview"
        """
        selected_indices = []
        
        # Add navigation options
        nav_options = options.copy()
        if allow_multiple:
            nav_options.extend([
                "─" * 40,
                "✨ Preview current selection",
                "✅ Continue with selected options",
            ])
        if back_option:
            nav_options.append("🔙 Back to previous step")
        nav_options.append("❌ Exit to main menu")
        
        while True:
            # Create display options with selection status
            display_options = []
            
            for i, option in enumerate(options):
                if allow_multiple:
                    status = "✅" if i in selected_indices else "⬜"
                    display_options.append(f"{status} {option}")
                else:
                    display_options.append(option)
            
            # Add the navigation options
            display_options.extend(nav_options[len(options):])
            
            # Update title with selection count if multiple allowed
            display_title = title
            if allow_multiple and selected_indices:
                display_title = f"{title} ({len(selected_indices)} selected)"
            
            # Show current configuration context
            if config:
                self._show_config_context(config)
            
            # Handle preview if available
            if preview_func and selected_indices:
                try:
                    preview_content = preview_func(selected_indices, config)
                    if preview_content:
                        self._show_preview_panel(preview_content)
                except Exception as e:
                    self.format_warning(f"Preview error: {e}")
            
            # Get user selection
            try:
                choice_index, choice = self.arrow_select(display_title, display_options)
                
                if choice_index == -1:
                    return -1, [], "exit"
                    
                # Handle different choice types
                if "Exit to main menu" in choice:
                    return -1, [], "exit"
                elif "Back to previous step" in choice:
                    return -1, [], "back"
                elif "Continue with selected options" in choice:
                    if required and not selected_indices:
                        self.format_warning("Please select at least one option")
                        continue
                    selected_options = [options[i] for i in selected_indices]
                    return 0, selected_options, "continue"
                elif "Preview current selection" in choice:
                    if preview_func:
                        try:
                            preview_content = preview_func(selected_indices, config)
                            self._show_detailed_preview(preview_content)
                            input("\nPress Enter to continue...")
                        except Exception as e:
                            self.format_error(f"Preview failed: {e}")
                    continue
                elif choice_index < len(options):
                    # Handle option selection
                    if allow_multiple:
                        # Toggle selection for multi-select
                        if choice_index in selected_indices:
                            selected_indices.remove(choice_index)
                        else:
                            selected_indices.append(choice_index)
                        continue
                    else:
                        # Single selection - return immediately
                        return choice_index, [options[choice_index]], "continue"
                        
            except KeyboardInterrupt:
                return -1, [], "exit"
            except Exception as e:
                self.format_error(f"Selection error: {e}")
                continue
    
    def _show_config_context(self, config: Dict[str, Any]):
        """Show current configuration context."""
        if not config:
            return
            
        context_items = []
        if config.get('source'):
            context_items.append(f"📊 Source: {Path(config['source']).name}")
        if config.get('export_types'):
            context_items.append(f"🎯 Formats: {', '.join(config['export_types'])}")
        if config.get('template_path'):
            context_items.append(f"🎨 Template: {Path(config['template_path']).name}")
            
        if context_items and RICH_AVAILABLE:
            context_text = " | ".join(context_items)
            context_panel = Panel(
                context_text,
                title="Current Configuration",
                border_style="dim",
                padding=(0, 1)
            )
            self.console.print(context_panel)
        elif context_items:
            print(f"📋 Current: {' | '.join(context_items)}")
    
    def _show_preview_panel(self, preview_content: str):
        """Show preview content in a panel."""
        if RICH_AVAILABLE:
            preview_panel = Panel(
                preview_content,
                title="Live Preview",
                border_style="green",
                padding=(1, 2)
            )
            self.console.print(preview_panel)
        else:
            print(f"\n� Preview:\n{preview_content}\n")
    
    def _show_detailed_preview(self, preview_content: str):
        """Show detailed preview in full screen."""
        if RICH_AVAILABLE:
            self.console.clear()
            preview_panel = Panel(
                preview_content,
                title="📖 Detailed Preview",
                border_style="green",
                expand=True
            )
            self.console.print(preview_panel)
        else:
            print("\n" + "="*60)
            print("📖 DETAILED PREVIEW")
            print("="*60)
            print(preview_content)
            print("="*60)
    
    def arrow_select(self, title: str, options: List[str], preview_func: Optional[Callable] = None) -> Tuple[int, str]:
        """
        Arrow key selection with optional live preview.
        
        Args:
            title: Selection prompt
            options: List of options to choose from
            preview_func: Optional function that returns preview content for an option
            
        Returns:
            Tuple of (index, selected_option)
        """
        if PICK_AVAILABLE:
            try:
                if preview_func:
                    # For now, use basic pick - we'll enhance with live preview later
                    option, index = pick(options, title, indicator="→")
                    return index, option
                else:
                    option, index = pick(options, title, indicator="→")
                    return index, option
            except KeyboardInterrupt:
                return -1, "exit"
        
        # Fallback to numbered selection
        return self._numbered_fallback(title, options)
    
    def _numbered_fallback(self, title: str, options: List[str]) -> Tuple[int, str]:
        """Fallback numbered selection when arrow keys aren't available."""
        while True:
            print(f"\n{title}")
            for i, option in enumerate(options, 1):
                print(f"  {i}. {option}")
            
            try:
                choice = input(f"\nSelect (1-{len(options)}) or 'q' to quit: ").strip().lower()
                
                if choice == 'q':
                    return -1, "exit"
                
                index = int(choice) - 1
                if 0 <= index < len(options):
                    return index, options[index]
                else:
                    print(f"❌ Please enter a number between 1 and {len(options)}")
                    
            except ValueError:
                print("❌ Please enter a valid number")
            except KeyboardInterrupt:
                return -1, "exit"
    
    def show_two_column_preview(self, left_content: str, right_content: str, left_title: str = "Options", right_title: str = "Preview"):
        """Display content in two columns - options on left, preview on right."""
        if RICH_AVAILABLE:
            left_panel = Panel(left_content, title=left_title, border_style="blue")
            right_panel = Panel(right_content, title=right_title, border_style="green")
            
            columns = Columns([left_panel, right_panel], equal=True, expand=True)
            self.console.print(columns)
        else:
            # Fallback for terminals without rich
            print(f"\n┌── {left_title} " + "─" * (25 - len(left_title)) + "┐  ┌── {right_title} " + "─" * (25 - len(right_title)) + "┐")
            
            left_lines = left_content.split('\n')
            right_lines = right_content.split('\n')
            max_lines = max(len(left_lines), len(right_lines))
            
            for i in range(max_lines):
                left_line = left_lines[i] if i < len(left_lines) else ""
                right_line = right_lines[i] if i < len(right_lines) else ""
                print(f"│ {left_line:<25} │  │ {right_line:<25} │")
            
            print("└" + "─" * 27 + "┘  └" + "─" * 27 + "┘")
    
    def show_markdown_preview(self, yaml_keys: List[str], content_keys: List[str], sample_data: Dict[str, Any]) -> str:
        """Generate a markdown preview showing how the output would look."""
        preview_lines = []
        
        # YAML Front Matter
        if yaml_keys:
            preview_lines.append("---")
            for key in yaml_keys[:3]:  # Show first 3 for preview
                if key in sample_data:
                    value = sample_data[key]
                    if isinstance(value, (dict, list)):
                        preview_lines.append(f"{key}: [complex object]")
                    else:
                        preview_lines.append(f"{key}: {value}")
            if len(yaml_keys) > 3:
                preview_lines.append(f"# ... {len(yaml_keys) - 3} more keys")
            preview_lines.append("---")
            preview_lines.append("")
        
        # Content
        if content_keys:
            preview_lines.append("# Document Content")
            preview_lines.append("")
            for key in content_keys[:2]:  # Show first 2 for preview
                if key in sample_data:
                    value = sample_data[key]
                    if isinstance(value, str) and len(value) > 50:
                        preview_lines.append(f"**{key}:** {value[:47]}...")
                    else:
                        preview_lines.append(f"**{key}:** {value}")
            if len(content_keys) > 2:
                preview_lines.append(f"*... {len(content_keys) - 2} more fields*")
        
        return "\n".join(preview_lines) if preview_lines else "No content selected"
    
    def format_success(self, message: str):
        """Format success message."""
        if RICH_AVAILABLE:
            self.console.print(f"[bold green]✅ {message}[/bold green]")
        elif COLORAMA_AVAILABLE:
            print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")
        else:
            print(f"✅ {message}")
    
    def format_error(self, message: str):
        """Format error message."""
        if RICH_AVAILABLE:
            self.console.print(f"[bold red]❌ {message}[/bold red]")
        elif COLORAMA_AVAILABLE:
            print(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")
        else:
            print(f"❌ {message}")
    
    def format_info(self, message: str):
        """Format info message."""
        if RICH_AVAILABLE:
            self.console.print(f"[bold blue]ℹ️ {message}[/bold blue]")
        elif COLORAMA_AVAILABLE:
            print(f"{Fore.BLUE}ℹ️ {message}{Style.RESET_ALL}")
        else:
            print(f"ℹ️ {message}")
    
    def format_warning(self, message: str):
        """Format warning message."""
        if RICH_AVAILABLE:
            self.console.print(f"[bold yellow]⚠️ {message}[/bold yellow]")
        elif COLORAMA_AVAILABLE:
            print(f"{Fore.YELLOW}⚠️ {message}{Style.RESET_ALL}")
        else:
            print(f"⚠️ {message}")


class YAMLKeySelector:
    """Advanced YAML key selector with live preview."""
    
    def __init__(self, cli: EnhancedCLI):
        self.cli = cli
        
    def select_keys_interactive(self, sample_data: Dict[str, Any], all_keys: List[str]) -> Dict[str, Any]:
        """
        Interactive YAML key selection with live preview using unified multi-select.
        
        Args:
            sample_data: Sample data object to show previews
            all_keys: All available keys
            
        Returns:
            Dictionary with selection configuration
        """
        # Step 1: Choose selection mode using unified interface
        mode_options = [
            "📋 All keys - Include everything in YAML front matter",
            "🎯 Select specific keys - Choose which properties to include", 
            "🔧 Flatten nested objects - Convert nested data to simple keys",
            "❌ No YAML front matter - Content only"
        ]
        
        def mode_preview_func(selected_indices: List[int], config: Dict[str, Any]) -> str:
            if not selected_indices:
                return "No mode selected"
            
            mode_index = selected_indices[0]
            if mode_index == 0:  # All keys
                return self.cli.show_markdown_preview(all_keys, [], sample_data)
            elif mode_index == 1:  # Select specific
                return "Interactive key selection will follow..."
            elif mode_index == 2:  # Flatten
                flattened_keys = self._flatten_keys(sample_data)
                return self.cli.show_markdown_preview(flattened_keys, [], sample_data)
            else:  # No YAML
                return self.cli.show_markdown_preview([], all_keys, sample_data)
        
        action_code, selected_modes, action_type = self.cli.multi_select_step(
            "How should YAML keys be handled?",
            mode_options,
            {},
            preview_func=mode_preview_func,
            allow_multiple=False,
            required=True,
            back_option=True
        )
        
        if action_code == -1 or action_type in ["exit", "back"]:
            return {"mode": "exit"}
        
        mode_index = action_code
        
        # Handle different modes
        if mode_index == 0:  # All keys
            return {
                "mode": "all",
                "selected_keys": all_keys,
                "flatten_nested": False
            }
        elif mode_index == 3:  # No YAML
            return {
                "mode": "none",
                "selected_keys": [],
                "flatten_nested": False
            }
        elif mode_index == 2:  # Flatten nested
            return {
                "mode": "flatten", 
                "selected_keys": all_keys,
                "flatten_nested": True
            }
        elif mode_index == 1:  # Select specific
            return self._select_specific_keys_unified(sample_data, all_keys)
    
    def _select_specific_keys_unified(self, sample_data: Dict[str, Any], all_keys: List[str]) -> Dict[str, Any]:
        """Handle specific key selection using unified multi-select interface."""
        
        def key_preview_func(selected_indices: List[int], config: Dict[str, Any]) -> str:
            selected_keys = [all_keys[i] for i in selected_indices]
            remaining_keys = [k for k in all_keys if k not in selected_keys]
            return self.cli.show_markdown_preview(selected_keys, remaining_keys, sample_data)
        
        action_code, selected_options, action_type = self.cli.multi_select_step(
            "Select YAML keys",
            all_keys,
            {},
            preview_func=key_preview_func,
            allow_multiple=True,
            required=True,
            back_option=True
        )
        
        if action_code == -1 or action_type in ["exit", "back"]:
            return {"mode": "exit"}
        
        return {
            "mode": "select",
            "selected_keys": selected_options,
            "flatten_nested": False
        }
    
    def _flatten_keys(self, data: Dict[str, Any], prefix: str = "") -> List[str]:
        """Flatten nested dictionary keys using dot notation."""
        flattened = []
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                flattened.extend(self._flatten_keys(value, full_key))
            else:
                flattened.append(full_key)
        return flattened


def get_available_features() -> Dict[str, bool]:
    """Check which enhanced CLI features are available."""
    return {
        "arrow_keys": PICK_AVAILABLE,
        "rich_formatting": RICH_AVAILABLE,
        "colors": COLORAMA_AVAILABLE,
        "enhanced_ui": PICK_AVAILABLE and RICH_AVAILABLE
    }
