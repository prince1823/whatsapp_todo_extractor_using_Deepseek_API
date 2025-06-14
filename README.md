# WhatsApp Todo Extractor using DeepSeek API

This project extracts to-do tasks from exported WhatsApp chats using the DeepSeek API.  
It supports recognizing varied languages and spelling errors to generate a structured JSON list of tasks with timestamps.

## Features

- Parses WhatsApp chat exports (`.txt` files).  
- Extracts to-do items in English and Hindi.  
- Handles common spelling mistakes and variations.  
- Outputs to-do list in JSON format with timestamps.  

## Tech Stack

- Python (for backend processing)  
- DeepSeek API (for natural language understanding)  
- Flask (for serving API/backend)  

## Setup Instructions

1. Navigate to backend:

    ```bash
    cd backend
    ```

2. Create and activate a virtual environment (optional but recommended):

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Linux/Mac
    venv\Scripts\activate     # Windows
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Run the Flask app:

    ```bash
    python app.py
    ```

## Usage

- Export WhatsApp chats as `.txt` files.  
- Upload the file via the frontend or call the backend API to extract todos.  
- Receive JSON with todo items and timestamps.

## Notes

- Virtual environment folder (`venv`) is excluded from Git.  
- DeepSeek API key is needed for extraction — configure it in your environment variables or config files.


