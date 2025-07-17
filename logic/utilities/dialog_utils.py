"""
GUI dialog utilities for file selection and user interaction.

This module provides consistent dialog interfaces for file selection,
directory selection, and user confirmation dialogs.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from typing import Optional, List, Dict, Any, Tuple, Union
from pathlib import Path
import logging


class DialogResult:
    """Result container for dialog operations."""
    
    def __init__(self, success: bool, value: Any = None, cancelled: bool = False):
        self.success = success
        self.value = value
        self.cancelled = cancelled


class FileDialogs:
    """File and directory selection dialogs."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._root = None
    
    def _ensure_root(self):
        """Ensure tkinter root window exists."""
        if self._root is None:
            self._root = tk.Tk()
            self._root.withdraw()  # Hide the root window
            
            # Configure for better Windows integration
            try:
                self._root.iconbitmap(default="")  # Remove default icon
            except Exception:
                pass
    
    def select_file(self, 
                   title: str = "Select File",
                   file_types: Optional[List[Tuple[str, str]]] = None,
                   initial_dir: Optional[str] = None,
                   multiple: bool = False) -> DialogResult:
        """
        Open a file selection dialog.
        
        Args:
            title: Dialog title
            file_types: List of (description, pattern) tuples
            initial_dir: Initial directory to open
            multiple: Allow multiple file selection
            
        Returns:
            DialogResult with selected file path(s)
        """
        try:
            self._ensure_root()
            
            if file_types is None:
                file_types = [
                    ("All Files", "*.*"),
                    ("CSV Files", "*.csv"),
                    ("JSON Files", "*.json"),
                    ("Text Files", "*.txt"),
                    ("Excel Files", "*.xlsx;*.xls")
                ]
            
            kwargs = {
                'title': title,
                'filetypes': file_types
            }
            
            if initial_dir:
                kwargs['initialdir'] = initial_dir
            
            if multiple:
                result = filedialog.askopenfilenames(**kwargs)
                if result:
                    paths = [Path(p) for p in result]
                    self.logger.info(f"Selected {len(paths)} files")
                    return DialogResult(success=True, value=paths)
                else:
                    return DialogResult(success=False, cancelled=True)
            else:
                result = filedialog.askopenfilename(**kwargs)
                if result:
                    path = Path(result)
                    self.logger.info(f"Selected file: {path}")
                    return DialogResult(success=True, value=path)
                else:
                    return DialogResult(success=False, cancelled=True)
        
        except Exception as e:
            error_msg = f"File selection dialog failed: {str(e)}"
            self.logger.error(error_msg)
            return DialogResult(success=False, value=error_msg)
    
    def select_directory(self, 
                        title: str = "Select Directory",
                        initial_dir: Optional[str] = None) -> DialogResult:
        """
        Open a directory selection dialog.
        
        Args:
            title: Dialog title
            initial_dir: Initial directory to open
            
        Returns:
            DialogResult with selected directory path
        """
        try:
            self._ensure_root()
            
            kwargs = {'title': title}
            
            if initial_dir:
                kwargs['initialdir'] = initial_dir
            
            result = filedialog.askdirectory(**kwargs)
            if result:
                path = Path(result)
                self.logger.info(f"Selected directory: {path}")
                return DialogResult(success=True, value=path)
            else:
                return DialogResult(success=False, cancelled=True)
        
        except Exception as e:
            error_msg = f"Directory selection dialog failed: {str(e)}"
            self.logger.error(error_msg)
            return DialogResult(success=False, value=error_msg)
    
    def save_file(self,
                 title: str = "Save File",
                 file_types: Optional[List[Tuple[str, str]]] = None,
                 initial_dir: Optional[str] = None,
                 default_extension: str = ".txt") -> DialogResult:
        """
        Open a file save dialog.
        
        Args:
            title: Dialog title
            file_types: List of (description, pattern) tuples
            initial_dir: Initial directory to open
            default_extension: Default file extension
            
        Returns:
            DialogResult with save file path
        """
        try:
            self._ensure_root()
            
            if file_types is None:
                file_types = [
                    ("All Files", "*.*"),
                    ("Markdown Files", "*.md"),
                    ("PDF Files", "*.pdf"),
                    ("Word Documents", "*.docx"),
                    ("Text Files", "*.txt")
                ]
            
            kwargs = {
                'title': title,
                'filetypes': file_types,
                'defaultextension': default_extension
            }
            
            if initial_dir:
                kwargs['initialdir'] = initial_dir
            
            result = filedialog.asksaveasfilename(**kwargs)
            if result:
                path = Path(result)
                self.logger.info(f"Save file selected: {path}")
                return DialogResult(success=True, value=path)
            else:
                return DialogResult(success=False, cancelled=True)
        
        except Exception as e:
            error_msg = f"Save file dialog failed: {str(e)}"
            self.logger.error(error_msg)
            return DialogResult(success=False, value=error_msg)


