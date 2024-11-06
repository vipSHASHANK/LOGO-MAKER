import os
import logging
from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from config import Config
from private_buttons import create_font_buttons, create_position_buttons, create_size_buttons, create_color_buttons

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

# Function to dynamically adjust font size
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

# Function to add 3D text effect
def add_3d_text(draw, position, text, font, glow_color, text_color, shadow_offset=(5, 5), glow_strength=5):
    x, y = position
    
    # Shadow effect
    shadow_x = x + shadow_offset[0]
    shadow_y = y + shadow_offset[1]
    draw.text((shadow_x, shadow_y), text, font=font, fill="black")

    # Glow effect
    for offset in range(1, glow_strength + 1):
        draw.text((x - offset, y - offset), text, font=font, fill=glow_color)
        draw.text((x + offset, y - offset), text, font=font, fill=glow_color)
        draw.text((x - offset, y + offset), text, font=font, fill=glow_color)
        draw.text((x + offset, y + offset), text, font=font, fill=glow_color)

    # Main text
    draw.text((x, y), text, font=font, fill=text_color)

# Function to add text to the image
async def add_text_to_image(photo_path, text, output_path, x_offset=0, y_offset=0, size_multiplier=1, glow_color="red", font_path=None):
    try:
        user_image = Image.open(photo_path)
        user_image = user_image.convert("RGBA")  # Convert to RGBA mode

        max_width, max_height = user_image.size
        font, text_width, text_height = get_dynamic_font(user_image, text, max_width, max_height, font_path)

        # Adjust text size
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

# Function to save user data
async def save_user_data(user_id, data):
    user_data_store[user_id] = data
    logger.info(f"User {user_id} data saved: {data}")

# Function to get user data
async def get_user_data(user_id):
    return user_data_store.get(user_id, None)

# Initialize the Pyrogram Client
session_name = "logo_creator_bot"  # Set a session name to manage multiple sessions
app = Client(
    session_name,  # Use a session name for better session management
    bot_token=Config.BOT_TOKEN,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    workdir=os.getcwd()  # Make sure the working directory is set to the current directory
)

# Start command handler
@app.on_message(filters.command("start"))
async def start_command(_, message: Message) -> None:
    """Welcomes the user with instructions."""
    welcome_text = (
        "👋 Welcome to the Logo Creator Bot!\n\n"
        "With this bot, you can create a custom logo by sending a photo and adding text to it!\n"
    )

    keyboard = [
        [InlineKeyboardButton("Join 👋", url="https://t.me/BABY09_WORLD")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await message.reply_text(welcome_text, reply_markup=reply_markup, disable_web_page_preview=True)

# Photo handler
@app.on_message(filters.photo & filters.private)
async def photo_handler(_, message: Message) -> None:
    """Handles incoming photo messages."""
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

# Text handler
@app.on_message(filters.text & filters.private)
async def text_handler(_, message: Message) -> None:
    """Handles incoming text for logo creation."""
    user_id = message.from_user.id
    user_data = await get_user_data(user_id)

    if not user_data:
        await message.reply_text("Please send a photo first.")
        return

    user_text = message.text.strip()

    if not user_text:
        await message.reply_text("You need to provide text for the logo.")
        return

    user_data['text'] = user_text
    await save_user_data(user_id, user_data)

    font_buttons = create_font_buttons()
    await message.reply_text(
        "Choose a font:", 
        reply_markup=InlineKeyboardMarkup([font_buttons])
    )

# Font selection handler
@app.on_message(filters.regex("font_") & filters.private)
async def font_handler(_, message: Message) -> None:
    """Handles font selection."""
    user_id = message.from_user.id
    user_data = await get_user_data(user_id)

    if not user_data:
        await message.reply_text("Please send a photo first.")
        return

    font_choice = message.text.strip().split('_')[1]
    selected_font = next((font for font in FONT_OPTIONS if font['name'].lower() == font_choice.lower()), None)

    if selected_font:
        user_data['font'] = selected_font
        await save_user_data(user_id, user_data)

        await message.reply_text(f"You selected the font '{selected_font['name']}'.")

        color_buttons = create_color_buttons()
        await message.reply_text("Choose a color for your logo text:", reply_markup=InlineKeyboardMarkup(color_buttons))

# Color selection handler
@app.on_message(filters.regex("color_") & filters.private)
async def color_handler(_, message: Message) -> None:
    """Handles color selection."""
    user_id = message.from_user.id
    user_data = await get_user_data(user_id)

    if not user_data:
        await message.reply_text("Please send a photo first.")
        return

    user_color = message.text.strip().split('_')[1]
    user_data['glow_color'] = user_color
    await save_user_data(user_id, user_data)

    await message.reply_text(f"You selected the color '{user_color}'.")

    position_buttons = create_position_buttons()
    await message.reply_text("Choose the position for your logo text:", reply_markup=InlineKeyboardMarkup(position_buttons))

# Position selection handler
@app.on_message(filters.regex("position_") & filters.private)
async def position_handler(_, message: Message) -> None:
    """Handles position selection."""
    user_id = message.from_user.id
    user_data = await get_user_data(user_id)

    if not user_data:
        await message.reply_text("Please send a photo first.")
        return

    position = message.text.strip().split('_')[1]
    user_data['position'] = position
    await save_user_data(user_id, user_data)

    await message.reply_text(f"Position '{position}' selected.")

    size_buttons = create_size_buttons()
    await message.reply_text("Choose the size for your logo:", reply_markup=InlineKeyboardMarkup(size_buttons))

# Size selection handler
@app.on_message(filters.regex("size_") & filters.private)
async def size_handler(_, message: Message) -> None:
    """Handles size selection."""
    user_id = message.from_user.id
    user_data = await get_user_data(user_id)

    if not user_data:
        await message.reply_text("Please send a photo first.")
        return

    size = message.text.strip().split('_')[1]
    size_multiplier = 1 if size == "small" else 1.5
    user_data['size_multiplier'] = size_multiplier
    await save_user_data(user_id, user_data)

    photo_path = user_data['photo_path']
    text = user_data['text']
    output_path = f"user_photos/output_{user_id}.png"

    added_text_image = await add_text_to_image(
        photo_path, text, output_path, size_multiplier=size_multiplier, glow_color=user_data['glow_color'], font_path=user_data['font']['path']
    )

    if added_text_image:
        await message.reply_photo(added_text_image, caption="Here is your logo!")
    else:
        await message.reply_text("Something went wrong while creating the logo.")

if __name__ == "__main__":
    app.run()
        
