# 🤖 Insta Agent (DeepSeekgram) - Setup Guide

This guide will help you set up and run the Instagram automation bot on your local machine or server.

---

## 📋 Table of Contents / Index
1. [Requirements](#1-requirements)
2. [Step 1: Installation](#step-1-installation)
3. [Step 2: Configuration (.env Setup)](#step-2-configuration-env-setup)
4. [Step 3: Scheduling (Post/Story Setup)](#step-3-scheduling-poststory-setup)
5. [Step 4: Running the Bot](#step-4-running-the-bot)
6. [Troubleshooting (Common Errors)](#troubleshooting-common-errors)

---

## 1. Requirements
*   **Python 3.8+**: Python must be installed on your computer.
*   **Instagram Account**: Ideally, Two-Factor Authentication (2FA) should be turned off for now (to avoid login issues).
*   **OpenAI API Key**: Used to generate replies using GPT-4o-mini.

---

## Step 1: Installation

First, open terminal/powershell in the project folder and run the following commands sequentially:

1.  **Create a Virtual Environment (Optional but recommended):**
    ```bash
    python -m venv .venv
    ```

2.  **Activate the Virtual Environment:**
    *   **Windows:** `.venv\Scripts\activate`
    *   **Mac/Linux:** `source .venv/bin/activate`

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

---

## Step 2: Configuration (.env Setup)

There should be a file named `.env` in the root directory (create one if it doesn't exist). Fill in the details correctly as shown below:

```env
IG_USERNAME="your_instagram_username"
IG_PASSWORD="your_instagram_password"
OPENAI_API_KEY="sk-proj-xxxx_your_openai_key"
SYSTEM_PROMPT="You are a smart representative of Team Cubemoons..."
```

---

## ✨ Features (New!)

1.  **Humanized Cubemoons Persona**: The bot now acts as a real human member of the Cubemoons team, using a natural, conversational tone (English/Hinglish).
2.  **Hiring Support**: Automatically handles job and internship inquiries by directing candidates to the careers page or the HR email.
3.  **Website Integration**: The bot is trained on Cubemoons' core services (Web, App, AI, SaaS) to answer business queries accurately.
4.  **Emoji Support**: Fixed logging issues to support emojis in all activity logs.

---

## Step 3: Scheduling (Post/Story Setup)

If you want the bot to automatically handle posts and stories, check these files:

1.  **`scheduled_posts.json`**: Enter the caption and image path here.
    ```json
    {
        "Caption of the post": "images/post1.jpg"
    }
    ```
2.  **`scheduled_stories.json`**: Enter the date and list of image paths here.
    ```json
    {
        "2026-04-15": ["images/story1.jpg", "images/story2.jpg"]
    }
    ```

---

## Step 4: Running the Bot

Now, run this command to start the bot:

```bash
python automate_page.py
```

**After starting the bot:**
*   It will only check DMs when a new unread message arrives.
*   It scans for unread messages every 30 seconds.
*   A health check server (Flask) will also start at `http://localhost:5000`.

---

## 🛠 Project Structure (File Information)

*   `automate_page.py`: **Main file** to be executed. Login and the main loop run from here.
*   `message_handler.py`: Logic for reading messages from Instagram.
*   `deepseek_api.py`: Logic for OpenAI responses, humanized persona, and hiring-specific handling.
*   `posting.py`: Logic for uploading photos/stories to Instagram.
*   `DMs_history/`: All chat history is saved here in JSON format.
*   `bot_activity.log`: Contains detailed information about the bot's activities.

---

## ⚠️ Troubleshooting (Common Errors)

| Error | Solution |
| :--- | :--- |
| **BadPassword** | Check your Username/Password in the `.env` file. |
| **TwoFactorRequired** | Disable 2FA (OTP) on your account. |
| **ChallengeRequired** | Open the Instagram app and click "It was me". |
| **IP Blacklisted** | Use a mobile hotspot or turn off your VPN. |
| **API Error** | Check if your OpenAI key is valid and has sufficient credits. |

---

**Made with ❤️ for Insta Automation.**