class MessageDialogs:
    """User notification and confirmation dialogs."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._root = None
    
    def _ensure_root(self):
        """Ensure tkinter root window exists."""
        if self._root is None:
            self._root = tk.Tk()
            self._root.withdraw()  # Hide the root window
    
    def show_info(self, title: str, message: str) -> DialogResult:
        """
        Show an information dialog.
        
        Args:
            title: Dialog title
            message: Information message
            
        Returns:
            DialogResult indicating success
        """
        try:
            self._ensure_root()
            messagebox.showinfo(title, message)
            self.logger.info(f"Showed info dialog: {title}")
            return DialogResult(success=True)
        
        except Exception as e:
            error_msg = f"Info dialog failed: {str(e)}"
            self.logger.error(error_msg)
            return DialogResult(success=False, value=error_msg)
    
    def show_warning(self, title: str, message: str) -> DialogResult:
        """
        Show a warning dialog.
        
        Args:
            title: Dialog title
            message: Warning message
            
        Returns:
            DialogResult indicating success
        """
        try:
            self._ensure_root()
            messagebox.showwarning(title, message)
            self.logger.info(f"Showed warning dialog: {title}")
            return DialogResult(success=True)
        
        except Exception as e:
            error_msg = f"Warning dialog failed: {str(e)}"
            self.logger.error(error_msg)
            return DialogResult(success=False, value=error_msg)
    
    def show_error(self, title: str, message: str) -> DialogResult:
        """
        Show an error dialog.
        
        Args:
            title: Dialog title
            message: Error message
            
        Returns:
            DialogResult indicating success
        """
        try:
            self._ensure_root()
            messagebox.showerror(title, message)
            self.logger.info(f"Showed error dialog: {title}")
            return DialogResult(success=True)
        
        except Exception as e:
            error_msg = f"Error dialog failed: {str(e)}"
            self.logger.error(error_msg)
            return DialogResult(success=False, value=error_msg)
    
    def confirm(self, title: str, message: str) -> DialogResult:
        """
        Show a yes/no confirmation dialog.
        
        Args:
            title: Dialog title
            message: Confirmation message
            
        Returns:
            DialogResult with True/False result
        """
        try:
            self._ensure_root()
            result = messagebox.askyesno(title, message)
            self.logger.info(f"Confirmation dialog result: {result}")
            return DialogResult(success=True, value=result)
        
        except Exception as e:
            error_msg = f"Confirmation dialog failed: {str(e)}"
            self.logger.error(error_msg)
            return DialogResult(success=False, value=error_msg)
    
    def confirm_with_cancel(self, title: str, message: str) -> DialogResult:
        """
        Show a yes/no/cancel confirmation dialog.
        
        Args:
            title: Dialog title
            message: Confirmation message
            
        Returns:
            DialogResult with True/False/None result (None = cancelled)
        """
        try:
            self._ensure_root()
            result = messagebox.askyesnocancel(title, message)
            self.logger.info(f"Confirmation dialog result: {result}")
            return DialogResult(success=True, value=result, cancelled=(result is None))
        
        except Exception as e:
            error_msg = f"Confirmation dialog failed: {str(e)}"
            self.logger.error(error_msg)
            return DialogResult(success=False, value=error_msg)


class InputDialogs:
    """User input and data entry dialogs."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._root = None
    
    def _ensure_root(self):
        """Ensure tkinter root window exists."""
        if self._root is None:
            self._root = tk.Tk()
            self._root.withdraw()  # Hide the root window
    
    def get_string(self, 
                  title: str, 
                  prompt: str, 
                  initial_value: str = "") -> DialogResult:
        """
        Get string input from user.
        
        Args:
            title: Dialog title
            prompt: Input prompt
            initial_value: Initial value in input field
            
        Returns:
            DialogResult with string input
        """
        try:
            self._ensure_root()
            result = simpledialog.askstring(title, prompt, initialvalue=initial_value)
            if result is not None:
                self.logger.info(f"String input received: {len(result)} characters")
                return DialogResult(success=True, value=result)
            else:
                return DialogResult(success=False, cancelled=True)
        
        except Exception as e:
            error_msg = f"String input dialog failed: {str(e)}"
            self.logger.error(error_msg)
            return DialogResult(success=False, value=error_msg)
    
    def get_integer(self, 
                   title: str, 
                   prompt: str, 
                   initial_value: int = 0,
                   min_value: Optional[int] = None,
                   max_value: Optional[int] = None) -> DialogResult:
        """
        Get integer input from user.
        
        Args:
            title: Dialog title
            prompt: Input prompt
            initial_value: Initial value in input field
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            
        Returns:
            DialogResult with integer input
        """
        try:
            self._ensure_root()
            result = simpledialog.askinteger(
                title, 
                prompt, 
                initialvalue=initial_value,
                minvalue=min_value,
                maxvalue=max_value
            )
            if result is not None:
                self.logger.info(f"Integer input received: {result}")
                return DialogResult(success=True, value=result)
            else:
                return DialogResult(success=False, cancelled=True)
        
        except Exception as e:
            error_msg = f"Integer input dialog failed: {str(e)}"
            self.logger.error(error_msg)
            return DialogResult(success=False, value=error_msg)
    
    def get_float(self, 
                 title: str, 
                 prompt: str, 
                 initial_value: float = 0.0,
                 min_value: Optional[float] = None,
                 max_value: Optional[float] = None) -> DialogResult:
        """
        Get float input from user.
        
        Args:
            title: Dialog title
            prompt: Input prompt
            initial_value: Initial value in input field
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            
        Returns:
            DialogResult with float input
        """
        try:
            self._ensure_root()
            result = simpledialog.askfloat(
                title, 
                prompt, 
                initialvalue=initial_value,
                minvalue=min_value,
                maxvalue=max_value
            )
            if result is not None:
                self.logger.info(f"Float input received: {result}")
                return DialogResult(success=True, value=result)
            else:
                return DialogResult(success=False, cancelled=True)
        
        except Exception as e:
            error_msg = f"Float input dialog failed: {str(e)}"
            self.logger.error(error_msg)
            return DialogResult(success=False, value=error_msg)


