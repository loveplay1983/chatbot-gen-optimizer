from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)

# def optimize_text(raw_text):
#     # Remove unprintable characters, allow newlines, tabs, and spaces for indentation
#     cleaned = "".join(c for c in raw_text if c.isprintable() or c in "\n\t ")
    
#     # Replace LaTeX-style math delimiters with Markdown math delimiters
#     cleaned = cleaned.replace(r"\( ", "$").replace(r" \)", "$")  # Inline math
#     cleaned = cleaned.replace(r"\[", "$$").replace(r"\]", "$$")  # Display math
    
#     # Split into lines and preserve indentation
#     lines = cleaned.splitlines()
#     optimized_lines = []
#     for line in lines:
#         # Only remove trailing whitespace, keep leading indentation
#         line = line.rstrip()
#         if line:  # Skip empty lines but preserve indentation in non-empty ones
#             optimized_lines.append(line)
    
#     # Join lines and remove trailing newlines
#     return "\n".join(optimized_lines).rstrip()


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




# def punct_replace(match):
#     prev_pos = match.start() - 1
#     if prev_pos >= 0:
#         prev_char = match.string[prev_pos]
#     else:
#         prev_char = ''
#     punct = match.group(1)
#     next_char = match.group(2)
#     if punct == '.' and prev_char.isdigit() and next_char.isdigit():
#         return punct + next_char
#     else:
#         return punct + ' ' + next_char

# def optimize_text(raw_text):
#     # Remove unprintable characters, allow newlines, tabs, and spaces for indentation
#     cleaned = "".join(c for c in raw_text if c.isprintable() or c in "\n\t ")
    
#     # Common misspellings in LLM/math content (expand this dict as needed)
#     common_corrections = {
#         'intergral': 'integral',
#         'summation': 'sum',  # Contextual, but common redundancy
#         'equasion': 'equation',
#     }
    
#     # Function to process math content: strip whitespace, fix artifacts -- NO underscore escape
#     def process_math_content(content):
#         content = content.strip()
#         content = content.replace(" ;=; ", " = ")
#         content = content.replace(";", "=")  
#         content = re.sub(r'(\w|\}|\d)\s*,\s*(\\log|\\sum|\\frac|\\big)', r'\1 \2', content)
#         content = re.sub(r'([=+\-*/])\1+', r'\1', content)
#         return content
    
#     # Function to process non-math text content
#     def process_text_content(content):
#         lines = content.splitlines()
#         processed_lines = []
#         for line in lines:
#             line = re.sub(r' +', ' ', line)
#             for wrong, correct in common_corrections.items():
#                 line = re.sub(r'\b' + re.escape(wrong) + r'\b', correct, line, flags=re.IGNORECASE)
#             line = line.replace("_", "\\_")
#             line = re.sub(r'\s+([.,!?])', r'\1', line)
#             line = re.sub(r'([.,!?])\1+', r'\1', line)
#             line = re.sub(r'([.,!?])([^\s])', punct_replace, line)
#             processed_lines.append(line)
#         content = '\n'.join(processed_lines)
#         # Skip sentence deduplication to preserve paragraph structure
#         # Check for unbalanced symbols (warn only)
#         def check_balance(symbol_pairs, text):
#             for open_sym, close_sym in symbol_pairs:
#                 if text.count(open_sym) != text.count(close_sym):
#                     print(f"Warning: Unbalanced {open_sym}{close_sym} in text: '{text[:50]}...'")
#         check_balance([('(', ')'), ('[', ']'), ('{', '}')], content)
#         return content
    
#     # Replace standard LaTeX delimiters
#     def replace_latex_math(match):
#         if match.group(1) is not None:  # Inline math
#             content = process_math_content(match.group(1))
#             return f"${content}$"
#         elif match.group(2) is not None:  # Display math
#             content = process_math_content(match.group(2))
#             return f"$${content}$$"
    
#     pattern_latex = re.compile(r"\\\((.*?)\\\)|\\\[([\s\S]*?)\\\]", re.DOTALL)
#     optimized = re.sub(pattern_latex, replace_latex_math, cleaned)
    
#     # Math check pattern (stricter, without ambiguous = < >)
#     math_check_pattern = r'\\[a-zA-Z]+|_|\^|\{|\}|\\in|\\sum|\\log|\\big|\\hat|\\frac'
    
#     # Handle ChatGPT-style display math: [ math ]
#     def replace_display_chatgpt(match):
#         content = match.group(1)
#         if re.search(math_check_pattern, content):
#             content = process_math_content(content)
#             return f"$${content}$$"
#         else:
#             return process_text_content(match.group(0))
    
#     pattern_display = re.compile(r"\[\s*([\s\S]*?)\s*(?<!\\big)\]", re.DOTALL)
    
#     # Handle ChatGPT-style inline math: ( math )
#     def replace_inline_chatgpt(match):
#         content = match.group(1)
#         if len(content) > 100 or not content.strip():
#             return match.group(0)
#         if '$' in content:
#             return match.group(0)
#         stripped_content = content.strip()
#         if stripped_content.isupper() and len(stripped_content) > 1:
#             return match.group(0)
#         has_math_symbols = re.search(math_check_pattern, content)
#         is_short_variable = (len(content.split()) == 1 and len(content) < 4)
#         if has_math_symbols or is_short_variable:
#             content = process_math_content(content)
#             return f"${content}$"
#         else:
#             return process_text_content(match.group(0))
    
#     pattern_inline = re.compile(r"\(\s*([\s\S]*?)\s*\)", re.DOTALL)
    
#     # Split for display $$ to protect math
#     parts = re.split(r'(\$\$)', optimized)
#     is_math = False
#     optimized_parts = []
#     for part in parts:
#         if part == '$$':
#             is_math = not is_math
#             optimized_parts.append(part)
#         else:
#             if not is_math:
#                 # Split for inline $ to protect math
#                 subparts = re.split(r'(\$)', part)
#                 is_inline = False
#                 processed_subparts = []
#                 for subpart in subparts:
#                     if subpart == '$':
#                         is_inline = not is_inline
#                         processed_subparts.append(subpart)
#                     else:
#                         if not is_inline:
#                             # Apply in pure text only
#                             subpart = re.sub(pattern_display, replace_display_chatgpt, subpart)
#                             subpart = re.sub(pattern_inline, replace_inline_chatgpt, subpart)
#                             subpart = process_text_content(subpart)
#                         processed_subparts.append(subpart)
#                 part = ''.join(processed_subparts)
#             optimized_parts.append(part)
#     optimized = ''.join(optimized_parts)
    
#     # Final line clean
#     lines = optimized.splitlines()
#     optimized_lines = [line.rstrip() for line in lines]
#     return "\n".join(optimized_lines).rstrip()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get raw text from the form input
        raw_text = request.form.get("input_text", "")
        optimized = optimize_text(raw_text)
        return jsonify({"optimized": optimized})
    # Render the HTML template for GET requests
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)