import os
import logging
import cv2
import numpy as np
from pyrogram import Client, filters
from pyrogram.types import Message
from PIL import Image, ImageEnhance, ImageFilter
from config import Config  # Ensure you have this file for your bot's config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up the Telegram bot client
app = Client(
    "photo_enhancer_bot",
    bot_token=Config.BOT_TOKEN,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
)

# Function to enhance image using Pillow (PIL) and OpenCV
def enhance_image(input_image_path, output_image_path):
    try:
        # Open image using Pillow
        img = Image.open(input_image_path)

        # 1. Contrast Enhancement
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.5)  # Adjust contrast

        # 2. Brightness Enhancement
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.5)  # Adjust brightness

        # 3. Sharpness Enhancement (using Pillow)
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2.0)  # Increase sharpness

        # 4. Vibrance Adjustment (Increase color saturation)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(2.0)  # Increase color saturation

        # 5. Gaussian Blur for smooth look
        img = img.filter(ImageFilter.GaussianBlur(radius=1))

        # Save the enhanced image
        img.save(output_image_path)

        # Apply OpenCV-based denoising and edge sharpening
        return apply_opencv_enhancements(output_image_path)
    
    except Exception as e:
        logger.error(f"Error enhancing image: {str(e)}")
        return None


def apply_opencv_enhancements(image_path):
    """Apply OpenCV denoising, contrast stretching, and edge sharpening."""
    # Read the image using OpenCV
    image = cv2.imread(image_path)

    # 1. Denoising (using OpenCV to reduce noise)
    denoised_image = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)

    # 2. Contrast Stretching (Auto-adjust contrast)
    lab = cv2.cvtColor(denoised_image, cv2.COLOR_BGR2Lab)
    l, a, b = cv2.split(lab)
    l = cv2.equalizeHist(l)  # Apply histogram equalization to L channel (luminance)
    lab = cv2.merge((l, a, b))
    contrast_stretched_image = cv2.cvtColor(lab, cv2.COLOR_Lab2BGR)

    # 3. Edge Sharpening (Using a kernel)
    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])  # Sharpening kernel
    sharpened_image = cv2.filter2D(contrast_stretched_image, -1, kernel)

    # Save the final enhanced image
    enhanced_image_path = "enhanced_" + os.path.basename(image_path)
    cv2.imwrite(enhanced_image_path, sharpened_image)

    return enhanced_image_path


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
    """Handles incoming photo messages, enhances them, and sends back the enhanced photo."""
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

        # Define the path for the enhanced image
        enhanced_image_path = "enhanced_" + os.path.basename(local_path)

        # Enhance the photo using Pillow and OpenCV
        enhanced_image = enhance_image(local_path, enhanced_image_path)

        if enhanced_image:
            await text.edit_text("Sending enhanced image...")
            # Send the enhanced image back to the user
            await message.reply_photo(enhanced_image)
        else:
            await text.edit_text("Error enhancing the image. Please try again later.")

        # Clean up the original and enhanced files after processing
        os.remove(local_path)
        os.remove(enhanced_image_path)

    except Exception as e:
        logger.error(f"Error in photo_handler: {str(e)}")
        await text.edit_text("Something went wrong. Please try again later.")
        if os.path.exists(local_path):
            os.remove(local_path)  # Clean up if download fails

if __name__ == "__main__":
    app.run()
