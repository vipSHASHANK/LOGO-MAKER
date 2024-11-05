import os
import logging
import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from config import Config  # Ensure you have this file for your bot's config
from PIL import Image
from io import BytesIO

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the bot client
app = Client(
    "photo_enhancer_bot",
    bot_token=Config.BOT_TOKEN,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
)

# PixelCut API setup (or any enhancement API you want to use)
PIXELCUT_API_KEY = "sk_43374ec592354e4295b023151243efa4"
PIXELCUT_API_URL = "https://api.pixelcut.ai/v1/enhance"  # Assuming this is the correct endpoint

# Function to enhance the image using PixelCut API
def enhance_image_with_pixelcut(image_path):
    try:
        with open(image_path, "rb") as img_file:
            files = {"file": img_file}
            headers = {"Authorization": f"Bearer {PIXELCUT_API_KEY}"}

            # Make the request to the PixelCut API
            response = requests.post(PIXELCUT_API_URL, files=files, headers=headers)

            if response.status_code == 200:
                # Save the enhanced image
                enhanced_image_path = "enhanced_" + os.path.basename(image_path)
                with open(enhanced_image_path, "wb") as out_file:
                    out_file.write(response.content)
                return enhanced_image_path
            else:
                logger.error(f"Error from PixelCut API: {response.text}")
                return None
    except Exception as e:
        logger.error(f"Error enhancing image with PixelCut: {e}")
        return None

@app.on_message(filters.command("start"))
async def start_command(_, message: Message) -> None:
    """Welcomes the user with instructions."""
    welcome_text = (
        "👋 Welcome to the Image Enhancer Bot!\n\n"
        "Send me a photo, and I will enhance it for you!"
    )

    keyboard = [
        [InlineKeyboardButton("Join 👋", url="https://t.me/BABY09_WORLD")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await message.reply_text(welcome_text, reply_markup=reply_markup, disable_web_page_preview=True)

@app.on_message(filters.photo & filters.incoming & filters.private)
async def photo_handler(_, message: Message) -> None:
    """Handles incoming photo messages by enhancing them."""
    media = message
    file_size = media.photo.file_size if media.photo else 0

    if file_size > 200 * 1024 * 1024:
        return await message.reply_text("Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴘʜᴏᴛᴏ ᴜɴᴅᴇʀ 200MB.")

    try:
        text = await message.reply("Processing...")

        # Download the image
        local_path = await media.download()

        # Enhance the image using PixelCut API
        enhanced_image = enhance_image_with_pixelcut(local_path)

        if enhanced_image:
            await text.edit_text("Enhancement completed, sending back...")

            # Send the enhanced image back to the user
            await message.reply_photo(enhanced_image)
        else:
            await text.edit_text("❍ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ᴇɴʜᴀɴᴄɪɴɢ.")

        # Clean up the original and enhanced files after processing
        os.remove(local_path)
        os.remove(enhanced_image)

    except Exception as e:
        logger.error(e)
        await text.edit_text("File enhancement failed.")
        if os.path.exists(local_path):
            os.remove(local_path)  # Clean up if download fails

if __name__ == "__main__":
    app.run()
