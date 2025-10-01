# import sys
# import re
# from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
#                                QWidget, QTextEdit, QPushButton)
# from PySide6.QtGui import QClipboard
# from PySide6.QtCore import Qt

# def optimize_text(raw_text):
#     # Remove unprintable characters, allow newlines, tabs, and spaces for indentation
#     cleaned = "".join(c for c in raw_text if c.isprintable() or c in "\n\t ")
    
#     # Function to process math content: strip whitespace and escape underscores
#     def process_math_content(content):
#         content = content.strip()
#         escaped_content = content.replace("_", "\\_")
#         return escaped_content
    
#     # Function to replace LaTeX math delimiters with Markdown delimiters
#     def replace_math(match):
#         if match.group(1) is not None:  # Inline math
#             content = process_math_content(match.group(1))
#             return f"${content}$"
#         elif match.group(2) is not None:  # Display math
#             content = process_math_content(match.group(2))
#             return f"$${content}$$"
    
#     # Regular expression to match LaTeX inline and display math
#     pattern = re.compile(r"\\\((.*?)\\\)|\\\[([\s\S]*?)\\\]", re.DOTALL)
    
#     # Replace all math expressions
#     optimized = re.sub(pattern, replace_math, cleaned)
    
#     # Split into lines, remove trailing whitespace, preserve blank lines
#     lines = optimized.splitlines()
#     optimized_lines = [line.rstrip() for line in lines]
    
#     # Join lines and remove trailing newlines
#     return "\n".join(optimized_lines).rstrip()

# class TextOptimizerWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Chatbot Text Optimizer")
#         self.setGeometry(100, 100, 600, 400)
        
#         # Main widget and layout
#         main_widget = QWidget()
#         self.setCentralWidget(main_widget)
#         layout = QVBoxLayout(main_widget)
        
#         # Input field
#         self.input_field = QTextEdit()
#         self.input_field.setPlaceholderText("Paste chatbot text here...")
#         layout.addWidget(self.input_field)
        
#         # Output field
#         self.output_field = QTextEdit()
#         self.output_field.setPlaceholderText("Optimized Markdown text will appear here...")
#         self.output_field.setReadOnly(True)
#         layout.addWidget(self.output_field)
        
#         # Buttons layout
#         button_layout = QHBoxLayout()
#         self.copy_button = QPushButton("Copy Output")
#         self.clear_button = QPushButton("Clear")
#         button_layout.addWidget(self.copy_button)
#         button_layout.addWidget(self.clear_button)
#         layout.addLayout(button_layout)
        
#         # Connect signals
#         self.input_field.textChanged.connect(self.optimize)
#         self.copy_button.clicked.connect(self.copy_to_clipboard)
#         self.clear_button.clicked.connect(self.clear_fields)
        
#         # Styling with gray background for read-only output field
#         self.setStyleSheet("""
#             QMainWindow {
#                 background-color: #f0f0f0;
#             }
#             QTextEdit {
#                 border: 1px solid #ccc;
#                 border-radius: 5px;
#                 padding: 5px;
#                 font-family: Arial;
#                 font-size: 14px;
#                 background-color: white;
#             }
#             QTextEdit[readOnly="true"] {
#                 background-color: #f9f9f9;  /* Light gray for read-only field */
#             }
#             QPushButton {
#                 background-color: #4CAF50;
#                 color: white;
#                 padding: 8px;
#                 border: none;
#                 border-radius: 5px;
#                 font-size: 14px;
#             }
#             QPushButton:hover {
#                 background-color: #45a049;
#             }
#             QPushButton:pressed {
#                 background-color: #3d8b40;
#             }
#         """)
    
#     def optimize(self):
#         raw_text = self.input_field.toPlainText()
#         optimized = optimize_text(raw_text)
#         self.output_field.setPlainText(optimized)
    
#     def copy_to_clipboard(self):
#         clipboard = QApplication.clipboard()
#         clipboard.setText(self.output_field.toPlainText())
    
#     def clear_fields(self):
#         self.input_field.clear()
#         self.output_field.clear()

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = TextOptimizerWindow()
#     window.show()
#     sys.exit(app.exec())











import sys
import re
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                               QWidget, QTextEdit, QPushButton)
from PySide6.QtGui import QClipboard
from PySide6.QtCore import Qt

