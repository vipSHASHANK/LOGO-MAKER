import os
import logging
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
        # Open the image file
        user_image = Image.open(photo_path)
        user_image = user_image.convert("RGBA")  # Convert image to RGBA mode to support transparency

        max_width, max_height = user_image.size
        font, text_width, text_height = get_dynamic_font(user_image, text, max_width, max_height, font_path)

        # Adjust the text size
        text_width = int(text_width * size_multiplier)
        text_height = int(text_height * size_multiplier)

        # Calculate text position to center it
        x = (max_width - text_width) // 2 + x_offset
        y = (max_height - text_height) // 2 + y_offset
        text_position = (x, y)

        draw = ImageDraw.Draw(user_image)
        add_3d_text(draw, text_position, text, font, glow_color=glow_color, text_color="white", glow_strength=10)

        # Save the final image
        user_image.save(output_path, "PNG")
        return output_path
    except Exception as e:
        logger.error(f"Error adding text to image: {e}")
        return None

# Function to handle when a user sends a photo
@app.on_message(filters.photo & filters.private)
async def photo_handler(_, message: Message):
    if message.photo:
        # Save the user's photo locally
        photo_path = f"user_photos/{message.photo.file_id}.jpg"
        await message.download(photo_path)  # Download the photo to the specified path

        # Save user data (photo path, text, and settings)
        await save_user_data(message.from_user.id, {'photo_path': photo_path, 'text': '', 'text_position': (0, 0), 'size_multiplier': 1, 'glow_color': 'red'})

        await message.reply_text("Ab apna logo text bheje.")

# Function to save user data (you can update this as per your needs)
async def save_user_data(user_id, data):
    # Here, you would typically save the data to a database, but for simplicity, it's just logged
    logger.info(f"Saving data for user {user_id}: {data}")
    # You can save the data to a file or database as per your logic

# Handler for receiving logo text after photo
@app.on_message(filters.text & filters.private)
async def text_handler(_, message: Message):
    user_id = message.from_user.id
    user_data = await get_user_data(user_id)

    if not user_data:
        await message.reply_text("Pehle apna photo bheje.")
        return

    user_text = message.text.strip()

    if not user_text:
        await message.reply_text("Logo text dena hoga.")
        return

    # Save the text into the user's data
    user_data['text'] = user_text
    await save_user_data(user_id, user_data)

    # Send font selection buttons
    font_buttons = create_font_buttons()
    await message.reply_text(
        "Apna font choose karein:", 
        reply_markup=InlineKeyboardMarkup([font_buttons])
    )

# Start command handler
@app.on_message(filters.command("start") & filters.private)
async def start(_, message: Message):
    await message.reply_text("Welcome to Logo Creator Bot! Send a photo to get started.")

if __name__ == "__main__":
    app.run()
    
