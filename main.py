import logging
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path to the background image
background_image_path = "backgrounds/istockphoto-529329091-612x612.jpg"  # Replace with the path to your wood texture image

# List of available fonts (TTF fonts)
fonts = [
    "fonts/FIGHTBACK.ttf"  # Replace with the path to a stylized, rough font
]

# Function to add glow effect to text
def add_glow(draw, position, text, font, glow_color, text_color, glow_strength=10):
    x, y = position
    for offset in range(glow_strength, 0, -1):
        draw.text((x - offset, y - offset), text, font=font, fill=glow_color)
        draw.text((x + offset, y - offset), text, font=font, fill=glow_color)
        draw.text((x - offset, y + offset), text, font=font, fill=glow_color)
        draw.text((x + offset, y + offset), text, font=font, fill=glow_color)
    draw.text(position, text, font=font, fill=text_color)

# Function to generate logo
def generate_stylish_logo(text, output_path):
    try:
        # Load the background image
        background = Image.open(background_image_path)
        width, height = background.size

        # Create an ImageDraw object
        draw = ImageDraw.Draw(background)

        # Select random font
        font = ImageFont.truetype(random.choice(fonts), 250)  # Adjust size as needed

        # Text size and position
        text_width, text_height = draw.textsize(text, font=font)
        position = ((width - text_width) // 2, (height - text_height) // 2)

        # Add glow effect
        add_glow(draw, position, text, font, glow_color="red", text_color="white", glow_strength=15)

        # Save the image
        background.save(output_path, quality=95)
        return output_path
    except Exception as e:
        logger.error(f"Error generating logo: {e}")
        return None

# Function to generate 1 logo for simplicity
def generate_logo(user_text):
    output_dir = "logos"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    image_path = os.path.join(output_dir, f"{user_text}_logo.png")
    result = generate_stylish_logo(user_text, image_path)
    return image_path if result else None

# Text handler (receive user's text and generate stylish logo)
async def text_handler(_, message: Message) -> None:
    """Receive user text and generate stylish logo image."""
    if message.text:
        user_text = message.text.strip()

        if not user_text:
            await message.reply_text("Please provide some text to style.")
            return
        
        # Generate a stylish logo image
        image_path = generate_logo(user_text)

        # Send image to the user
        if image_path:
            await message.reply_photo(image_path)

# Main entry point to run the bot
if __name__ == "__main__":
    app = Client(
        "stylish_text_logo_bot_session",  # Session name
        bot_token=Config.BOT_TOKEN,
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
    )

    if app:
        # Handlers define karte hain
        app.on_message(filters.text & filters.private)(text_handler)

        # Bot ko run karte hain
        app.run()
    else:
        logger.error("Client banane mein kuch problem aayi.")