class PreviewDialog:
    """Document preview dialog for showing generated content."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def show_text_preview(self, 
                         title: str, 
                         content: str,
                         width: int = 100,
                         height: int = 30) -> DialogResult:
        """
        Show a preview of text content.
        
        Args:
            title: Dialog title
            content: Text content to preview
            width: Dialog width in characters
            height: Dialog height in lines
            
        Returns:
            DialogResult indicating success
        """
        try:
            root = tk.Tk()
            root.title(title)
            root.geometry(f"{width * 8}x{height * 20}")
            
            # Create text widget with scrollbars
            frame = tk.Frame(root)
            frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            text_widget = tk.Text(frame, wrap=tk.WORD, width=width, height=height)
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=text_widget.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            text_widget.config(yscrollcommand=scrollbar.set)
            
            # Insert content
            text_widget.insert(tk.END, content)
            text_widget.config(state=tk.DISABLED)  # Make read-only
            
            # Add close button
            button_frame = tk.Frame(root)
            button_frame.pack(pady=5)
            
            close_button = tk.Button(button_frame, text="Close", command=root.destroy)
            close_button.pack()
            
            # Center the window
            root.update_idletasks()
            x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
            y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
            root.geometry(f"+{x}+{y}")
            
            root.mainloop()
            
            self.logger.info(f"Showed preview dialog: {title}")
            return DialogResult(success=True)
        
        except Exception as e:
            error_msg = f"Preview dialog failed: {str(e)}"
            self.logger.error(error_msg)
            return DialogResult(success=False, value=error_msg)


class ProgressDialog:
    """Progress tracking dialog for long-running operations."""
    
    def __init__(self, title: str = "Processing..."):
        self.title = title
        self.logger = logging.getLogger(__name__)
        self.root = None
        self.progress_var = None
        self.status_var = None
        self.cancelled = False
    
    def show(self, max_value: int = 100) -> bool:
        """
        Show the progress dialog.
        
        Args:
            max_value: Maximum progress value
            
        Returns:
            True if dialog was created successfully
        """
        try:
            import tkinter.ttk as ttk
            
            self.root = tk.Tk()
            self.root.title(self.title)
            self.root.geometry("400x150")
            self.root.resizable(False, False)
            
            # Progress bar
            self.progress_var = tk.DoubleVar()
            progress_bar = ttk.Progressbar(
                self.root, 
                variable=self.progress_var, 
                maximum=max_value,
                length=350
            )
            progress_bar.pack(pady=20)
            
            # Status label
            self.status_var = tk.StringVar(value="Starting...")
            status_label = tk.Label(self.root, textvariable=self.status_var)
            status_label.pack(pady=5)
            
            # Cancel button
            cancel_button = tk.Button(
                self.root, 
                text="Cancel", 
                command=self._cancel
            )
            cancel_button.pack(pady=10)
            
            # Center the window
            self.root.update_idletasks()
            x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
            y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
            self.root.geometry(f"+{x}+{y}")
            
            self.root.protocol("WM_DELETE_WINDOW", self._cancel)
            
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to create progress dialog: {str(e)}")
            return False
    
    def update(self, value: Union[int, float], status: str = ""):
        """
        Update progress dialog.
        
        Args:
            value: Current progress value
            status: Status message
        """
        if self.root and not self.cancelled:
            try:
                if self.progress_var:
                    self.progress_var.set(value)
                
                if status and self.status_var:
                    self.status_var.set(status)
                
                self.root.update_idletasks()
            
            except Exception as e:
                self.logger.warning(f"Failed to update progress dialog: {str(e)}")
    
    def close(self):
        """Close the progress dialog."""
        if self.root:
            try:
                self.root.destroy()
                self.root = None
            except Exception:
                pass
    
    def _cancel(self):
        """Handle cancel button click."""
        self.cancelled = True
        self.close()
    
    def is_cancelled(self) -> bool:
        """Check if dialog was cancelled."""
        return self.cancelled


# Convenience functions for common dialog operations
def select_input_file(title: str = "Select Input File") -> Optional[Path]:
    """Convenience function for selecting an input file."""
    dialogs = FileDialogs()
    result = dialogs.select_file(
        title=title,
        file_types=[
            ("Data Files", "*.csv;*.json;*.xlsx;*.xls"),
            ("CSV Files", "*.csv"),
            ("JSON Files", "*.json"),
            ("Excel Files", "*.xlsx;*.xls"),
            ("All Files", "*.*")
        ]
    )
    return result.value if result.success else None


def select_output_directory(title: str = "Select Output Directory") -> Optional[Path]:
    """Convenience function for selecting an output directory."""
    dialogs = FileDialogs()
    result = dialogs.select_directory(title=title)
    return result.value if result.success else None


def select_template_file(title: str = "Select Template File") -> Optional[Path]:
    """Convenience function for selecting a template file."""
    dialogs = FileDialogs()
    result = dialogs.select_file(
        title=title,
        file_types=[
            ("Template Files", "*.md;*.txt;*.html"),
            ("Markdown Files", "*.md"),
            ("Text Files", "*.txt"),
            ("HTML Files", "*.html"),
            ("All Files", "*.*")
        ]
    )
    return result.value if result.success else None


def confirm_operation(title: str, message: str) -> bool:
    """Convenience function for confirmation dialogs."""
    dialogs = MessageDialogs()
    result = dialogs.confirm(title, message)
    return result.value if result.success else False


def show_error_message(title: str, message: str) -> None:
    """Convenience function for error messages."""
    dialogs = MessageDialogs()
    dialogs.show_error(title, message)


def show_info_message(title: str, message: str) -> None:
    """Convenience function for info messages."""
    dialogs = MessageDialogs()
    dialogs.show_info(title, message)
