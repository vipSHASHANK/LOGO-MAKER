import logging
import os
from PIL import Image, ImageDraw, ImageFont
import pyfiglet
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to create images with stylish text
def generate_stylish_logo(text, font_path, output_path):
    """Stylish text ko image format mein generate karne ka function."""
    try:
        # Image create karte hain (white background)
        width, height = 800, 200  # Image size
        image = Image.new('RGB', (width, height), color='white')  # Create a white canvas
        draw = ImageDraw.Draw(image)

        # Font ko load karte hain
        font = ImageFont.truetype(font_path, 80)

        # Text ka width aur height calculate karte hain
        text_width, text_height = draw.textsize(text, font=font)
        position = ((width - text_width) // 2, (height - text_height) // 2)

        # Text ko image par draw karte hain
        draw.text(position, text, fill="black", font=font)

        # Image save karte hain
        image.save(output_path)
        return output_path
    except Exception as e:
        logger.error(f"Font {font_path} ke saath image generate karte waqt error: {e}")
        return None

# Function to convert user text into 10 different stylish logos
def convert_to_logo_images(user_text):
    """User ke text ko 10 alag-alag logo images mein convert kare."""
    # pyfiglet fonts ki list
    available_fonts = pyfiglet.FigletFont.getFonts()

    # Output directory banate hain
    output_dir = "logos"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    image_paths = []
    
    # 10 fonts select karte hain (pehle 10 fonts lete hain)
    fonts = available_fonts[:10]  # Pehle 10 fonts se images generate karenge
    
    for i, font in enumerate(fonts):
        try:
            # pyfiglet ka use karke text ko stylish font mein convert karte hain
            figlet_text = pyfiglet.figlet_format(user_text, font=font)
            
            # Image ka path banate hain
            image_path = os.path.join(output_dir, f"{user_text}_{i + 1}.png")
            
            # Image ko generate karte hain
            if generate_stylish_logo(figlet_text, font, image_path):
                image_paths.append(image_path)
        except Exception as e:
            logger.error(f"Font '{font}' ke liye image generate karte waqt error: {e}")

    return image_paths

# Text handler (user ka text receive karna aur usko image format mein reply dena)
async def text_handler(_, message: Message) -> None:
    """User ka text receive karke usko stylish logo images ke roop mein reply karna."""
    if message.text:
        user_text = message.text.strip()

        if not user_text:
            await message.reply_text("Kripya kuch text bhejein jise main style kar sakoon.")
            return
        
        # Text ko 10 stylish logo images mein convert karte hain
        image_paths = convert_to_logo_images(user_text)
        
        # Har image ko user ko bhejte hain
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
