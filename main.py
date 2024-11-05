import os
import logging
from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client, filters
from pyrogram.errors import SessionRevoked  # Only importing SessionRevoked
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery, InputMediaPhoto
from config import Config
from private_buttons import create_font_buttons, POSITION_SIZE_BUTTONS, GLOW_COLOR_BUTTONS  # Import buttons
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pyrogram Bot Setup
def create_app():
    return Client(
        "logo_creator_bot",
        bot_token=Config.BOT_TOKEN,
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        workers=2  # Set number of workers to handle requests faster
    )

# Font options (fonts stored here)
FONT_OPTIONS = [
    {"name": "FIGHTBACK", "path": "fonts/FIGHTBACK.ttf"},
    {"name": "Arial", "path": "fonts/Lobster-Regular.ttf"},
    {"name": "Times New Roman", "path": "fonts/OpenSans-Regular.ttf"},
    {"name": "Courier", "path": "fonts/Pacifico-Regular.ttf"},
    {"name": "Verdana", "path": "fonts/Roboto-Regular.ttf"},
]

# Function to dynamically adjust font size
def get_dynamic_font(image, text, max_width, max_height, font_path=None):
    draw = ImageDraw.Draw(image)
    
    font_size = 100
    while font_size > 10:
        font = ImageFont.truetype(font_path or "fonts/FIGHTBACK.ttf", font_size)
        text_width, text_height = draw.textsize(text, font=font)
        
        if text_width <= max_width and text_height <= max_height:
            return font, text_width, text_height
        
        font_size -= 5

    return font, text_width, text_height

# Function to add 3D text effect with shadow and glow
def add_3d_text(draw, position, text, font, glow_color, text_color, shadow_offset=(5, 5), glow_strength=5):
    x, y = position
    
    # Shadow: Draw the shadow slightly offset from the original position
    shadow_x = x + shadow_offset[0]
    shadow_y = y + shadow_offset[1]
    
    # Draw the shadow in a darker shade
    draw.text((shadow_x, shadow_y), text, font=font, fill="black")

    # Glow effect around the main text (optional, for more depth)
    for offset in range(1, glow_strength + 1):
        draw.text((x - offset, y - offset), text, font=font, fill=glow_color)
        draw.text((x + offset, y - offset), text, font=font, fill=glow_color)
        draw.text((x - offset, y + offset), text, font=font, fill=glow_color)
        draw.text((x + offset, y + offset), text, font=font, fill=glow_color)

    # Main text: Draw the main text on top of the shadow and glow
    draw.text((x, y), text, font=font, fill=text_color)

# Function to add text to the image
async def add_text_to_image(photo_path, text, output_path, x_offset=0, y_offset=0, size_multiplier=1, glow_color="red", font_path=None):
    try:
        user_image = Image.open(photo_path)
        user_image = user_image.convert("RGBA")

        max_width, max_height = user_image.size
        font, text_width, text_height = get_dynamic_font(user_image, text, max_width, max_height, font_path)

        text_width = int(text_width * size_multiplier)
        text_height = int(text_height * size_multiplier)

        x = (max_width - text_width) // 2 + x_offset
        y = (max_height - text_height) // 2 + y_offset
        text_position = (x, y)

        draw = ImageDraw.Draw(user_image)
        add_3d_text(draw, text_position, text, font, glow_color=glow_color, text_color="white", glow_strength=10)

        user_image.save(output_path, "PNG")
        return output_path
    except Exception as e:
        logger.error(f"Error adding text to image: {e}")
        return None

# Reinitialize the bot after session is revoked
async def restart_bot():
    try:
        app.stop()  # Stop the previous client instance
        logger.info("Bot stopped. Restarting the bot.")
        time.sleep(2)  # Giving some time before reinitializing
        app = create_app()  # Reinitialize the bot client
        await app.start()  # Start the bot again
        logger.info("Bot restarted successfully.")
    except Exception as e:
        logger.error(f"Error during bot restart: {e}")

# Initialize the bot and run it
async def main():
    try:
        app = create_app()  # Initialize the app
        await app.start()
    except SessionRevoked as e:
        logger.error(f"Session revoked: {str(e)}. The session has been invalidated.")
        # Restart the bot if session is revoked
        await restart_bot()  # This will reinitialize and restart the bot
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")

# Start the bot
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
        
