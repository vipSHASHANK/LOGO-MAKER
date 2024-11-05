import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config  # Ensure you have this file for your bot's config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Full A-Z stylish fonts list (10 styles per letter)
stylish_alphabet = {
    'A': ['𝐴', '𝒜', '𝔸', '𝖠', '𝒶', '𝓐', '🅰', '𝕬', 'Ａ', '𝒜'],
    'B': ['𝐵', '𝒲', '𝔹', '𝖡', '𝒷', '𝓑', '🅱', '𝕭', 'Ｂ', '𝒲'],
    'C': ['𝐶', '𝒞', 'ℂ', '𝖢', '𝒸', '𝓒', '🅲', '𝕮', 'Ｃ', '𝒞'],
    'D': ['𝐷', '𝒟', '𝔻', '𝖣', '𝒹', '𝓓', '🅳', '𝕯', 'Ｄ', '𝒟'],
    'E': ['𝐸', '𝒳', '𝔼', '𝖤', '𝑒', '𝓔', '🅴', '𝕰', 'Ｅ', '𝒳'],
    'F': ['𝐹', '𝒻', '𝔽', '𝖴', '𝒻', '𝓕', '🅵', '𝕱', 'Ｆ', '𝒻'],
    'G': ['𝐺', '𝒢', '𝔾', '𝖦', '𝑔', '𝓖', '🅶', '𝕲', 'Ｇ', '𝒢'],
    'H': ['𝐻', '𝒲', 'ℍ', '𝖧', '𝒽', '𝓗', '🅷', '𝕳', 'Ｈ', '𝒲'],
    'I': ['𝐼', '𝒾', '𝕀', '𝖨', '𝒾', '𝓘', '🅸', '𝕴', 'Ｉ', '𝒾'],
    'J': ['𝒥', '𝒿', '𝕵', '𝖩', '𝒿', '𝓙', '🅹', '𝕵', 'Ｊ', '𝒿'],
    'K': ['𝐾', '𝒦', '𝒦', '𝖪', '𝓚', '𝒦', '🅺', '𝕶', 'Ｋ', '𝒦'],
    'L': ['𝐿', '𝒧', '𝕷', '𝖫', '𝓛', '𝓛', '🅻', '𝕷', 'Ｌ', '𝒧'],
    'M': ['𝑀', '𝒨', '𝕸', '𝖬', '𝓜', '𝓜', '🅼', '𝕸', 'Ｍ', '𝒨'],
    'N': ['𝑁', '𝒩', '𝓝', '𝖩', '𝓞', '𝒩', '🅽', '𝕹', 'Ｎ', '𝒩'],
    'O': ['𝒪', '𝓞', '𝕆', '𝖮', '𝓸', '𝓞', '🅾', '𝕺', 'Ｏ', '𝓞'],
    'P': ['𝒫', '𝒫', '𝕻', '𝖯', '𝓟', '𝒫', '🅿', '𝕻', 'Ｐ', '𝒫'],
    'Q': ['𝒬', '𝒬', '𝕼', '𝖰', '𝓠', '𝒬', '🅀', '𝕼', 'Ｑ', '𝒬'],
    'R': ['𝑅', '𝒭', '𝕽', '𝖷', '𝓡', '𝒭', '🅡', '𝕽', 'Ｒ', '𝒭'],
    'S': ['𝒮', '𝒮', '𝕾', '𝖲', '𝓢', '𝒮', '🅂', '𝕾', 'Ｓ', '𝒮'],
    'T': ['𝒯', '𝒯', '𝕿', '𝖳', '𝓣', '𝒯', '🅣', '𝕿', 'Ｔ', '𝒯'],
    'U': ['𝒰', '𝒰', '𝕌', '𝖴', '𝓤', '𝒰', '🅤', '𝕌', 'Ｕ', '𝒰'],
    'V': ['𝒱', '𝒲', '𝖵', '𝖻', '𝓥', '𝒲', '🅥', '𝖵', 'Ｖ', '𝒲'],
    'W': ['𝒲', '𝒲', '𝖶', '𝖶', '𝓦', '𝒲', '🅦', '𝖶', 'Ｗ', '𝒲'],
    'X': ['𝒳', '𝒳', '𝖷', '𝖷', '𝓧', '𝒲', '🅧', '𝖷', 'Ｘ', '𝒲'],
    'Y': ['𝒴', '𝒴', '𝕎', '𝖸', '𝓨', '𝒴', '🅨', '𝕎', 'Ｙ', '𝒴'],
    'Z': ['𝒵', '𝒵', '𝖩', '𝖹', '𝓩', '𝒵', '🅩', '𝖹', 'Ｚ', '𝒵'],
}

# Stylish Symbols List (special characters and Unicode symbols)
stylish_symbols = [
    "❤", "❀", "✰", "☪", "☽", "☁", "⭐", "✿", "☘", "❖", "✧", "☠", "⚡", "✪", "⚔", "✪", "❣", "➸", "✦"
]

# Function to convert text to stylish versions and add symbols
def convert_to_stylish_text(input_text):
    """Convert user text to different premium stylish formats using Unicode characters and fancy fonts."""
    
    stylish_texts = []
    
    # Create a list of styled versions of the input text
    for letter in input_text.upper():
        if letter in stylish_alphabet:
            stylish_texts.append(stylish_alphabet[letter][0])  # Take the first style as an example
        else:
            stylish_texts.append(letter)  # Non-alphabet characters stay as they are

    # Join the stylish letters together to form the stylish text
    stylish_version = "".join(stylish_texts)
    
    # Add some random symbols to enhance the stylish text
    symbol = stylish_symbols[0]  # For now, just adding the first symbol
    stylish_version_with_symbols = f"{symbol} {stylish_version} {symbol}"
    
    return stylish_version_with_symbols

# Text handler (processing the user input text and generating stylish outputs)
async def text_handler(_, message: Message) -> None:
    """Handles incoming text messages and applies stylish transformation."""
    if message.text:
        user_text = message.text.strip()

        if not user_text:
            await message.reply_text("Kripya kuch text bhejein jise main style kar sakoon.")
            return
        
        # Convert the text to premium stylish names with symbols
        stylish_text = convert_to_stylish_text(user_text)
        
        # Send back the styled text to the user
        await message.reply_text(stylish_text)

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
        logger.error("Failed to create the client.")
