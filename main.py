import os
import logging
import tempfile
from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, InputMediaPhoto
from config import Config

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

# Add text to image with red brush and white outline
async def add_text_to_image(photo_path, text, output_path, font_path):
    try:
        # Open the image
        user_image = Image.open(photo_path).convert("RGBA")
        max_width, max_height = user_image.size

        # Get the appropriate font
        font = get_dynamic_font(user_image, text, max_width, max_height, font_path)
        
        # Calculate text position
        draw = ImageDraw.Draw(user_image)
        text_width, text_height = draw.textsize(text, font=font)
        x = (max_width - text_width) // 2
        y = (max_height - text_height) // 2

        # White outline effect (brush)
        outline_width = 3
        for dx in [-outline_width, outline_width]:
            for dy in [-outline_width, outline_width]:
                draw.text((x + dx, y + dy), text, font=font, fill="white")

        # Red main text
        draw.text((x, y), text, font=font, fill="red")

        # Save the image to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            output_path = temp_file.name
            user_image.save(output_path, "PNG")
        
        return output_path
    except Exception as e:
        logger.error(f"Error adding text to image: {e}")
        return None

# Save user data
async def save_user_data(user_id, data):
    user_data_store[user_id] = data
    logger.info(f"User {user_id} data saved: {data}")

# Get user data
async def get_user_data(user_id):
    return user_data_store.get(user_id, None)

# Initialize the Pyrogram Client
session_name = "logo_creator_bot"
app = Client(
    session_name,
    bot_token=Config.BOT_TOKEN,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    workdir=os.getcwd()
)

@app.on_message(filters.command("start"))
async def start_command(_, message: Message) -> None:
    welcome_text = (
        "👋 Welcome to the Logo Creator Bot!\n\n"
        "With this bot, you can create a custom logo by sending a photo and adding text to it!\n"
    )
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Join 👋", url="https://t.me/BABY09_WORLD")]])
    await message.reply_text(welcome_text, reply_markup=keyboard, disable_web_page_preview=True)

@app.on_message(filters.photo & filters.private)
async def photo_handler(_, message: Message) -> None:
    media = message
    file_size = media.photo.file_size if media.photo else 0
    if file_size > 200 * 1024 * 1024:
        return await message.reply_text("Please provide a photo under 200MB.")
    try:
        text = await message.reply("Processing...")
        local_path = await media.download()
        await text.edit_text("Processing your logo...")
        await save_user_data(message.from_user.id, {'photo_path': local_path, 'text': '', 'text_position': (0, 0), 'size_multiplier': 1, 'glow_color': 'red'})
        await message.reply_text("Please send the text you want for your logo.")
    except Exception as e:
        logger.error(e)
        await text.edit_text("File processing failed.")

@app.on_message(filters.text & filters.private)
async def text_handler(_, message: Message) -> None:
    user_id = message.from_user.id
    user_data = await get_user_data(user_id)

    # Check if user has already provided text
    if not user_data:
        await message.reply_text("Please send a photo first.")
        return
    
    # Check if text has already been entered to prevent multiple prompts
    if user_data['text']:
        await message.reply_text("You have already entered text for the logo. Proceed with font and position selection.")
        return

    user_text = message.text.strip()
    if not user_text:
        await message.reply_text("You need to provide text for the logo.")
        return
    user_data['text'] = user_text
    await save_user_data(user_id, user_data)

    # Generate the logo immediately after user sends the text
    local_path = user_data['photo_path']
    text = user_data['text']
    font_path = "fonts/FIGHTBACK.ttf"  # Set your custom font path here

    # Use the simplified version of text addition
    output_path = await add_text_to_image(local_path, text, None, font_path)

    if output_path is None:
        await message.reply_text("There was an error generating the logo. Please try again.")
        return

    await message.reply_photo(photo=output_path)

# Start the bot
app.run()
