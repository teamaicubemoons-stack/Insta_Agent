# Insta Agent - Instagram Bot with OpenAI GPT-4o-mini

This project automates the process of reading Instagram DMs and generating natural, human-like responses using the OpenAI GPT-4o-mini model. It also includes a scheduler for Instagram posts and stories.

## Features

- **Humanized DM Responses:** Generates conversational replies in Hinglish, Hindi, or English, matching the user's style and avoiding "robotic" language.
- **Detailed Interaction History:** Saves every DM interaction (Message ID, User Message, AI Reply, and Timestamps) into a JSON file for easy tracking.
- **Instagram Post/Story Scheduling:** Automatically handles uploading photos and stories with captions.
- **Smart Filtering:** Detects new messages and ignores bot-sent messages to avoid infinite loops.
- **Premium Messaging:** Uses emojis and proper formatting for a professional brand experience.

## Project Structure

- **automate_page.py:** Main script that handles Instagram login and runs the bot loop.
- **message_handler.py:** Manages DM checking, unread message detection, and thread processing.
- **deepseek_api.py:** Interfaces with OpenAI to generate responses and logs conversation history to JSON.
- **posting.py:** Handles Instagram post and story scheduling logic.

## Setup Instructions

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configuration:**
   Create a `.env` file in the root directory with the following variables:
   ```env
   IG_USERNAME="your_username"
   IG_PASSWORD="your_password"
   OPENAI_API_KEY="your_openai_api_key"
   SYSTEM_PROMPT="... (Defined in .env for personality)"
   ```

3. **Run the Bot:**
   ```bash
   python automate_page.py
   ```

## Logging & History

- **Detailed History:** `DMs_history/detailed_messages_history.json` contains a structured log of all conversations.
- **Activity Log:** `bot_activity.log` contains technical logs of the bot's runtime activity.

## Important Note

Ensure your `.env` and `session.json` files are never shared or pushed to public repositories to protect your account credentials.
