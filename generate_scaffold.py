import sys
import os
import subprocess
from google import genai

# 1. Capture the file path from your macOS Quick Action
if len(sys.argv) < 2:
    print("CRITICAL ERROR: No file path provided. Make sure to run this via the Quick Action.", file=sys.stderr)
    sys.exit(1)
    
pdf_file_path = sys.argv[1]

# 2. Securely Initialize the Gemini Client 
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("CRITICAL ERROR: API key missing. Ensure the Shortcut is exporting GEMINI_API_KEY.", file=sys.stderr)
    sys.exit(1)

try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    print(f"CRITICAL ERROR initializing client: {e}", file=sys.stderr)
    sys.exit(1)

# 3. Upload the PDF directly to preserve math formatting
try:
    uploaded_file = client.files.upload(file=pdf_file_path)
except Exception as e:
    print(f"CRITICAL ERROR uploading file '{pdf_file_path}': {e}", file=sys.stderr)
    sys.exit(1)

# 4. The Socratic Tutor & LaTeX Prompt
socratic_prompt = r"""
You are an expert mathematics tutor. Analyze the uploaded document.

CRITICAL INSTRUCTIONS FOR OUTPUT FORMAT:
1. You MUST output ONLY a valid, compilable LaTeX document.
2. The very first text of your response MUST be \documentclass[12pt]{article}.
3. The very last text of your response MUST be \end{document}.
4. Include \usepackage{amsmath, amssymb, geometry, enumitem}.
5. Set \geometry{letterpaper, margin=1in}.
6. DO NOT use markdown bolding (**text**) or markdown headers (##). Use LaTeX commands like \section*{} and \textbf{}.
7. Ensure all math is enclosed in $ for inline or $$ for display math.

PEDAGOGICAL INSTRUCTIONS:
- If the document is a LESSON PLAN: Summarize core objectives and create a structured study guide with GROW framework scaffolding for the tutor to use.
- If the document is an EXAM or TEST: DO NOT SOLVE THE PROBLEMS. Group problems by mathematical concept. Build a study guide containing 3 tiered scaffolding hints (Conceptual, Algorithmic, Visual) that a tutor can use to coach a student without giving away the final answer.
"""

# 5. Generate Content using the Gemini 3.5 Flash Lite model
try:
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=[uploaded_file, socratic_prompt]
    )
except Exception as e:
    print(f"CRITICAL ERROR generating content: {e}", file=sys.stderr)
    sys.exit(1)

# 6. Save the output to a new .tex file next to the original PDF
try:
    target_dir = os.path.dirname(os.path.abspath(pdf_file_path))
    base_name = os.path.splitext(os.path.basename(pdf_file_path))[0]
    tex_filepath = os.path.join(target_dir, f"{base_name}_TutorGuide.tex")

    with open(tex_filepath, "w", encoding="utf-8") as f:
        f.write(response.text)
except Exception as e:
    print(f"CRITICAL ERROR writing .tex file: {e}", file=sys.stderr)
    sys.exit(1)
    
# 7. Automatically compile to PDF using pdflatex
try:
    res = subprocess.run(
        [
            "/Library/TeX/texbin/pdflatex",
            "-interaction=nonstopmode",
            f"-output-directory={target_dir}",
            tex_filepath
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if res.returncode != 0:
        print(f"LaTeX file written, but pdflatex failed:\n{res.stdout[-500:]}", file=sys.stderr)
        sys.exit(1)
except Exception as pdf_err:
    print(f"pdflatex execution failed entirely: {pdf_err}", file=sys.stderr)
    sys.exit(1)
