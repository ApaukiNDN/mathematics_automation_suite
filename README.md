# mathematics_automation_suite
A localized, AI-driven pipeline that automates the generation and typesetting of mathematical solutions and pedagogical study guides. Designed to process raw math problems into compilable LaTeX, outputting both rigorous solution sets and Socratic-method scaffolding modules.
Overview
This suite eliminates the manual formatting overhead of multivariable calculus and linear algebra by chaining Google's Gemini API with local LaTeX compilers. It allows educators and students to process documents via native macOS Quick Actions, instantly outputting perfectly formatted PDFs and study modules optimized for AI ingestion tools like NotebookLM.
Architecture & Scripts
generate_scaffold.py (The Pedagogical Engine)
Takes an existing mathematical PDF and utilizes a custom Socratic prompt via the Gemini 3.5 Flash Lite model to generate a tiered study guide.
⚬	Evaluates documents using the GROW framework to generate Conceptual, Algorithmic, and Visual scaffolding hints.
⚬	Forces outputs into strictly compilable LaTeX code with dynamic preamble generation.
⚬	Automatically routes the .tex output through local pdflatex for final rendering.
latex_test.py (The Formatting Engine)
Parses raw math inputs and compiles them into clean, typeset PDF answer keys.
⚬	Handles multi-step algebraic work and 3D geometry notation.
⚬	Outputs standardized PDFs directly to the source directory without manual LaTeX authoring.
Prerequisites
⚬	macOS environment (built for Apple Shortcuts integration).
⚬	Python 3.10+
⚬	A local TeX distribution (e.g., MacTeX) with pdflatex configured in your system PATH.
⚬	Gemini API Key (Gemini 3.5 Flash Lite).
Installation
	1.)	Clone the repository:
  git clone https://github.com/ApaukiNDN/mathematics_automation_suite.git
cd mathematics_automation_suite

  2.) Install Python Dependencies
pip3 install python-dotenv google-genai

  3.)Secure API Credentials:
Create a local .env file in the project root to securely store your API key. This is ignored by Git via .gitignore.
  echo 'GEMINI_API_KEY="your_api_key_here"' > .env

  4.) Usage
This suite is designed to be run as a background process via a macOS Quick Action.
	a.	Create a Quick Action in Apple Shortcuts configured to receive files (PDFs).
	b.	Set the shell script to pass the file path to the Python environment:
  export GEMINI_API_KEY="your_api_key_here"
/usr/bin/python3 /path/to/repo/generate_scaffold.py "$1"
	c.	Right-click any PDF math document in Finder, select your Quick Action, and the automated compilation will handle the rest.

License
MIT License
  
  
