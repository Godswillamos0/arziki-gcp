from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
from typing import Dict, List
from google.cloud import speech

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
    
    Data:
    {input_json}
    """

    # 4. Generate Content with JSON enforcement
    # The new SDK makes it very easy to enforce JSON output using 'response_mime_type'
    print("Sending data to Gemini (via google-genai SDK)...")
    
    response = client.models.generate_content(
        model="gemini-1.5-pro-002",  # Using the latest stable model
        contents=prompt_text,
        config=types.GenerateContentConfig(
            response_mime_type="application/json", 
            temperature=0.2
        )
    )

    return response.text


def generate_report_html(analysis_data: str, model_name: str = 'gemini-2.5-flash') -> str:
    
    client = create_client()
    
    """
    Sends market analysis data to Gemini with instructions to return a structured HTML report.

    Args:
        analysis_data: The prediction data in JSON or string format.
        model_name: The Gemini model to use.

    Returns:
        A string containing the generated HTML report.
    """
    
    # Define a clear, constrained prompt to force HTML output
    prompt = f"""
    You are a Professional Report Formatting Engine. Your task is to take the provided market analysis 
    data and transform it into a single, complete HTML document suitable for conversion to PDF.

    **Instructions:**
    1.  **Start** the output with `<!DOCTYPE html>`.
    2.  Use **internal CSS** within the `<style>` tags in the `<head>` for a clean, professional look 
        (e.g., set font-family, basic padding, use colors for headers, etc.).
    3.  Structure the data clearly using HTML tags (`<h1>`, `<h2>`, `<p>`, `<ul>`, `<table>`).
    4.  **Do not** include any conversational text outside of the HTML structure.

    **Market Analysis Data to Format:**
    ---
    {analysis_data}
    ---
    """

    print("Sending data to Gemini for HTML generation...")

    response = client.models.generate_content(
        model=model_name,
        contents=[prompt],
    )
    
    # Return the generated text, which should be the HTML string
    return response.text.strip()


def transcribe_audio(audio_path: str):
    client = speech.SpeechClient()

    with open(audio_path, "rb") as f:
        audio_data = f.read()

    config = speech.RecognitionConfig(
        auto_decoding_config=speech.AutoDetectDecodingConfig(),
        language_codes=["en-US"]
    )

    request = speech.RecognizeRequest(
        recognizer="projects/YOUR_PROJECT_ID/locations/global/recognizers/default",
        config=config,
        content=audio_data
    )

    response = client.recognize(request=request)
    return response.results[0].alternatives[0].transcript if response.results else None


# Full pipeline
def process_audio(user_id, audio_path):
    transcript = transcribe_audio(audio_path)
    print("Transcript:", transcript)

    reply = generate_reply(user_id, transcript)
    print("Gemini Reply:", reply)

    return reply, transcript