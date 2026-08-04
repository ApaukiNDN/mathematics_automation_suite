import sys
import os
import subprocess
from google import genai
from google.genai import types

def main():
    pdf_bytes = None
    input_path = None

    # 1. Try reading PDF directly from file path argument ($1)
    if len(sys.argv) > 1 and sys.argv[1].strip():
        candidate_path = sys.argv[1].strip()
        if os.path.exists(candidate_path):
            input_path = os.path.abspath(candidate_path)
            try:
                with open(input_path, "rb") as f:
                    pdf_bytes = f.read()
            except Exception as e:
                print(f"Error reading file directly from path '{input_path}': {e}", file=sys.stderr)

    # 2. Fallback to stdin if no valid file path was supplied or read
    if not pdf_bytes:
        try:
            pdf_bytes = sys.stdin.buffer.read()
        except Exception as e:
            print(f"Error reading stdin stream: {e}", file=sys.stderr)

    # Validate that we successfully retrieved binary data
    if not pdf_bytes:
        print("Error: No PDF input received via file path or stdin.", file=sys.stderr)
        sys.exit(1)

    # 3. Initialize Gemini Client
    try:
        client = genai.Client()
    except Exception as e:
        print(f"Error initializing Gemini Client: {e}", file=sys.stderr)
        sys.exit(1)

    # 4. Wrap PDF bytes in an inline Part object (no file upload required)
    pdf_part = types.Part.from_bytes(
        data=pdf_bytes,
        mime_type="application/pdf"
    )

    # 5. Prompts & System Instructions
    system_instruction = (
        "You are an expert mathematician and LaTeX document creator. Your job is to convert "
        "handwritten or scanned vector calculus problem sets into clean, compiles-without-errors "
        "LaTeX code. Provide complete documents with standard preamble, using packages like "
        "amsmath, amssymb, and geometry. Output ONLY raw LaTeX code without markdown code blocks."
    )
    
    prompt = (
        "Please transcribe and solve the vector calculus problems from the attached PDF snippet. "
        "Show clear, step-by-step mathematical reasoning for each problem."
    )

    # 6. Generate LaTeX output via Gemini API
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[pdf_part, prompt],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2,
            )
        )
        latex_content = response.text
    except Exception as e:
        print(f"Error generating LaTeX output: {e}", file=sys.stderr)
        sys.exit(1)

    # 7. Determine target output directory & filenames
    if input_path:
        target_dir = os.path.dirname(input_path)
        base_name = os.path.splitext(os.path.basename(input_path))[0]
    else:
        # Fallback location if executed without a direct source path
        target_dir = os.path.expanduser("~/Public/LaTex files")
        os.makedirs(target_dir, exist_ok=True)
        base_name = "vector_calc_solution"

    tex_filepath = os.path.join(target_dir, f"{base_name}_solution.tex")
    pdf_filepath = os.path.join(target_dir, f"{base_name}_solution.pdf")

    # Debug logs (printed to stderr so Shortcuts notification catches them)
    print(f"DEBUG: Input Path -> {input_path}", file=sys.stderr)
    print(f"DEBUG: Target Dir -> {target_dir}", file=sys.stderr)
    print(f"DEBUG: Saving Tex -> {tex_filepath}", file=sys.stderr)

    # 8. Write .tex file alongside original input file
    try:
        with open(tex_filepath, "w", encoding="utf-8") as f:
            f.write(latex_content)
        print(f"Successfully saved LaTeX: {tex_filepath}", file=sys.stderr)
    except Exception as e:
        print(f"Error writing .tex file to {tex_filepath}: {e}", file=sys.stderr)
        sys.exit(1)

    # 9. Automatically compile to PDF using pdflatex
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
            print(f"pdflatex compilation warning/error:\n{res.stdout[-500:]}", file=sys.stderr)
        else:
            print(f"SUCCESS: Generated PDF at {pdf_filepath}", file=sys.stderr)
    except Exception as pdf_err:
        print(f"LaTeX file written, but pdflatex execution failed: {pdf_err}", file=sys.stderr)

if __name__ == "__main__":
    main()