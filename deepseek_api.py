from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
from openai import OpenAI
import os 
import json
import logging
from datetime import datetime

load_dotenv() # For script to access env file
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', 
                    handlers=[logging.FileHandler("bot_activity.log"),
                            logging.StreamHandler()])
logger = logging.getLogger()

API_KEY = os.getenv("OPENAI_API_KEY")
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "You are a helpful social media assistant. Respond politely and concisely to Instagram DMs.")

def respond_to_other_party(response, other_party_id, user):
    """
    Sends the AI generated response to the other party on Instagram.
    """
    try:
        # direct_send expects a list or a single user_id as a string/int
        user.direct_send(response, [str(other_party_id)])
        logger.info(f"Sent DM to other_party_id: {other_party_id}. Response: {response}\n")
    except Exception as e:
        logger.info(f"Unable to send DM ({response}) back to user ({other_party_id}). Error: {e}")

def save_message_history(message_id, user_message, user_message_time, bot_reply, bot_reply_time):
    """
    Saves the interaction history into a JSON file.
    """
    history_file = "DMs_history/detailed_messages_history.json"
    new_entry = {
        "message_id": message_id,
        "user_message": user_message,
        "user_message_time": user_message_time,
        "bot_reply": bot_reply,
        "bot_reply_time": bot_reply_time
    }
    
    try:
        os.makedirs(os.path.dirname(history_file), exist_ok=True)
        history = []
        if os.path.exists(history_file):
            with open(history_file, "r") as f:
                try:
                    history = json.load(f)
                except json.JSONDecodeError:
                    history = []
        
        history.append(new_entry)
        with open(history_file, "w") as f:
            json.dump(history, f, indent=4)
        logger.info(f"History saved for message ID: {message_id}")
    except Exception as e:
        logger.error(f"Error saving message history: {e}")

def get_ai_response(text_content):
    """
    Requests a response from the OpenAI API to generate a human-like response.
    """
    try:
        client = OpenAI(api_key=API_KEY)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"User message: {text_content}\n\nReminder: Reply in the same language/style as the user (English, Hindi, or Hinglish)."},
            ],
            temperature=0.7
        )

        ai_response = response.choices[0].message.content
        return ai_response

    except Exception as e:
        logger.info("Unable to fetch OpenAI response: %s" % e)
        return None

def process_text(new_messages, user):
    """
    Handles processing the text and generating replies for new messages.
    """
    try:
        if not new_messages:
            logger.info("No new messages to process.")
            return

        for thread_id, msg_data in new_messages.items():
            sender_id = msg_data.get("user_id")
            text = msg_data.get("text")
            message_id = msg_data.get("message_id")
            user_msg_time = msg_data.get("timestamp")
            
            if text and len(text) > 1:
                logger.info(f"Generating AI response for message: '{text}' from user {sender_id}")
                user_message_time = user_msg_time if user_msg_time else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                ai_reply = get_ai_response(text)
                bot_reply_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                if ai_reply:
                    respond_to_other_party(ai_reply, sender_id, user)
                    save_message_history(message_id, text, user_message_time, ai_reply, bot_reply_time)
                else:
                    logger.info(f"Failed to get AI response for user {sender_id}")
            else:
                logger.info(f"Skipping trivial or empty message from user {sender_id}")
                  
    except Exception as e:
        logger.info("Error in process_text: %s" % e)

    