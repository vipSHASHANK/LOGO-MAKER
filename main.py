import logging
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps
import random
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Function to add text to user photo
def add_text_to_image(photo_path, text, output_path):
    try:
        # Load the user's photo
        user_image = Image.open(photo_path)
        user_image = user_image.convert("RGBA")  # Convert to RGBA for transparency

        # Create an ImageDraw object
        draw = ImageDraw.Draw(user_image)

        # Select random font
        font = ImageFont.truetype(random.choice(fonts), 100)  # Adjust font size as needed

        # Calculate text size and position
        text_width, text_height = draw.textsize(text, font=font)
        position = ((user_image.width - text_width) // 2, (user_image.height - text_height) // 2)

        # Add glow effect to text
        add_glow(draw, position, text, font, glow_color="red", text_color="white", glow_strength=15)

        # Save the final image with transparent background where necessary
        user_image.save(output_path, "PNG")
        return output_path
    except Exception as e:
        logger.error(f"Error adding text to image: {e}")
        return None

# Handler for when a user sends a photo
async def photo_handler(_, message: Message):
    if message.photo:
        # Save the received photo
        photo_path = f"user_photos/{message.photo.file_id}.jpg"
        await message.download(photo_path)

        # Ask the user to send the logo text
        await message.reply_text("Ab apna logo text bheje.")

        # Store the user's photo path and wait for text
        # (This can be done using a state management system like a dictionary or database)
        user_data[message.from_user.id] = {'photo_path': photo_path}

# Handler for receiving text and adding it to the photo
async def text_handler(_, message: Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        await message.reply_text("Pehle apna photo bheje.")
        return

    if message.text:
        user_text = message.text.strip()

        if not user_text:
            await message.reply_text("Logo text dena hoga.")
            return

        # Get the user's photo path
        photo_path = user_data[user_id]['photo_path']
        output_path = f"logos/{user_text}_logo.png"

        # Add the logo text to the photo
        result = add_text_to_image(photo_path, user_text, output_path)

        if result:
            # Send the updated photo to the user
            await message.reply_photo(output_path)

            # Optionally clear the user data after use
            del user_data[user_id]

# Main entry point to run the bot
if __name__ == "__main__":
    app = Client(
        "stylish_text_logo_bot_session",  # Session name
        bot_token=Config.BOT_TOKEN,
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
    )

    # Dictionary to store user data (photo and logo text)
    user_data = {}

    if app:
        # Handlers define karte hain
        app.on_message(filters.photo & filters.private)(photo_handler)
        app.on_message(filters.text & filters.private)(text_handler)

        # Bot ko run karte hain
        app.run()
    else:
        logger.error("Client banane mein kuch problem aayi.")
