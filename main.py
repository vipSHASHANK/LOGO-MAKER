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

# Font options
FONT_OPTIONS = [
    {"name": "FIGHTBACK", "path": "fonts/FIGHTBACK.ttf"},
    {"name": "Arial", "path": "fonts/Lobster-Regular.ttf"},
    {"name": "Times New Roman", "path": "fonts/OpenSans-Regular.ttf"},
    {"name": "Courier", "path": "fonts/Pacifico-Regular.ttf"},
    {"name": "Verdana", "path": "fonts/Roboto-Regular.ttf"},
]

# Adjust font size dynamically
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

# Add text to image without 3D effect
async def add_text_to_image(photo_path, text, output_path, x_offset=0, y_offset=0, size_multiplier=1, text_color="white", font_path=None):
    try:
        # Open the image
        user_image = Image.open(photo_path).convert("RGBA")
        max_width, max_height = user_image.size
        
        # Get the appropriate font and text size
        font, text_width, text_height = get_dynamic_font(user_image, text, max_width, max_height, font_path)
        
        # Adjust the text size according to the size multiplier
        text_width = int(text_width * size_multiplier)
        text_height = int(text_height * size_multiplier)
        
        # Ensure x_offset and y_offset are integers
        x = (max_width - text_width) // 2 + int(x_offset)  # Ensure x_offset is an integer
        y = (max_height - text_height) // 2 + int(y_offset)  # Ensure y_offset is an integer
        text_position = (x, y)

        # Draw the text onto the image
        draw = ImageDraw.Draw(user_image)
        draw.text(text_position, text, font=font, fill=text_color)

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

    if not user_data:
        await message.reply_text("Please send a photo first.")
        return
    
    if user_data['text']:
        await message.reply_text("You have already entered text for the logo. Proceed with font and position selection.")
        return

    user_text = message.text.strip()
    if not user_text:
        await message.reply_text("You need to provide text for the logo.")
        return
    user_data['text'] = user_text
    await save_user_data(user_id, user_data)

    local_path = user_data['photo_path']
    text = user_data['text']
    position = user_data['text_position']
    size_multiplier = user_data['size_multiplier']
    glow_color = user_data['glow_color']

    output_path = await add_text_to_image(local_path, text, None, x_offset=position[0], y_offset=position[1], size_multiplier=size_multiplier, text_color=glow_color)

    if output_path is None:
        await message.reply_text("There was an error generating the logo. Please try again.")
        return

    position_buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Left", callback_data="position_left"),
            InlineKeyboardButton("Right", callback_data="position_right")
        ],
        [
            InlineKeyboardButton("Up", callback_data="position_up"),
            InlineKeyboardButton("Down", callback_data="position_down")
        ]
    ])

    size_buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Zoom In", callback_data="size_1.5"),
            InlineKeyboardButton("Zoom Out", callback_data="size_0.8")
        ]
    ])

    color_buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Red", callback_data="color_red"),
            InlineKeyboardButton("Blue", callback_data="color_blue"),
            InlineKeyboardButton("White", callback_data="color_white")
        ]
    ])

    keyboard = position_buttons.inline_keyboard + size_buttons.inline_keyboard + color_buttons.inline_keyboard

    await message.reply_photo(photo=output_path, reply_markup=InlineKeyboardMarkup(keyboard))

@app.on_callback_query(filters.regex("position_"))
async def position_callback(_, callback_query):
    user_id = callback_query.from_user.id
    position = callback_query.data.split("_")[1]
    user_data = await get_user_data(user_id)
    
    x_offset, y_offset = 0, 0

    if position == "left":
        x_offset = -100
    elif position == "right":
        x_offset = 100
    elif position == "up":
        y_offset = -100
    elif position == "down":
        y_offset = 100

    user_data['text_position'] = (x_offset, y_offset)
    await save_user_data(user_id, user_data)

    local_path = user_data['photo_path']
    text = user_data['text']
    size_multiplier = user_data['size_multiplier']
    glow_color = user_data['glow_color']

    new_logo_path = await add_text_to_image(local_path, text, None, 
                                             x_offset=x_offset, y_offset=y_offset,
                                             size_multiplier=size_multiplier, text_color=glow_color)

    if new_logo_path is None:
        await callback_query.message.edit_text("There was an error generating the logo.")
        return

    position_buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Left", callback_data="position_left"),
            InlineKeyboardButton("Right", callback_data="position_right")
        ],
        [
            InlineKeyboardButton("Up", callback_data="position_up"),
            InlineKeyboardButton("Down", callback_data="position_down")
        ]
    ])

    size_buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Zoom In", callback_data="size_1.5"),
            InlineKeyboardButton("Zoom Out", callback_data="size_0.8")
        ]
    ])

    color_buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Red", callback_data="color_red"),
            InlineKeyboardButton("Blue", callback_data="color_blue"),
            InlineKeyboardButton("White", callback_data="color_white")
        ]
    ])

    keyboard = position_buttons.inline_keyboard + size_buttons.inline_keyboard + color_buttons.inline_keyboard

    media = InputMediaPhoto(media=new_logo_path)
    await callback_query.message.edit_media(
        media=media,  # Use InputMediaPhoto instead of dict
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await callback_query.answer(f"Position updated to {position}!")

@app.on_callback_query(filters.regex("size_"))
async def size_callback(_, callback_query):
    user_id = callback_query.from_user.id
    size = callback_query.data.split("_")[1]
    user_data = await get_user_data(user_id)

    user_data['size_multiplier'] = float(size)
    await save_user_data(user_id, user_data)

    await callback_query.answer(f"Size multiplier set to {size}!")
    await callback_query.message.edit_text(f"Size: {size}. Now, choose color!")

@app.on_callback_query(filters.regex("color_"))
async def color_callback(_, callback_query):
    user_id = callback_query.from_user.id
    color = callback_query.data.split("_")[1]
    user_data = await get_user_data(user_id)

    user_data['glow_color'] = color
    await save_user_data(user_id, user_data)

    await callback_query.answer(f"Glow color set to {color}!")
    await callback_query.message.edit_text(f"Glow color: {color}. Your logo is ready!")

# Start the bot
app.run()