def optimize_text(raw_text):
    # Remove unprintable characters, allow newlines, tabs, and spaces for indentation
    cleaned = "".join(c for c in raw_text if c.isprintable() or c in "\n\t ")
    
    # Function to process math content: strip whitespace, fix artifacts, escape underscores
    def process_math_content(content):
        content = content.strip()
        # Fix common copy-paste artifacts from ChatGPT-like content
        content = content.replace(" ;=; ", " = ")
        content = content.replace(";", "=")  # Clean up any leftover semicolons in equations
        # Remove commas that are likely typos in math expressions (e.g., y_i , \log -> y_i \log)
        content = re.sub(r'(\w|\}|\d)\s*,\s*(\\log|\\sum|\\frac|\\big)', r'\1 \2', content)
        # Escape underscores for Markdown compatibility
        escaped_content = content.replace("_", "\\_")
        return escaped_content
    
    # Function to replace standard LaTeX math delimiters (used in Grok-like content)
    def replace_latex_math(match):
        if match.group(1) is not None:  # Inline math
            content = process_math_content(match.group(1))
            return f"${content}$"
        elif match.group(2) is not None:  # Display math
            content = process_math_content(match.group(2))
            return f"$${content}$$"
    
    # First, handle standard LaTeX delimiters (\( \), \[ \])
    pattern_latex = re.compile(r"\\\((.*?)\\\)|\\\[([\s\S]*?)\\\]", re.DOTALL)
    optimized = re.sub(pattern_latex, replace_latex_math, cleaned)
    
    # Now, handle ChatGPT-style display math: [ math ]
    def replace_display_chatgpt(match):
        content = match.group(1)
        # Check if content likely contains math (e.g., LaTeX commands, symbols)
        if re.search(r'\\[a-zA-Z]+|_|\^|\{|\}|=|<|>|\\in|\\sum|\\log|\\big|\\hat|\\frac', content):
            content = process_math_content(content)
            return f"$${content}$$"
        else:
            # If not math, leave unchanged
            return match.group(0)
    
    pattern_display = re.compile(r"\[\s*([\s\S]*?)\s*(?<!\\big)\]", re.DOTALL)
    optimized = re.sub(pattern_display, replace_display_chatgpt, optimized)
    
    # Handle ChatGPT-style inline math: ( math )
    def replace_inline_chatgpt(match):
        content = match.group(1)
        # Skip if too long or empty
        if len(content) > 100 or not content.strip():
            return match.group(0)
        # Skip if already processed (contains $)
        if '$' in content:
            return match.group(0)
        # Skip abbreviations like (CE)
        stripped_content = content.strip()
        if stripped_content.isupper() and len(stripped_content) > 1:
            return match.group(0)
        # Check if likely math: either has specific math symbols or is short single-word (e.g., variables like y, k)
        has_math_symbols = re.search(r'\\[a-zA-Z]+|_|\^|\{|\}|=|<|>|\\in|\\sum|\\log|\\big|\\hat|\\frac', content)
        is_short_variable = (len(content.split()) == 1 and len(content) < 10)
        if has_math_symbols or is_short_variable:
            content = process_math_content(content)
            return f"${content}$"
        else:
            # If not math, leave unchanged
            return match.group(0)
    
    pattern_inline = re.compile(r"\(\s*([\s\S]*?)\s*\)", re.DOTALL)
    
    # Apply inline replacement only outside of $$ ... $$
    parts = re.split(r'(\$\$)', optimized)
    is_math = False
    optimized_parts = []
    for part in parts:
        if part == '$$':
            is_math = not is_math
            optimized_parts.append(part)
        else:
            if not is_math:
                part = re.sub(pattern_inline, replace_inline_chatgpt, part)
            optimized_parts.append(part)
    optimized = ''.join(optimized_parts)
    
    # Split into lines, remove trailing whitespace, preserve blank lines
    lines = optimized.splitlines()
    optimized_lines = [line.rstrip() for line in lines]
    
    # Join lines and remove trailing newlines
    return "\n".join(optimized_lines).rstrip()

class TextOptimizerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chatbot Text Optimizer")
        self.setGeometry(100, 100, 600, 400)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Input field
        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("Paste chatbot text here...")
        layout.addWidget(self.input_field)
        
        # Output field
        self.output_field = QTextEdit()
        self.output_field.setPlaceholderText("Optimized Markdown text will appear here...")
        self.output_field.setReadOnly(True)
        layout.addWidget(self.output_field)
        
        # Buttons layout
        button_layout = QHBoxLayout()
        self.copy_button = QPushButton("Copy Output")
        self.clear_button = QPushButton("Clear")
        button_layout.addWidget(self.copy_button)
        button_layout.addWidget(self.clear_button)
        layout.addLayout(button_layout)
        
        # Connect signals
        self.input_field.textChanged.connect(self.optimize)
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        self.clear_button.clicked.connect(self.clear_fields)
        
        # Styling with gray background for read-only output field
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                font-family: Arial;
                font-size: 14px;
                background-color: white;
            }
            QTextEdit[readOnly="true"] {
                background-color: #f9f9f9;  /* Light gray for read-only field */
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
    
    def optimize(self):
        raw_text = self.input_field.toPlainText()
        optimized = optimize_text(raw_text)
        self.output_field.setPlainText(optimized)
    
    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.output_field.toPlainText())
    
    def clear_fields(self):
        self.input_field.clear()
        self.output_field.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TextOptimizerWindow()
    window.show()
    sys.exit(app.exec())