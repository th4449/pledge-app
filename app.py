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
    """Reads the list of already researched companies from the memory file."""
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r") as f:
        return [line.strip() for line in f.readlines()]

def add_company_to_memory(company_name):
    """Appends a new company to the memory file."""
    with open(MEMORY_FILE, "a") as f:
        f.write(company_name + "\n")

# --- Gemini Model Setup ---
def setup_gemini_model():
    """Sets up and returns the Gemini model by prompting for the key."""
    try:
        print_header("API Key Required")
        api_key = input("Please paste your Gemini API key and press Enter: ")
        if not api_key:
            print("🔴 No API Key provided. Cannot start server.")
            return None
        print("✅ Key received. Configuring Gemini...")
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        print(f"🔴 ERROR: Could not configure Gemini. Details: {e}")
        return None

model = None

def ask_gemini(prompt):
    """A helper function to send a prompt to Gemini."""
    if model is None: return "Error: Gemini model not configured."
    try:
        response = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(temperature=0.8))
        return response.text
    except Exception as e:
        return f"🔴 ERROR: Could not get a response from Gemini. Details: {e}"

# --- Flask Routes ---

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate_initial_list", methods=["POST"])
def generate_initial_list():
    """Finds companies, excluding any that have already been researched."""
    researched_list = read_researched_companies()
    researched_names = ", ".join(researched_list) if researched_list else "None"
    
    prompt = f"""
    List 10 major multinational companies known for significant lobbying efforts in the United States. Your list MUST include at least four companies whose headquarters are in Europe.
    Do not include any of the following companies in your list: {researched_names}

    For each company, provide the following on a new line, separated by '||':
    1. The company name.
    2. The company's primary industry and country of origin.
    """
    response_text = ask_gemini(prompt)
    companies = [line.strip() for line in response_text.split('\n') if '||' in line]
    return jsonify(companies=companies)

@app.route("/investigate_company", methods=["POST"])
def investigate_company():
    """Performs a detailed investigation on a selected company."""
    data = request.json
    company_name = data.get("company")
    add_company_to_memory(company_name)
    
    # --- MODIFIED PROMPT WITH NEW RESEARCH QUESTIONS ---
    investigation_prompt = f"""
    Act as a research analyst. For '{company_name}', investigate three specific areas and provide a concise summary for each, including source URLs.

    1.  **Environmental Hypocrisy:** While the company publicly promotes sustainability, find one sourced example of its PAC donating to politicians who voted against climate agreements or for fossil fuel subsidies.
    2.  **Labor Practices:** Find one sourced report from a reputable news outlet or NGO linking the company to labor rights controversies in its international supply chain.
    3.  **European Tax Strategy:** Find one sourced report detailing the company's use of European tax havens or aggressive tax avoidance strategies.

    If you cannot find specific data for a point, state that clearly. Structure your answer with clear headings.
    """
    details = ask_gemini(investigation_prompt)
    return jsonify(details=details)

@app.route("/reset_memory", methods=["POST"])
def reset_memory():
    """Endpoint to clear the memory file."""
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)
    with open(MEMORY_FILE, "w") as f:
        pass
    return jsonify(status="success", message="Memory has been reset.")

@app.route("/generate_content", methods=["POST"])
def generate_content_endpoint():
    data = request.json
    company_name = data.get("company")
    investigation_results = data.get("investigationResults") # Note: renamed for clarity
    market = data.get("market")
    language = data.get("language")
    
    # --- FINAL, MOST ADVANCED PROMPT ---
    generation_prompt = f"""
    Act as a highly impactful social media strategist for the watchdog group 'Dekleptocracy'. Your tone is sharp, journalistic, and authoritative. You will create a hard-hitting, evidence-based social media campaign.

    **Core Principles:**
    - **Narrative Focus:** Every post should tell a small story about hypocrisy or consequence.
    - **Evidence is everything:** Every factual claim MUST be followed by its source URL.
    - **Audience Action:** Every campaign should empower the local audience with specific actions.

    **Campaign Details:**
    - **Target Company:** {company_name}
    - **Target Audience:** Citizens of {market}.
    - **Key Research Findings:** "{investigation_results}"

    **AI Research Task (Required for context):**
    1.  **Find Competitors:** Identify one or two major, local competitors to {company_name} within {market}.

    **Generate the following assets in both English and {language}:**

    1.  **X (Twitter) Thread (4-6 tweets):**
        - **Tweet 1 (The Hook):** Start with the company's connection to the local market. Frame it as a story. "While {company_name} operates in {market}, their political spending in the US tells a different story. (Source from user research)."
          - *Image Suggestion:* A high-quality photo of the company's product or presence in {market}, with the 'Dekleptocracy' logo watermarked.
        - **Tweet 2 (Environmental Hypocrisy):** "They talk about sustainability in Europe. But in the US, their money funds politicians who vote against climate action. (Source from investigation results)."
          - *Image Suggestion:* A split-screen image: on one side, a glossy picture from the company's sustainability report; on the other, a photo of a polluting factory or oil rig.
        - **Tweet 3 (Labor/Tax Hypocrisy):** "They benefit from our economy. But do they treat their global workers ethically and pay their fair share of taxes? Reports suggest otherwise. (Source from investigation results)."
          - *Image Suggestion:* An infographic with a damning quote from an NGO report about the company's labor or tax practices.
        - **Tweet 4 (The Local Choice):** "As a consumer in {market}, you have a choice. Companies like [Competitor Name 1] and [Competitor Name 2] operate here too."
          - *Image Suggestion:* A clean graphic showing the logos of the local competitors.
        - **Tweet 5 (The Call to Action):** "Does {company_name}'s political agenda align with your values? Let them know. Let your pension fund know."
          - *Image Suggestion:* A powerful photo of people protesting or engaged in community action.
        - **Tweet 6 (The Donation):** "Support the fight for transparency. Donate to Dekleptocracy: https://secure.actblue.com/donate/dekleptocracy-action-social-media"
          - *Image Suggestion:* The 'Dekleptocracy' logo and QR code.

    2.  **Pictory Video Script:**
        - **Concept:** An ominous, 30-second "follow the money" exposé.
        - **Scene 1 (The Local Presence):** VISUAL: Beautiful, user-generated-style footage of {company_name}'s products/stores in {market}. TEXT: "{company_name}. They're part of our lives in {market}."
        - **Scene 2 (The Hidden Action):** VISUAL: A graphic showing money flowing from the company logo to a generic, imposing government building labeled "U.S. Lobbying." TEXT: "But where does their money go in America?"
        - **Scene 3 (The Contradiction):** VISUAL: A rapid, split-screen montage. Left side: The company's greenwashing ads or happy worker photos. Right side: Symbolic footage of environmental damage or factory workers in poor conditions (based on investigation results). TEXT: "Their marketing says one thing. Their political funding says another."
        - **Scene 4 (The Empowered Consumer):** VISUAL: A hand in a supermarket decisively choosing a competitor's product over the {company_name} product. TEXT: "You have the power to choose."
        - **Scene 5 (The CTA):** VISUAL: The 'Dekleptocracy' logo and QR code. TEXT: "Demand corporate accountability. Donate to Dekleptocracy."
    """
    
    final_content = ask_gemini(generation_prompt)
    return jsonify(content=final_content)

if __name__ == "__main__":
    model = setup_gemini_model()
    if model:
        print("✅ Gemini configured successfully. Starting Flask server...")
        app.run(debug=True, port=5001)
