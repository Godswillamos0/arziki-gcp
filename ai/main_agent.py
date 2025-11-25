from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
from typing import Dict, List
from google import genai
import json
import re
from google.oauth2 import service_account

# Load .env file
load_dotenv()

PROJECT_ID = "arziki"  # replace with your project ID
LOCATION = "us-central1"


# --- Store history per user ---
user_histories: Dict[str, List[Dict[str, str]]] = {}


# --- Google GenAI Client ---
def create_client():
    client = genai.Client(
        vertexai={
            "project": PROJECT_ID,
            "location": LOCATION
        }
    )
    return client

def generate_reply(user_id: str, user_message: str) -> str:
    history = user_histories.get(user_id, [])

    client = create_client()

    # Build a single prompt string including history
    prompt_text = ""
    for msg in history:
        if msg["role"] == "user":
            prompt_text += f"User: {msg['content']}\n"
        else:
            prompt_text += f"Bot: {msg['content']}\n"

    prompt_text += f"User: {user_message}\nBot:"

    # Call Gemini 2.0
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt_text
    )

    bot_reply = response.text.strip()

    # Update history for this user
    history.append({"role": "user", "content": user_message})
    history.append({"role": "model", "content": bot_reply})
    user_histories[user_id] = history

    return bot_reply


def predict_demand_v2(input_json: str) -> str:
    # 1. Initialize the new unified Client
    # Setting vertexai=True tells it to use your GCP Project credits/quota
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

    # 3. Define the Prompt
    prompt_text = f"""
You are an expert retail analyst. Analyze the business data below.
For each product, predict 'demand_level' (High, Medium, Low) and provide 'reasoning'.
Most importantly include the business name in the output and, return the results STRICTLY in the following JSON format:
{{
    "business_name": "string",
    "predictions": [
        {{
        "category": "string",
        "product_name": "string",
        "price": float,
        "current_stock": int,
        "predicted_demand": int,
        "demand_level": "High|Medium|Low",
        "reasoning": "string"
        }}
    ]
}}

Data:
{input_json}
"""


    # 4. Generate Content with JSON enforcement
    # The new SDK makes it very easy to enforce JSON output using 'response_mime_type'
    print("Sending data to Gemini (via google-genai SDK)...")
    
    response = client.models.generate_content(
        model="gemini-2.5-pro",  # Using the latest stable model
        contents=[
        {
            "role": "user",
            "parts": [{"text": prompt_text}]
        }
    ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json", 
            temperature=0.2
        )
    )
    print(response.text, "\n --- End of Gemini Response ---\n")
    
    return response.text


def generate_report_html(prediction_json: dict, model_name='gemini-2.5-flash'):
    client = create_client()


    # Convert the combined data to a clean JSON string for the prompt
    analysis_data_str = json.dumps(prediction_json, indent=2)

    prompt = f"""
You are a Professional Report Formatting Engine. Convert the data below into a complete HTML document.

1. Role: Act as a professional analyst. Interpret the data to create a narrative for the report, focusing on market demand, supply (stock levels), and strategic insights.
2. Output Format: The output MUST be a single, complete HTML document. It must start exactly with <!DOCTYPE html> and end with </html>. Do not include any conversational text, markdown formatting, or explanations outside of the HTML structure.
3. Styling: All CSS must be internal, placed within a <style> tag in the <head> section. Design for a clean, modern, and professional aesthetic suitable for a corporate PDF report. Use a professional color palette (e.g., shades of blue, gray, and white), clear typography (e.g., sans-serif fonts like Arial or Helvetica), and appropriate spacing.
4. Report Structure: The HTML body must be structured as follows:
5. Main Title: An <h1> element containing the report title, dynamically using the business name (e.g., "Market Demand & Supply Analysis for [Business Name]").
6. Executive Summary: An <h2> for "Executive Summary". Below it, write a 2-3 paragraph summary that synthesizes the key findings. Mention the overall demand landscape (e.g., "The analysis reveals a mixed demand landscape...") and highlight the most significant product opportunities or risks based on the demand_level and reasoning fields.
7. Business Profile: An <h2> for "Business Profile". Display the business metadata (Industry, Location, Size) in a clear, easy-to-read format, such as an unordered list (<ul>) or a definition list (<dl>).
8. Detailed Product Analysis: An <h2> for "Detailed Product Analysis". Present the product data in a well-structured HTML <table>.
9. Table Headers (<thead>): The table must have columns for: "Product Name", "Category", "Price", "Current Stock", "Predicted Demand", and "Analyst Reasoning".
10. Table Body (<tbody>): Each product from the JSON data should be a row (<tr>) in the table.
11. Visual Indicators: In the "Predicted Demand" cell, use the text but also consider adding a subtle visual cue with CSS. For example, you could style the cell's background color based on the demand level (e.g., light green for 'High', light yellow for 'Medium', light red for 'Low').
12. Strategic Recommendations: An <h2> for "Strategic Recommendations". Based on the analysis, provide 2-3 actionable recommendations in a bulleted list (<ul>). For example:
13. For "High" demand products: "Prioritize restocking and consider marketing campaigns to capitalize on strong demand."
14. For "Medium" demand products: "Maintain current stock levels and monitor sales trends closely."
15. For "Low" demand products: "Consider promotional pricing or bundling to clear excess inventory."
16. AT the end create a footer contain the business name and "powered by Arziki Analytics"."

DATA:
{analysis_data_str}
"""

    response = client.models.generate_content(
        model=model_name,
        contents=[{
            "role": "user",
            "parts": [{"text": prompt.replace("\\n", "")}]
        }],
        config=types.GenerateContentConfig(temperature=0.1)
    )

    print("Generated HTML Report Content:\n", response.text)
    return response.text.strip()


def transcribe_audio(audio_path: str):
    client = create_client()

    audio_bytes = open(audio_path, "rb").read()

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            types.Part.from_bytes(audio_bytes, mime_type="audio/wav")
        ],
        config=types.GenerateContentConfig(
            temperature=0.0,
        )
    )

    return response.text.strip()



# Full pipeline
def process_audio(user_id, audio_path):
    transcript = transcribe_audio(audio_path)
    print("Transcript:", transcript)

    reply = generate_reply(user_id, transcript)
    print("Gemini Reply:", reply)

    return reply, transcript
