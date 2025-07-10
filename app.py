import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# --- File for storing researched companies ---
MEMORY_FILE = "researched_companies.txt"

# --- Helper Function ---
def print_header(title):
    """Prints a formatted header to the console."""
    print("\n" + "="*50)
    print(f"➡️  {title}")
    print("="*50)

# --- Memory Functions ---
def read_researched_companies():
    if not os.path.exists(MEMORY_FILE): return []
    with open(MEMORY_FILE, "r") as f: return [line.strip() for line in f.readlines()]

def add_company_to_memory(company_name):
    with open(MEMORY_FILE, "a") as f: f.write(company_name + "\n")

# --- Gemini Model Setup ---
def setup_gemini_model():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("🔴 FATAL ERROR: GOOGLE_API_KEY environment variable not set on the server.")
        return None
    try:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        print(f"🔴 ERROR: Could not configure Gemini. Details: {e}")
        return None

model = None

def ask_gemini(prompt):
    if model is None: return "Error: Gemini model not configured."
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"🔴 ERROR: Could not get a response from Gemini. Details: {e}"

# --- Flask Routes ---

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate_initial_list", methods=["POST"])
def generate_initial_list():
    """Uses a completely neutral prompt to test the API connection."""
    # --- FINAL TEST PROMPT ---
    prompt = """
    List three common fruits and their primary color.

    For each fruit, provide the following on a new line, separated by '||':
    1. The fruit name.
    2. Its primary color.
    """
    response_text = ask_gemini(prompt)
    companies = [line.strip() for line in response_text.split('\n') if '||' in line]
    return jsonify(companies=companies)

# All other functions remain the same...
@app.route("/investigate_company", methods=["POST"])
def investigate_company():
    data = request.json
    company_name = data.get("company")
    add_company_to_memory(company_name)
    return jsonify(details=f"Investigation for {company_name} would happen here.")

@app.route("/reset_memory", methods=["POST"])
def reset_memory():
    if os.path.exists(MEMORY_FILE): os.remove(MEMORY_FILE)
    with open(MEMORY_FILE, "w") as f: pass
    return jsonify(status="success", message="Memory has been reset.")

@app.route("/generate_content", methods=["POST"])
def generate_content_endpoint():
    # This function is now simplified for the test
    data = request.json
    return jsonify(content=f"Content generation for {data.get('company')} would happen here.")

if __name__ == "__main__":
    # This part is for local development, it won't run on Render
    try:
        print_header("API Key Required")
        local_api_key = input("Please paste your Gemini API key and press Enter: ")
        if local_api_key: os.environ['GOOGLE_API_KEY'] = local_api_key
    except:
        pass # Silently fail if input is not possible

    model = setup_gemini_model()
    if model:
        print("✅ Gemini configured successfully. Starting Flask server...")
        app.run(debug=True, port=5001)
