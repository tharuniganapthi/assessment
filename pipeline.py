import os
import pdfplumber
import pandas as pd
import google.generativeai as genai
import json
import time

# --- CONFIGURATION ---
# PASTE YOUR GOOGLE GEMINI API KEY HERE (Keep the quotes!)
API_KEY = "AIzaSyABWMNlpsZF5JczXChb-PqafT0ZH5TQQW8"

PDF_FOLDER = "./contracts"
OUTPUT_FILE = "contract_analysis_output.csv"

# Configure Google Gemini
genai.configure(api_key=API_KEY)

def get_working_model():
    """Automatically finds a model that works for your account."""
    print("Searching for available Gemini models...")
    try:
        # List all models available to your API key
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"Found working model: {m.name}")
                # Return the first model that supports text generation
                return genai.GenerativeModel(m.name)
    except Exception as e:
        print(f"Error listing models: {e}")
    
    # Fallback if search fails
    print("Could not auto-detect. Defaulting to 'gemini-1.5-flash'.")
    return genai.GenerativeModel('gemini-1.5-flash')

# Initialize the model using the auto-finder
model = get_working_model()

def extract_text_from_pdf(pdf_path):
    """Reads a PDF and converts it to text."""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return text

def analyze_contract_with_llm(text):
    """Sends text to Gemini to extract clauses and summary."""
    # Truncate text to be safe
    truncated_text = text[:80000] 
    
    prompt = f"""
    You are a legal AI assistant. Analyze the contract text below.
    
    TASK:
    1. Summarize the contract in 100-150 words (Purpose, Key Obligations, Risks).
    2. Extract the 'Termination Clause' (verbatim or summary of condition).
    3. Extract the 'Confidentiality Clause'.
    4. Extract the 'Liability Clause'.
    
    If a clause is not found, return "Not Found".
    
    OUTPUT FORMAT (Strict JSON):
    {{
        "summary": "...",
        "termination_clause": "...",
        "confidentiality_clause": "...",
        "liability_clause": "..."
    }}

    CONTRACT TEXT:
    {truncated_text}
    """

    try:
        response = model.generate_content(prompt)
        # Clean the response to ensure valid JSON (removes ```json ... ``` wrappers)
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception as e:
        print(f"LLM Error: {e}")
        time.sleep(2) 
        return None

def main():
    results = []
    
    if not os.path.exists(PDF_FOLDER):
        print(f"Error: Folder '{PDF_FOLDER}' not found.")
        return

    pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.endswith('.pdf')]
    print(f"Found {len(pdf_files)} contracts. Starting analysis...")

    for i, filename in enumerate(pdf_files):
        print(f"[{i+1}/{len(pdf_files)}] Processing {filename}...")
        file_path = os.path.join(PDF_FOLDER, filename)
        
        raw_text = extract_text_from_pdf(file_path)
        
        if raw_text:
            data = analyze_contract_with_llm(raw_text)
            if data:
                row = {
                    "contract_id": filename,
                    "summary": data.get("summary", ""),
                    "termination_clause": data.get("termination_clause", ""),
                    "confidentiality_clause": data.get("confidentiality_clause", ""),
                    "liability_clause": data.get("liability_clause", "")
                }
                results.append(row)
            # Sleep briefly to avoid rate limits
            time.sleep(4)

    if results:
        df = pd.DataFrame(results)
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"\nSuccess! Results saved to {OUTPUT_FILE}")
    else:
        print("\nNo results were generated.")

if __name__ == "__main__":
    main()