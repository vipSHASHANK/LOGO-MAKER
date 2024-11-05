import os
import logging
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config  # Ensure you have this file for your bot's config
from pyrogram.errors import SessionRevoked
import sqlite3

# Logging Setup
logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG to get detailed logs
logger = logging.getLogger(__name__)

# PixelCut API setup
PIXELCUT_API_KEY = "sk_43374ec592354e4295b023151243efa4"
PIXELCUT_API_URL = "https://api.pixelcut.ai/v1/enhance"  # Assuming this is the correct endpoint, check PixelCut API docs

# Function to set WAL mode for SQLite (to avoid database locked errors)
def set_wal_mode(session_name="photo_enhancer_session"):
    try:
        connection = sqlite3.connect(f"{session_name}.session")  # Using session file name
        connection.execute("PRAGMA journal_mode=WAL;")
        connection.close()
        logger.info("WAL mode enabled for SQLite.")
    except Exception as e:
        logger.error(f"Failed to set WAL mode: {e}")

# Function to delete the session file if it exists
def delete_session_file(session_name="photo_enhancer_session"):
    session_file = f"{session_name}.session"
    if os.path.exists(session_file):
        os.remove(session_file)
        logger.info(f"Session file '{session_file}' deleted successfully.")

# Create client function
def create_client(session_name="photo_enhancer_session"):
    delete_session_file(session_name)  # Delete any existing session file before starting
    set_wal_mode(session_name)  # Set WAL mode before creating the client
    return Client(
        session_name,
        bot_token=Config.BOT_TOKEN,
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
    )

# Function to enhance image using PixelCut API
def enhance_image_with_pixelcut(image_path):
    try:
        # Read the image file
        with open(image_path, "rb") as img_file:
            files = {"file": img_file}
            headers = {"Authorization": f"Bearer {PIXELCUT_API_KEY}"}

            # Make the request to the PixelCut API
            response = requests.post(PIXELCUT_API_URL, files=files, headers=headers)

            # Check if the request was successful
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

# Create a client for the bot
app = create_client("photo_enhancer_session")

@app.on_message(filters.command("start"))
async def start_command(_, message: Message) -> None:
    """Welcome the user with instructions."""
    welcome_text = (
        "👋 Welcome to the Image Enhancer Bot!\n\n"
        "Send me a photo, and I'll enhance it using AI!"
    )
    await message.reply_text(welcome_text, disable_web_page_preview=True)

@app.on_message(filters.photo & filters.incoming & filters.private)
async def photo_handler(_, message: Message) -> None:
    """Handle incoming photo messages, enhance them using PixelCut, and send back."""
    media = message
    file_size = media.photo.file_size if media.photo else 0

    # Check if the image is too large (max 200MB)
    if file_size > 200 * 1024 * 1024:
        return await message.reply_text("Please provide a photo under 200MB.")

    try:
        # Show processing message
        text = await message.reply("Processing...")

        # Download the image
        local_path = await media.download()

        # Enhance the image using PixelCut API
        enhanced_image = enhance_image_with_pixelcut(local_path)

        if enhanced_image:
            await text.edit_text("Sending enhanced image...")
            # Send the enhanced image back to the user
            await message.reply_photo(enhanced_image)
        else:
            await text.edit_text("Error enhancing the image. Please try again later.")

        # Clean up the original and enhanced files after processing
        os.remove(local_path)
        os.remove(enhanced_image)

    except Exception as e:
        logger.error(f"Error in photo_handler: {str(e)}")
        await text.edit_text("Something went wrong. Please try again later.")
        if os.path.exists(local_path):
            os.remove(local_path)  # Clean up if download fails

if __name__ == "__main__":
    try:
        # Run the bot
        app.run()
    except SessionRevoked:
        logger.error("Session revoked. Please restart the bot.")
    except Exception as e:
        logger.error(f"Something went wrong: {e}")
