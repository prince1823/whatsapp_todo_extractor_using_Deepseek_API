
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)
@app.route("/", methods=["GET"])
def home():
    return "✅ WhatsApp To-Do Extractor Backend is Running"


DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
API_KEY = os.getenv("DEEPSEEK_API_KEY")

SYSTEM_PROMPT = """
You are a smart WhatsApp chat analyzer. Assume that the first sender in the uploaded WhatsApp chat is the user (called "me").

If this first sender gives an instruction to someone else, the task should be assigned to the recipient (other person).  
If another person sends a message asking for or implying a task, it should be assigned to "me".

Extract all current or upcoming actionable tasks (todos) from messages, even when written in mixed Hindi-English (Hinglish), other languages, or informal style with emojis, abbreviations, or spelling errors.


🎯 Your job is to output a **clean JSON array**, where each object follows this format:
[
  {
    "timestamp": "original timestamp",
    "sender": "sender name",
    "recipient": "me | other name",
    "task": "concise task description"
  }
]

✅ Extraction Rules:
1. Extract only actionable tasks — ignore completed or past-tense tasks (e.g. “sent yesterday”, “already done”).
2. Support multilingual, informal text — including English, Hindi, Hinglish, and Indic languages.
3. Recognize broken grammar, spelling errors, abbreviations: "snd" → "send", "bhejdo" → "send", "krdo" → "do", "sended" → "sent", "plz" → "please".
4. Detect code-mixed and informal phrasing: “Bhai, krde send pls”, “kal report bhejdena”, “tmrw plz ping”.
5. Normalize emojis, slang, casual tone, and convert them to a clean task form. Ignore emojis unless they support the intent.
6. Consider tasks implied by requests, reminders, or instructions — even if vaguely stated.
7. Also include common task cues like: "check", "check krna", "verify", "look into it", "remind me", "share", "update", "send", "finalize", "book", "fix", "submit", "review", "ping", "upload".
8. Extract **multiple tasks** from a single message if found (e.g., “send doc and check the status” → 2 tasks).
9. Recipient:
   - Use "me" if the task is intended for the user.
   - Use actual name (if present) if task is assigned to someone else.
10. Task:
    - Convert informal or broken requests into clear task descriptions.
    - Make task short but clear (e.g., “Send the report via email”, “Book client meeting slot”).
11. Priority:
    - **High**: “asap”, “urgent”, “jaldi”, “by today”, “immediately”, “tonight”
    - **Medium**: “by tomorrow”, “this week”, “soon”, polite requests without urgency
    - **Low**: “whenever you can”, “later”, “no rush”
12. Output a valid JSON **array only**, no markdown, no explanations, no headings.
13. If no tasks are found, return an empty array: []
14. Timestamps and sender names must match the chat format.         
15. Avoid duplicates — extract unique actionable items only.
16. Consider future intent phrases like "I'll check", "check krna", "check kar lunga", "kal check krte hain", "socha check kar lunga", etc. as valid TODOs. These imply upcoming tasks and must be included.
📌 Examples:
- Message: "plz snd the ppt and check krna notes bhi"
  → Output: 2 tasks — send PPT and check notes
- Message: "done with the report"
  → Not a task (already completed)
- Message: "Jaldi slides mail krdo"
  → Task: Send the slides via email (priority: high)
- Message: "me: thik hai bhej dunga"
  → Not a new task
- Message: "Okay, I'll check my inbox."
  → Output:
  [{ "timestamp": "10/06/2025 16:53", "sender": "me", "recipient": "me", "task": "Check inbox" }]
- Message: "check krlunga"
  → Output:
  [{ "timestamp": "10/06/2025 16:53", "sender": "me", "recipient": "me", "task": "Check inbox" }]
-Message: "ok check krleta hu "
  → Output:
  [{ "timestamp": "10/06/2025 16:53", "sender": "me", "recipient": "me", "task": "Check inbox" }]
Message: "ok dekhlunga apne pass ek baar agar hoga toh"
  → Output:
  [{ "timestamp": "10/06/2025 16:53", "sender": "me", "recipient": "me", "task": "Check inbox" }]
-Message: "thik hai check krlunga"
  → Output:
  [{ "timestamp": "10/06/2025 16:53", "sender": "me", "recipient": "me", "task": "Check inbox" }]


Keep the response structured, smart, and JSON-only. Don't include ``` or explanations.
"""


def extract_todos_with_deepseek(chat_content):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": chat_content}
        ],
        "temperature": 0.1
    }

    try:
        response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()

        raw_output = result['choices'][0]['message']['content']
        cleaned_output = re.sub(r"```(json)?", "", raw_output).strip("`\n ")

        return jsonify({"success": True, "todos": cleaned_output})
    except Exception as e:
        return jsonify({"error": f"DeepSeek API error: {str(e)}"}), 500

@app.route('/extract', methods=['POST'])
def extract_todos():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if not file.filename.endswith('.txt'):
        return jsonify({"error": "Only .txt files allowed"}), 400

    try:
        content = file.read().decode('utf-8')
        return extract_todos_with_deepseek(content)
    except Exception as e:
        return jsonify({"error": f"Processing error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
