import os
import logging
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config  # Ensure you have this file for your bot's config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Client(
    "remini_enhancer",
    bot_token=Config.BOT_TOKEN,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
)

# DeepAI Image Enhancement API URL
DEEPAI_API_URL = "https://api.deepai.org/api/torch-srgan"  # URL for DeepAI's image enhancement API
DEEPAI_API_KEY = 'your-deepai-api-key-here'  # Replace with your actual DeepAI API key

# Function to enhance photo using DeepAI's API
def enhance_with_deepai(file_path):
    try:
        # Open the image file to send to DeepAI's API
        with open(file_path, 'rb') as image_file:
            response = requests.post(
                DEEPAI_API_URL,
                files={'image': image_file},
                headers={'api-key': DEEPAI_API_KEY}
            )

        # If the request is successful, return the enhanced image URL
        if response.status_code == 200:
            result = response.json()
            enhanced_image_url = result.get('output_url')
            return enhanced_image_url
        else:
            logger.error(f"Error enhancing image: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error enhancing image: {str(e)}")
        return None

@app.on_message(filters.command("start"))
async def start_command(_, message: Message) -> None:
    """Welcomes the user with instructions."""
    welcome_text = (
        "👋 Welcome to the Photo Enhancer Bot!\n\n"
        "Just send me a photo, and I'll enhance it using AI and send it back to you!"
    )

    await message.reply_text(welcome_text, disable_web_page_preview=True)

@app.on_message(filters.photo & filters.incoming & filters.private)
async def photo_handler(_, message: Message) -> None:
    """Handles incoming photo messages, enhances them with DeepAI, and sends the enhanced photo back."""
    media = message
    file_size = media.photo.file_size if media.photo else 0

    if file_size > 200 * 1024 * 1024:
        return await message.reply_text("Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴘʜᴏᴛᴏ ᴜɴᴅᴇʀ 200MB.")

    try:
        # Download the photo
        text = await message.reply("Processing...")

        local_path = await media.download()

        # Enhance the photo using DeepAI API
        enhanced_image_url = enhance_with_deepai(local_path)

        if enhanced_image_url:
            await text.edit_text("Sending enhanced image...")

            # Send the enhanced image URL back to the user
            await message.reply_text(f"Your enhanced image: {enhanced_image_url}")

        else:
            await text.edit_text("Error enhancing the image. Please try again later.")

        os.remove(local_path)  # Clean up the original file after processing

    except Exception as e:
        logger.error(e)
        await text.edit_text("Something went wrong. Please try again later.")
        if os.path.exists(local_path):
            os.remove(local_path)  # Clean up if download fails

if __name__ == "__main__":
    app.run()
