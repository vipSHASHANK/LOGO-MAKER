import os
import logging
import time
from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery, InputMediaPhoto
from config import Config  # Ensure you have this file for your bot's config
from private_buttons import create_font_buttons, POSITION_SIZE_BUTTONS, GLOW_COLOR_BUTTONS  # Button imports

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot Setup
app = Client(
    "logo_creator_bot",  # Unique session name
    bot_token=Config.BOT_TOKEN,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH
)

# Font options (path to your fonts)
FONT_OPTIONS = [
    {"name": "FIGHTBACK", "path": "fonts/FIGHTBACK.ttf"},
    {"name": "Arial", "path": "fonts/Lobster-Regular.ttf"},
    {"name": "Times New Roman", "path": "fonts/OpenSans-Regular.ttf"},
    {"name": "Courier", "path": "fonts/Pacifico-Regular.ttf"},
    {"name": "Verdana", "path": "fonts/Roboto-Regular.ttf"},
]

# Function to adjust font size dynamically
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

# Start bot with retry logic
def start_bot():
    try:
        app.run()
    except Exception as e:
        logger.error(f"Error: {e}")
        if "401 SESSION_REVOKED" in str(e):
            logger.error("Session was revoked. Attempting to restart the bot...")
            time.sleep(5)  # Wait before retrying
            start_bot()  # Retry starting the bot

# Handler for the '/start' command
@app.on_message(filters.command("start"))
async def start_command(_, message: Message) -> None:
    """Welcomes the user with instructions."""
    welcome_text = (
        "👋 Welcome to the Logo Creator Bot!\n\n"
        "With this bot, you can create logos. Just send a photo to get started!"
    )

    keyboard = [
        [InlineKeyboardButton("Join 👋", url="https://t.me/BABY09_WORLD")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await message.reply_text(welcome_text, reply_markup=reply_markup, disable_web_page_preview=True)

# Handler for incoming photos
@app.on_message(filters.photo & filters.private)
async def photo_handler(_, message: Message) -> None:
    """Handles incoming photo messages for logo creation."""
    try:
        local_path = await message.download()
        await message.reply_text("Photo received! Now, send the text for your logo.")

    except Exception as e:
        logger.error(f"Error in photo handling: {e}")
        await message.reply_text("Failed to process the photo. Please try again.")

# Handler for text input after photo
@app.on_message(filters.text & filters.private)
async def text_handler(_, message: Message) -> None:
    """Handles text input from user for logo text."""
    user_text = message.text.strip()

    if not user_text:
        return await message.reply_text("Please send some text for your logo.")

    await message.reply_text(f"Text for logo: {user_text}. Now, choose a font style.")

    # Proceed to font selection logic (can implement font selection buttons here)
    font_buttons = create_font_buttons()  # Assuming this function is in 'private_buttons.py'
    await message.reply_text(
        "Please choose a font for your logo:",
        reply_markup=InlineKeyboardMarkup([font_buttons])
    )

# Handler for font selection
@app.on_callback_query(filters.regex("^font_"))
async def font_button_handler(_, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    selected_font_name = callback_query.data.split("_")[1]
    selected_font = next((font for font in FONT_OPTIONS if font['name'] == selected_font_name), None)

    if selected_font:
        user_data = {
            "selected_font": selected_font['path'],
            "text": callback_query.message.text.strip()
        }

        # Create logo with selected font
        photo_path = "path_to_user_photo"  # Should be saved somewhere when photo is received
        output_path = f"logos/updated_{user_data['text']}_logo.png"
        result = await add_text_to_image(photo_path, user_data['text'], output_path, font_path=selected_font['path'])

        if result:
            media = InputMediaPhoto(media=output_path, caption="Here's your logo!")
            await callback_query.message.edit_media(media=media)
            await callback_query.answer(f"Font changed to {selected_font_name}")

# Error Handling (Generic Exception Handler)
@app.on_message(filters.private)
async def generic_error_handler(_, message: Message):
    try:
        # Your regular handler logic here
        pass
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        await message.reply_text(f"An error occurred: {str(e)}")

# Start the bot
if __name__ == "__main__":
    start_bot()  # Run bot with retry logic
                       
