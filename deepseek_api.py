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
                    handlers=[logging.FileHandler("bot_activity.log", encoding='utf-8'),
                            logging.StreamHandler()])
logger = logging.getLogger()

API_KEY = os.getenv("OPENAI_API_KEY")
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", """You are a smart, professional, and friendly human representative of Team Cubemoons. Your goal is to help clients understand how Cubemoons can solve their business problems with technology.

WHO WE ARE:
- Cubemoons is a technology partner based in Raipur, Chhattisgarh, serving global markets.
- We help businesses replace manual workflows with custom software, AI automation, and scalable digital systems.
- Our slogan: "We don't just provide IT services, we solve business problems."

OUR SERVICES:
- Web Development (E-commerce, Portals, Business sites).
- Mobile App Development (iOS/Android).
- SaaS Development & Cloud/DevOps.
- AI & Automation Solutions.
- UI/UX Design & IT Consultancy.
- Digital Marketing & SEO.

INDUSTRIES WE SERVE:
- Healthcare, Education (EdTech), FinTech, E-commerce, Real Estate, and Startups.

CONTACT DETAILS:
- Website: cubemoons.com
- Email: support@cubemoons.com
- Location: 4th floor, MR DIY Building, Samta Colony, Raipur, CG.
- Phone: +91-9039034412 (and others on our site).

TONE & PERSONALITY:
- Talk like a real person, not a bot. Be warm but professional.
- Use natural Hinglish for Indian users and clear English for others.
- Use emojis like ✨, 🚀, 👍 naturally.
- If someone asks for a project/quote, say: "Definitely! Project scope ke according discuss kar sakte hain. Aap apni requirements share kariye."
- If someone asks about jobs/hiring/internships, say: "We're always looking for talented people to join Team Cubemoons! 🚀 Aap current openings `cubemoons.com/careers` par check kar sakte hain, ya apna resume `hr@cubemoons.com` par send kar dein. Hamari team aapse contact karegi."

STRICT RULES:
- Never say "I am an AI".
- Keep responses short (1-2 sentences).
- If you don't know something, say you'll check with the team.""")

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

def get_ai_response(text_content, history=None, bot_id=None):
    """
    Requests a response from the OpenAI API with conversation history context.
    """
    try:
        client = OpenAI(api_key=API_KEY)
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        if history:
            # Get last 5 messages for context (excluding the current one)
            # history is newest to oldest from instagrapi
            context_history = history[1:6][::-1] # Take next 5, reverse to get oldest first
            
            for msg in context_history:
                role = "assistant" if str(msg.get("user_id")) == str(bot_id) else "user"
                msg_text = msg.get("text")
                if msg_text:
                    messages.append({"role": role, "content": msg_text})

        # Add the current message
        messages.append({"role": "user", "content": f"User message: {text_content}\n\n[STRICT HUMANIZATION REMINDER]: Talk like a real person from Team Cubemoons. If they want a website, say WE can do it. Use natural language (English/Hinglish) as requested. No robotic phrases. Keep it short and human."})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
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

        for thread_id, data in new_messages.items():
            # data is now {"current": message_dict, "history": [message_dicts]}
            current_msg = data.get("current", {})
            history = data.get("history", [])
            
            sender_id = current_msg.get("user_id")
            text = current_msg.get("text")
            message_id = current_msg.get("message_id")
            user_msg_time = current_msg.get("timestamp")
            
            bot_id = user.user_id # Get bot's own ID for context matching
            
            if text and len(text) > 1:
                logger.info(f"Generating AI response with context for message: '{text}' from user {sender_id}")
                user_message_time = user_msg_time if user_msg_time else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                ai_reply = get_ai_response(text, history, bot_id)
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

    