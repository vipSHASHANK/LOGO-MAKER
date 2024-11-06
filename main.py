# your_main_script.py

import os
import logging
import tempfile
from PIL import Image, ImageDraw, ImageFont, ImageColor, ImageFilter
from random import randint
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery, InputMediaPhoto
from config import Config
from buttons import get_adjustment_keyboard  # Importing the button function
from UTTAM.callbacks import handle_callback  # Importing the callback handler from callbacks.py

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# User data store
user_data_store = {}

# Adjust font size dynamically
def get_dynamic_font(image, text, max_width, max_height, font_path):
    draw = ImageDraw.Draw(image)
    font_size = 100
    while font_size > 10:
        font = ImageFont.truetype(font_path, font_size)
        text_width, text_height = draw.textsize(text, font=font)
        if text_width <= max_width and text_height <= max_height:
            return font
        font_size -= 5
    return font

# Add text to image with "brushstroke" effect, and blur functionality
async def add_text_to_image(photo_path, text, font_path, text_position, size_multiplier, text_color, blur_radius):
    try:
        user_image = Image.open(photo_path).convert("RGBA")
        max_width, max_height = user_image.size

        # Adjust font size based on size_multiplier
        font = get_dynamic_font(user_image, text, max_width, max_height, font_path)
        font = ImageFont.truetype(font_path, int(font.size * size_multiplier))
        
        # Create a new image for text drawing (text will be drawn here)
        text_image = Image.new("RGBA", user_image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_image)
        text_width, text_height = draw.textsize(text, font=font)
        
        # Apply position adjustments
        x = text_position[0]
        y = text_position[1]

        # Brushstroke effect (slightly offset multiple layers of text to create a stroke effect)
        num_strokes = 8  # Number of brush strokes
        for i in range(num_strokes):
            offset_x = randint(-5, 5)  # Random horizontal offset
            offset_y = randint(-5, 5)  # Random vertical offset
            # Add a blurred stroke effect by drawing text in slightly different positions
            draw.text((x + offset_x, y + offset_y), text, font=font, fill="white")  # White outline effect
        
        # Main text in the chosen color
        draw.text((x, y), text, font=font, fill=text_color)

        # Blur the background (excluding text)
        blurred_image = user_image.filter(ImageFilter.GaussianBlur(blur_radius))

        # Composite the blurred image with the text image
        final_image = Image.alpha_composite(blurred_image, text_image)

        # Save the image
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            output_path = temp_file.name
            final_image.save(output_path, "PNG")
        
        return output_path
    except Exception as e:
        logger.error(f"Error adding text to image: {e}")
        return None

# Convert image to JPG format (keeping final image as JPG)
def convert_to_jpg(png_path):
    try:
        with Image.open(png_path) as img:
            jpg_path = png_path.replace(".png", ".jpg")
            img.convert("RGB").save(jpg_path, "JPEG")
        return jpg_path
    except Exception as e:
        logger.error(f"Error converting PNG to JPG: {e}")
        return None

# Handle user interactions with buttons
@app.on_callback_query()
async def callback_handler(_, callback_query: CallbackQuery):
    await handle_callback(_, callback_query)  # Call the callback handler from callbacks.py

# Start the bot
if __name__ == "__main__":
    app.run()
    
