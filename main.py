import os
import logging
import tempfile
from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery, InputMediaPhoto
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

# Define inline keyboard for adjustments
def get_adjustment_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Left", callback_data="move_left"),
         InlineKeyboardButton("➡️ Right", callback_data="move_right")],
        [InlineKeyboardButton("⬆️ Up", callback_data="move_up"),
         InlineKeyboardButton("⬇️ Down", callback_data="move_down")],
        [InlineKeyboardButton("🔍 Increase", callback_data="increase_size"),
         InlineKeyboardButton("🔎 Decrease", callback_data="decrease_size")]
    ])

# Add text to image with adjustments
async def add_text_to_image(photo_path, text, output_path, font_path, text_position, size_multiplier):
    try:
        user_image = Image.open(photo_path).convert("RGBA")
        max_width, max_height = user_image.size

        # Adjust font size based on size_multiplier
        font = get_dynamic_font(user_image, text, max_width, max_height, font_path)
        font = ImageFont.truetype(font_path, int(font.size * size_multiplier))
        
        draw = ImageDraw.Draw(user_image)
        text_width, text_height = draw.textsize(text, font=font)
        
        # Apply position adjustments
        x = text_position[0]
        y = text_position[1]

        # Outline effect
        outline_width = 3
        for dx in [-outline_width, outline_width]:
            for dy in [-outline_width, outline_width]:
                draw.text((x + dx, y + dy), text, font=font, fill="white")

        # Red main text
        draw.text((x, y), text, font=font, fill="red")

        # Save the image
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
        await save_user_data(message.from_user.id, {'photo_path': local_path, 'text': '', 'text_position': (0, 0), 'size_multiplier': 1})
        await message.reply_text("Please send the text you want for your logo.")
    except Exception as e:
        logger.error(e)
        await text.edit_text("File processing failed.")

@app.on_message(filters.text & filters.private)
async def text_handler(_, message: Message) -> None:
    user_id = message.from_user.id
    user_data = await get_user_data(user_id)

    if not user_data:
        await message.reply_text("Please send a photo first.")
        return
    
    if user_data['text']:
        await message.reply_text("You have already entered text for the logo. Proceed with position adjustments.")
        return

    user_text = message.text.strip()
    if not user_text:
        await message.reply_text("You need to provide text for the logo.")
        return
    user_data['text'] = user_text
    await save_user_data(user_id, user_data)

    # Generate logo and show adjustment options
    font_path = "fonts/FIGHTBACK.ttf"
    output_path = await add_text_to_image(user_data['photo_path'], user_text, None, font_path, user_data['text_position'], user_data['size_multiplier'])

    if output_path is None:
        await message.reply_text("There was an error generating the logo. Please try again.")
        return

    await message.reply_photo(photo=output_path, reply_markup=get_adjustment_keyboard())

@app.on_callback_query()
async def callback_handler(_, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user_data = await get_user_data(user_id)

    if not user_data or not user_data.get("photo_path"):
        await callback_query.answer("Please upload a photo first.", show_alert=True)
        return

    # Adjust position or size based on button pressed
    if callback_query.data == "move_left":
        user_data['text_position'] = (user_data['text_position'][0] - 20, user_data['text_position'][1])
    elif callback_query.data == "move_right":
        user_data['text_position'] = (user_data['text_position'][0] + 20, user_data['text_position'][1])
    elif callback_query.data == "move_up":
        user_data['text_position'] = (user_data['text_position'][0], user_data['text_position'][1] - 20)
    elif callback_query.data == "move_down":
        user_data['text_position'] = (user_data['text_position'][0], user_data['text_position'][1] + 20)
    elif callback_query.data == "increase_size":
        user_data['size_multiplier'] *= 1.1
    elif callback_query.data == "decrease_size":
        user_data['size_multiplier'] *= 0.9

    await save_user_data(user_id, user_data)

    # Re-generate the image with new adjustments
    font_path = "fonts/FIGHTBACK.ttf"
    output_path = await add_text_to_image(user_data['photo_path'], user_data['text'], None, font_path, user_data['text_position'], user_data['size_multiplier'])

    if output_path is None:
        await callback_query.message.reply_text("There was an error generating the logo. Please try again.")
        return

    await callback_query.message.edit_media(InputMediaPhoto(media=output_path), reply_markup=get_adjustment_keyboard())
    await callback_query.answer()

# Start the bot
app.run()
