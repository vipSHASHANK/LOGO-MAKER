import os
import logging
from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery, InputMediaPhoto
from config import Config  # Ensure you have this file for your bot's config
from private_buttons import create_font_buttons, POSITION_SIZE_BUTTONS, GLOW_COLOR_BUTTONS  # Import buttons

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Client(
    "logo_creator_bot",
    bot_token=Config.BOT_TOKEN,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
)

# Font options (fonts stored here)
FONT_OPTIONS = [
    {"name": "FIGHTBACK", "path": "fonts/FIGHTBACK.ttf"},
    {"name": "Arial", "path": "fonts/Lobster-Regular.ttf"},
    {"name": "Times New Roman", "path": "fonts/OpenSans-Regular.ttf"},
    {"name": "Courier", "path": "fonts/Pacifico-Regular.ttf"},
    {"name": "Verdana", "path": "fonts/Roboto-Regular.ttf"},
]

user_data = {}

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

# Function to add 3D text effect with shadow and glow
def add_3d_text(draw, position, text, font, glow_color, text_color, shadow_offset=(5, 5), glow_strength=5):
    """
    Adds a 3D text effect by creating a shadow and the main text.
    The main text is drawn on top of the shadow with a glowing effect.
    """
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
def add_text_to_image(photo_path, text, output_path, x_offset=0, y_offset=0, size_multiplier=1, glow_color="red", font_path=None):
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

# Handler for when a user sends a photo
@app.on_message(filters.photo & filters.private)
async def photo_handler(_, message: Message):
    if message.photo:
        photo_path = f"user_photos/{message.photo.file_id}.jpg"
        await message.download(photo_path)

        await message.reply_text("Ab apna logo text bheje.")
        user_data[message.from_user.id] = {'photo_path': photo_path, 'text': ''}

# Handler for receiving logo text after photo
@app.on_message(filters.text & filters.private)
async def text_handler(_, message: Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        await message.reply_text("Pehle apna photo bheje.")
        return

    user_text = message.text.strip()

    if not user_text:
        await message.reply_text("Logo text dena hoga.")
        return

    user_data[user_id]['text'] = user_text

    # Send font selection buttons
    font_buttons = create_font_buttons()
    await message.reply_text(
        "Apna font choose karein:", 
        reply_markup=InlineKeyboardMarkup([font_buttons])
    )

    # Initialize default values for position, size, and glow color
    user_data[user_id]['text_position'] = (0, 0)
    user_data[user_id]['size_multiplier'] = 1
    user_data[user_id]['glow_color'] = "red"

# Handler for font selection
@app.on_callback_query(filters.regex("^font_"))
async def font_button_handler(_, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id not in user_data:
        return

    selected_font_name = callback_query.data.split("_")[1]
    selected_font = next((font for font in FONT_OPTIONS if font['name'] == selected_font_name), None)
    
    if selected_font:
        user_data[user_id]['selected_font'] = selected_font['path']
        font_path = selected_font['path']
        
        photo_path = user_data[user_id]['photo_path']
        user_text = user_data[user_id]['text']
        output_path = f"logos/updated_{user_text}_logo.png"
        
        result = add_text_to_image(photo_path, user_text, output_path, font_path=font_path)

        if result:
            await callback_query.message.edit_text(
                "Font selected! Ab apni logo ka position, size aur glow color change karein.",
                reply_markup=InlineKeyboardMarkup([
                    *POSITION_SIZE_BUTTONS,
                    *GLOW_COLOR_BUTTONS
                ])
            )
            media = InputMediaPhoto(media=output_path, caption="")
            await callback_query.message.edit_media(media=media)
            await callback_query.answer(f"Font changed to {selected_font_name}")

# Handler for position adjustments, size changes, and glow color changes
@app.on_callback_query(filters.regex("^(left|right|up|down|smaller|bigger|glow_[a-z]+)$"))
async def button_handler(_, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id not in user_data:
        return

    action = callback_query.data
    user_info = user_data[user_id]
    
    x_offset, y_offset = user_info['text_position']
    size_multiplier = user_info['size_multiplier']
    text = user_info['text']  # Get the logo text
    glow_color = user_info['glow_color']  # Get the selected glow color
    font_path = user_info['selected_font']

    if action == "left":
        x_offset -= 10
    elif action == "right":
        x_offset += 10
    elif action == "up":
        y_offset -= 10
    elif action == "down":
        y_offset += 10
    elif action == "smaller":
        size_multiplier = max(0.5, size_multiplier - 0.1)
    elif action == "bigger":
        size_multiplier = min(2, size_multiplier + 0.1)
    elif action == "glow_red":
        glow_color = "red"
    elif action == "glow_green":
        glow_color = "green"
    elif action == "glow_blue":
        glow_color = "blue"

    # Update user data with new position, size, and glow color
    user_info['text_position'] = (x_offset, y_offset)
    user_info['size_multiplier'] = size_multiplier
    user_info['glow_color'] = glow_color

    # Get the photo path and regenerate the logo with new adjustments
    photo_path = user_info['photo_path']
    output_path = f"logos/updated_{text}_logo.png"

    result = add_text_to_image(photo_path, text, output_path, x_offset, y_offset, size_multiplier, glow_color, font_path)

    if result:
        media = InputMediaPhoto(media=output_path, caption="")
        await callback_query.message.edit_media(media=media)
        await callback_query.answer(f"Logo updated with {action}")

# Start command handler
@app.on_message(filters.command("start") & filters.private)
async def start(_, message: Message):
    await message.reply_text("Welcome to Logo Creator Bot! Send a photo to get started.")

if __name__ == "__main__":
    app.run()
        
