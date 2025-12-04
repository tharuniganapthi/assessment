1. Objective
This project implements an automated pipeline to process legal contracts (PDFs) from the CUAD dataset. It utilizes Large Language Models (LLMs) to extract critical clauses (Termination, Confidentiality, Liability) and generate concise summaries of legal obligations and risks.

2. System Architecture (Flow Diagram)
The solution follows a linear Extract-Transform-Load (ETL) workflow, designed for robustness and error recovery.
graph TD
    A[Input: PDF Contracts] -->|pdfplumber| B(Text Extraction)
    B -->|Preprocessing| C{Token Truncation}
    C -->|Prompt Engineering| D[LLM Analysis]
    D -->|Google Gemini Pro| E{JSON Parsing}
    E -->|Success| F[Append to Results]
    E -->|Error/Invalid JSON| G[Log Error & Skip]
    F -->|Pandas| H[Output: CSV File]
3. Approach & Methodology
Data Ingestion
Library: Used pdfplumber for text extraction.

Reasoning: Unlike OCR-based tools, pdfplumber extracts raw text directly from the PDF stream, resulting in higher fidelity and fewer artifacts (like confused characters) which is critical for legal text.

Preprocessing
Token Management: Legal documents can be lengthy. The raw text is truncated to ~80,000 characters before being sent to the LLM. This ensures the payload stays within the model's context window while retaining the majority of the substantive clauses typically found in the body of the agreement.

LLM Strategy
Model: Google Gemini Pro.

Prompt Engineering:

Role-Playing: The model is instructed to act as a "Legal AI Assistant" to set the correct tone and vocabulary.

Strict JSON Output: The prompt explicitly enforces a JSON structure. This allows for programmatic parsing of the results into a structured dataset (CSV) rather than unstructured free text.

Error Handling: The system includes a dynamic model finder (get_working_model) to automatically detect and utilize the best available model version for the user's API key, ensuring high reproducibility.

4. Setup Instructions
Prerequisites
Python 3.8 or higher.

A Google Gemini API Key.

5. Project Structure

/
├── contracts/                   # Directory containing input PDF files
├── pipeline.py                  # Main processing script
├── requirements.txt             # Python dependencies
├── README.md                    # Project documentation
└── contract_analysis_output.csv # Final structured output
