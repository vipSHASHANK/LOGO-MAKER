import logging
import os
from PIL import Image, ImageDraw, ImageFont
import random
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# List of available fonts (TTF fonts)
fonts = [
    "fonts/Roboto-Regular.ttf",        # Example font 1
    "fonts/OpenSans-Regular.ttf",      # Example font 2
    "fonts/Lobster-Regular.ttf",       # Example font 3
    "fonts/Pacifico-Regular.ttf",      # Example font 4
    "fonts/Monospace.ttf",             # Example font 5
]

# Function to generate stylish logo images
def generate_stylish_logo(text, output_path):
    try:
        # Image size and background color
        width, height = 500, 500
        image = Image.new('RGB', (width, height), color=(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)))  # Random background color
        draw = ImageDraw.Draw(image)

        # Select random font
        font = ImageFont.truetype(random.choice(fonts), 80)

        # Text size and position
        text_width, text_height = draw.textsize(text, font=font)
        position = ((width - text_width) // 2, (height - text_height) // 2)

        # Add text to image
        draw.text(position, text, fill="white", font=font)

        # Save the image
        image.save(output_path)
        return output_path
    except Exception as e:
        logger.error(f"Error generating logo: {e}")
        return None

# Function to generate 10 different logo variations
def generate_multiple_logos(user_text):
    output_dir = "logos"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    image_paths = []
    
    for i in range(10):  # Generate 10 different logos
        image_path = os.path.join(output_dir, f"{user_text}_{i+1}.png")
        result = generate_stylish_logo(user_text, image_path)
        
        if result:
            image_paths.append(result)

    return image_paths

# Text handler (receive user's text and generate stylish logos)
async def text_handler(_, message: Message) -> None:
    """Receive user text and generate stylish logo images."""
    if message.text:
        user_text = message.text.strip()

        if not user_text:
            await message.reply_text("Please provide some text to style.")
            return
        
        # Generate 10 stylish logo images
        image_paths = generate_multiple_logos(user_text)

        # Send each image to the user
        for image_path in image_paths:
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
