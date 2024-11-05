"""
Configuration module for the bot status checker.

This module loads environment variables required for the bot to function,
such as bot token, API ID and API HASH.
It also sets up the necessary configuration settings.
"""

from os import getenv
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_ID = int(getenv("API_ID", "16457832"))
    API_HASH = getenv("API_HASH", "3030874d0befdb5d05597deacc3e83ab")
    BOT_TOKEN = getenv("BOT_TOKEN", "7893206132:AAEhC7NgDL08NKNmIpTLt4AZ2XxQTd_Y-Ko")
    MONGO_URI = getenv("MONGO_URI", "mongodb+srv://TEAMBABY01:UTTAMRATHORE09@cluster0.vmjl9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    MONGO_DB_NAME = getenv("MONGO_DB_NAME", "logo_creator_bot")
    
