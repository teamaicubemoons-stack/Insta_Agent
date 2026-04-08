from message_handler import get_unread_DMs, load_latest_messages, save_new_messages
from posting import process_posts, process_stories
from dotenv import load_dotenv
from instagrapi import Client, exceptions
import os 
import json
import logging
import random
import time
import threading
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running! 🚀"

def run_web_server():
    # Render provides PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

load_dotenv() # For script to access env file

# Consolidated logging to both file and terminal
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s', 
    handlers=[
        logging.FileHandler("bot_activity.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

# Update environment variable names to match .env file
IG_USERNAME = os.getenv('IG_USERNAME')
IG_PASSWORD = os.getenv('IG_PASSWORD')


def login_user(user):
    """
    Attempts to login to Instagram with detailed diagnostic feedback.
    """
    try:
        if not IG_USERNAME or "ENTER_YOUR" in IG_USERNAME or "aapka" in IG_USERNAME:
             logger.error("REASON: Aapne .env file mein details (Username/Password) nahi dali hain!")
             return False

        session_file = "session.json"
        
        # Fresh login attempt with specific exception handling
        logger.info(f"Diagnosing login for user: {IG_USERNAME}...")
        
        try:
            if os.path.exists(session_file):
                session = user.load_settings(session_file)
                user.set_settings(session)
                user.login(IG_USERNAME, IG_PASSWORD)
                logger.info("Login via session SUCCESS.")
                return True
        except Exception:
            logger.info("Session invalid, trying fresh login...")

        if user.login(IG_USERNAME, IG_PASSWORD):
            user.dump_settings(session_file)
            logger.info("Fresh Login SUCCESS. Session saved.")
            return True
        
    except exceptions.BadPassword:
        logger.error("REASON: Password ya Username galat hai. (Check if you used double underscore __ in username)")
    except exceptions.TwoFactorRequired:
        logger.error("REASON: Aapke account par 2FA on hai. Ise off karein.")
    except exceptions.ChallengeRequired:
        logger.error("REASON: Instagram Verification chahiye. App par 'It was me' karein.")
    except exceptions.PleaseWaitFewMinutes:
        logger.error("REASON: 'Please wait a few minutes' error. 1-2 ghante wait karein.")
    except exceptions.FeedbackRequired:
        logger.error("REASON: Instagram ne aapki activity spam samajhkar block ki hai.")
    except exceptions.ClientError as e:
        if "blacklist" in str(e).lower():
            logger.error("REASON: IP BLACKLISTED hai. Mobile Hotspot use karein.")
        else:
            logger.error(f"REASON: Client error -> {e}")
    except Exception as e:
        logger.error(f"REASON: Unexpected error -> {e}")

    return False
        
def main():
    user = Client() # An instance of class Client to send request to instagram# mimic human interaction
    
    # Random device setup - Trying a different profile (Samsung G960F)
    try:
        user.set_device({
            "app_version": "121.0.0.29.119",
            "android_release": "9",
            "android_version": "28",
            "manufacturer": "Samsung",
            "model": "SM-G960F",
            "device": "starlte",
            "cpu": "samsungexynos9810",
            "version_code": "180322800"
        })
        logger.info("Using Samsung S9 device profile for login.")
    except Exception as e:
        logger.warning(f"Failed to set custom device: {e}")

    # Ensure history directory exists
    os.makedirs("DMs_history", exist_ok=True)

    # Do not proceed if login fails
    if not login_user(user):
        logger.error("Script terminated: Unable to login to Instagram. Check your ENV variables on Render.")
        return

    user.delay_range = [5, 10] 
    logger.info("Bot is active and running in a loop. Checking for DMs...")

    while True:
        try:
            # 1. Check for unread DMs and reply automatically
            logger.info("Checking for new messages...")
            get_unread_DMs(user)

            # 2. Switch between other actions (Posting/Stories) occasionally
            random_val = random.random()
            if random_val < 0.05: # 5% chance per loop to check for posts
                 process_posts(user)
            elif random_val < 0.1: # Another 5% chance to check for stories
                process_stories(user)

            # 3. Wait for exactly 30 seconds before next check
            wait_seconds = 30
            logger.info(f"Task completed. Sleeping for {wait_seconds} seconds before next check.")
            time.sleep(wait_seconds)

        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            logger.info("Waiting for 1 minute before retrying...")
            time.sleep(60)

if __name__ == "__main__":
    # Start the Bot in a background thread so Flask can be the main process
    logger.info("Initializing Bot background thread...")
    bot_thread = threading.Thread(target=main, daemon=True)
    bot_thread.start()
    
    # Run the Health Check server (Main Process)
    logger.info("Starting Health Check server...")
    run_web_server()
