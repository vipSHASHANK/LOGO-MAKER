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
PICSART_API_KEY = 'eyJraWQiOiI5NzIxYmUzNi1iMjcwLTQ5ZDUtOTc1Ni05ZDU5N2M4NmIwNTEiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJhdXRoLXNlcnZpY2UtOTAzZjNhYWMtYjk1Ny00ZTNlLWJkOGEtN2Y3YzgwYjliY2MzIiwiYXVkIjoiNDY3MzgxMTczMDA4MTAxIiwibmJmIjoxNzMwNzkyNDIxLCJzY29wZSI6WyJiMmItYXBpLmdlbl9haSIsImIyYi1hcGkuaW1hZ2VfYXBpIl0sImlzcyI6Imh0dHBzOi8vYXBpLnBpY3NhcnQuY29tL3Rva2VuLXNlcnZpY2UiLCJvd25lcklkIjoiNDY3MzgxMTczMDA4MTAxIiwiaWF0IjoxNzMwNzkyNDIxLCJqdGkiOiIyY2EwYzdmMy1lZjE4LTQzYTYtOTZjNy00OGZjMzllNTE0MjIifQ.O4CFcvA9xIcrYPc_-JgYPHVtsfUYCGVtqlvkK3yIY_hDQ0qOsEayNXs2VICqxGQIdDF3_GgCZuopYQokUoMACmwo7r-bcuJ6PsbJuvW8Yo_hPdUsXaicD_Wnxu7lt4Gijh1EWSJrx7s7KjBdu6LOpvzOAXurp57Wabos1fSdY4AWd26OMU6bk2hBRNC0oJ5O30jRvxUm74W_xnswbEfd2KIj63drHQApZCp1UCVKooI_E3P3SJUygNVtJm3ucSOUwfSPlUSyueEusfK_EBhNfBGXegkJL0KXABaImUfjiFs02r4MIkqw0Mhz67SBLUcy5ebGblX8aJ2IgZOQQ18Trw'  # Replace this with your Picsart API key
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
