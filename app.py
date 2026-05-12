import os
import re
import json
import requests
import logging
# pyrefly: ignore [missing-import]
from flask import Flask, render_template, request, jsonify
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configure logging to file
logging.basicConfig(
    filename='server_debug.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s'
)

# User specifically requested Nvidia API endpoint
API_URL = "https://integrate.api.nvidia.com/v1"
API_KEY = os.getenv("API_KEY")
MODEL = "meta/llama-3.1-8b-instruct"

def extract_json_from_response(text: str) -> str:
    """
    Robustly extracts JSON from a string, handling markdown blocks or surrounding text.
    """
    text = text.strip()
    # Search for content within ```json ... ``` or ``` ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        return match.group(1).strip()
    
    # Fallback: find the outermost JSON structure (object or array)
    start_obj = text.find('{')
    start_arr = text.find('[')
    
    # Determine the earliest starting point
    if start_obj != -1 and (start_arr == -1 or start_obj < start_arr):
        start = start_obj
        end = text.rfind('}')
    elif start_arr != -1:
        start = start_arr
        end = text.rfind(']')
    else:
        return text

    if start != -1 and end != -1 and end > start:
        return text[start:end+1]
        
    return text


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/next_question", methods=["POST"])
def next_question():
    if not API_KEY:
        return jsonify({"error": "API Key is not configured."}), 500

    data = request.json or {}
    history = data.get("history", [])
    
    # Static First Question for Instant Load
    if len(history) == 0:
        return jsonify({"question": "What kind of stories or topics are you usually drawn to?", "done": False})
        
    if len(history) >= 10:
        return jsonify({"done": True})

    # Minimalist prompt for speed
    system_prompt = "You are an AI Librarian. Ask ONE follow-up question to refine book recommendations. Respond ONLY with JSON: {\"question\": \"...\"}"

    messages = [{"role": "system", "content": system_prompt}]
    for item in history:
        if isinstance(item, dict):
            if "question" in item: messages.append({"role": "assistant", "content": item["question"]})
            if "answer" in item: messages.append({"role": "user", "content": item["answer"]})

    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 100, # Shorter limit for speed
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    ai_message = ""
    try:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(f"{API_URL}/chat/completions", headers=headers, json=payload, timeout=60)
                response.raise_for_status()
                result = response.json()
                ai_message = result["choices"][0]["message"]["content"].strip()
                break
            except requests.exceptions.ReadTimeout:
                if attempt == max_retries - 1:
                    raise
                app.logger.warning(f"API timeout on attempt {attempt + 1}, retrying...")
            except Exception as e:
                raise e

        
        app.logger.debug(f"RAW AI RESPONSE: {ai_message}")
        cleaned = extract_json_from_response(ai_message)
        try:
            parsed = json.loads(cleaned)
            question = parsed.get("question") or "What else do you look for in a good book?"
        except json.JSONDecodeError:
            app.logger.warning(f"Failed to parse JSON in next_question. Using raw ai_message. Cleaned string: {cleaned}")
            question = ai_message if ai_message and len(ai_message) > 5 else "What else do you look for in a good book?"
            
        return jsonify({"question": question, "done": False})
    except Exception as e:
        app.logger.error(f"Error in next_question: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to process request."}), 500


@app.route("/api/recommend", methods=["POST"])
def recommend():
    if not API_KEY:
        return jsonify({"error": "API Key is not configured."}), 500

    data = request.json or {}
    history = data.get("history", [])

    system_prompt = """
You are a sophisticated book recommendation engine acting as a digital librarian.
Provide exactly 3 tailored book suggestions as a JSON array of objects.
STRICT JSON ONLY. No markdown, no extra text.

Object Schema:
{
  "title": "Book Title",
  "author": "Author Name",
  "genre": "Genre",
  "summary": "1-2 sentence summary",
  "reason": "Why it fits their taste",
  "match_score": 95
}
"""

    messages = [{"role": "system", "content": system_prompt}]
    for item in history:
        if isinstance(item, dict):
            if "question" in item: messages.append({"role": "assistant", "content": item["question"]})
            if "answer" in item: messages.append({"role": "user", "content": item["answer"]})

    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 2048,
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    ai_message = ""
    try:
        app.logger.info("Requesting recommendations...")
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(f"{API_URL}/chat/completions", headers=headers, json=payload, timeout=60)
                response.raise_for_status()
                result = response.json()
                ai_message = result["choices"][0]["message"]["content"].strip()
                break
            except requests.exceptions.ReadTimeout:
                if attempt == max_retries - 1:
                    raise
                app.logger.warning(f"API timeout on attempt {attempt + 1} for recommendations, retrying...")
            except Exception as e:
                raise e

        app.logger.debug(f"RAW AI RESPONSE: {ai_message}")
        
        cleaned = extract_json_from_response(ai_message)
        try:
            suggestions = json.loads(cleaned)
        except json.JSONDecodeError:
            app.logger.error(f"Failed to parse recommendations JSON. Cleaned string: {cleaned}")
            return jsonify({"error": "The AI provided an invalid response format. Please try again."}), 500
        
        if isinstance(suggestions, dict):
            for value in suggestions.values():
                if isinstance(value, list):
                    suggestions = value
                    break

        return jsonify({"recommendations": suggestions})
    except Exception as e:
        app.logger.error(f"Error in recommend: {str(e)}")
        app.logger.error(f"AI Message that failed: {ai_message}")
    
if __name__ == "__main__":
    app.run(debug=True, port=5000)
