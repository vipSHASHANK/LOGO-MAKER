import logging
import random
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config
import pyfiglet  # Pyfiglet for stylish text generation

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Stylish Symbols List (special characters and Unicode symbols)
stylish_symbols = [
    "❤", "❀", "✰", "☪", "☽", "☁", "⭐", "✿", "☘", "❖", "✧", "☠", "⚡", "✪", "⚔", "❣", "➸", "✦"
]

# Function to convert text to stylish versions using `pyfiglet`
def convert_to_stylish_text(input_text):
    """Text ko stylish formats mein convert kare."""
    
    # Check if the input text contains any invalid characters (non-alphabetic)
    if not input_text.replace(" ", "").isalnum():
        return "Kripya sirf text daalein, special characters nahi."

    stylish_versions = []

    # 1. Use pyfiglet for ASCII-style fonts (smaller and readable)
    try:
        figlet_version = pyfiglet.figlet_format(input_text, font="slant")  # Use a simple and compact font
        stylish_versions.append(figlet_version)
    except Exception as e:
        logger.error(f"Error in pyfiglet: {e}")

    # 2. Add random stylish symbols around the text
    symbol = random.choice(stylish_symbols)
    stylish_versions_with_symbols = [f"{symbol} {version} {symbol}" for version in stylish_versions]

    return stylish_versions_with_symbols

# Text handler (processing the user input text and generating stylish outputs)
async def text_handler(_, message: Message) -> None:
    """Incoming text messages ko process karein aur stylish text return karein."""
    if message.text:
        user_text = message.text.strip()

        if not user_text:
            await message.reply_text("Kripya kuch text bhejein jise main style kar sakoon.")
            return
        
        # Convert the text to stylish versions with symbols
        stylish_texts = convert_to_stylish_text(user_text)
        
        # Agar text ko convert nahi kar sakte to error message bhejenge
        if isinstance(stylish_texts, str):
            await message.reply_text(stylish_texts)
        else:
            # Har ek stylish version ko user ko bhejna
            for stylish_version in stylish_texts:
                await message.reply_text(stylish_version)

# Main entry point to run the bot
if __name__ == "__main__":
    app = Client(
        "stylish_text_bot_session",  # Session name
        bot_token=Config.BOT_TOKEN,
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
    )

    if app:
        # Define handlers after the app is created
        app.on_message(filters.text & filters.private)(text_handler)

        # Run the bot
        app.run()
    else:
        logger.error("Client banane mein kuch problem aayi.")
