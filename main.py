import os
import logging
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config  # Ensure you have this file for your bot's config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Picsart API Key and URL
PICSART_API_KEY = 'eyJraWQiOiI5NzIxYmUzNi1iMjcwLTQ5ZDUtOTc1Ni05ZDU5N2M4NmIwNTEiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJhdXRoLXNlcnZpY2UtYmI1YTEzNDYtOWQ0MC00NmI4LWJlMGMtOWQ4ZDFiZmZiMDAxIiwiYXVkIjoiNDY3MzgxMTczMDA4MTAxIiwibmJmIjoxNzMwNzkzMDE0LCJzY29wZSI6WyJiMmItYXBpLmdlbl9haSIsImIyYi1hcGkuaW1hZ2VfYXBpIl0sImlzcyI6Imh0dHBzOi8vYXBpLnBpY3NhcnQuY29tL3Rva2VuLXNlcnZpY2UiLCJvd25lcklkIjoiNDY3MzgxMTczMDA4MTAxIiwiaWF0IjoxNzMwNzkzMDE0LCJqdGkiOiJhNjM3Yzk3ZS02Zjk4LTQwMmUtOGE2Zi0xYWM1NzBhYmRkN2MifQ.NA4CgiP0K7UFUDMgL88MKklsrBjQhPp-6YsXEkcdhOORivSdwHDSXrBfX_Iy6jh-_vbuL19d0uCuhSWRgFKls81C4b2UOm4S9ESkxZqcS52xvID9dVDDvmuIYCAepKDG8tsEYXpEfqbo9RgwOv1J0dr6sjv_A90PoFi2IOIhU2oyrmHwwTw33nRatAEh6Gq9UxR05i6WGef670_z1QuIMcRf0RI3_0DDtq8UfgF5cSmDLZ1US74PdH8VFQMdojVOLFAXJYSyFxjZm77Fzolh1Bpu7A7xSS9S8Rad02Tvk1UvKJJotUXi5kPGgMJ606669a87vvYv-lWIEqwqtUPZVA'  # Replace this with your Picsart API key
PICSART_API_URL = "https://api.picsart.io/v1/ai/image/enhance"

# Set up the Telegram bot client
app = Client(
    "photo_enhancer_bot",
    bot_token=Config.BOT_TOKEN,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
)

# Function to enhance image using Picsart API
def enhance_with_picsart(file_path):
    try:
        # Open the image file to send to Picsart API
        with open(file_path, 'rb') as image_file:
            files = {'image': image_file}
            headers = {'Authorization': f'Bearer {PICSART_API_KEY}'}

            # Log the request to ensure we're sending it properly
            logger.info(f"Sending request to Picsart API with key: {PICSART_API_KEY}")

            # Send POST request to the Picsart API for enhancement
            response = requests.post(PICSART_API_URL, files=files, headers=headers)
            
            # Log the API response for debugging
            logger.info(f"Response from Picsart API: {response.status_code}, {response.text}")

            # If the API call is successful, return the enhanced image URL
            if response.status_code == 200:
                result = response.json()
                enhanced_image_url = result.get('url')  # Getting the enhanced image URL
                return enhanced_image_url
            else:
                logger.error(f"Error from Picsart API: {response.text}")
                return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception: {e}")
        return None
    except Exception as e:
        logger.error(f"General error: {e}")
        return None

@app.on_message(filters.command("start"))
async def start_command(_, message: Message) -> None:
    """Welcomes the user with instructions."""
    welcome_text = (
        "👋 Welcome to the Image Enhancer Bot!\n\n"
        "Send me a photo, and I'll enhance it using AI!"
    )

    await message.reply_text(welcome_text, disable_web_page_preview=True)

@app.on_message(filters.photo & filters.incoming & filters.private)
async def photo_handler(_, message: Message) -> None:
    """Handles incoming photo messages, enhances them with Picsart API, and sends back the enhanced photo."""
    media = message
    file_size = media.photo.file_size if media.photo else 0

    # Check if the image size is too large (max 200MB)
    if file_size > 200 * 1024 * 1024:
        return await message.reply_text("Please provide a photo under 200MB.")

    try:
        # Download the photo to a local file
        text = await message.reply("Processing...")

        # Download the image to local storage
        local_path = await media.download()

        # Enhance the photo using Picsart API
        enhanced_image_url = enhance_with_picsart(local_path)

        if enhanced_image_url:
            await text.edit_text("Sending enhanced image...")

            # Send the enhanced image URL back to the user
            await message.reply_text(f"Your enhanced image: {enhanced_image_url}")
        else:
            await text.edit_text("Error enhancing the image. Please try again later.")

        # Clean up the original file after processing
        os.remove(local_path)

    except Exception as e:
        logger.error(f"Error in photo_handler: {str(e)}")
        await text.edit_text("Something went wrong. Please try again later.")
        if os.path.exists(local_path):
            os.remove(local_path)  # Clean up if download fails

if __name__ == "__main__":
    app.run()
