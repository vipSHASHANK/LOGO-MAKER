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

# Pyrogram Bot Setup
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

# Initialize bot
@app.on_message(filters.command("start"))
async def start_command(_, message: Message) -> None:
    """Welcomes the user with instructions."""
    welcome_text = (
        "👋 Welcome to the Logo Creator Bot!\n\n"
        "With this bot, you can create custom logos by sending a photo and adding text to it.\n"
        "Send a photo to get started."
    )

    keyboard = [
        [InlineKeyboardButton("Join 👋", url="https://t.me/Your_Channel_Link")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await message.reply_text(welcome_text, reply_markup=reply_markup, disable_web_page_preview=True)

# Handler for receiving photo
@app.on_message(filters.photo & filters.private)
async def photo_handler(_, message: Message) -> None:
    """Handles incoming photo messages by saving it for logo creation."""
    if message.photo:
        photo_path = f"user_photos/{message.photo.file_id}.jpg"
        await message.download(photo_path)

        # Save initial user data in memory or a database (if necessary)
        # Just saving the photo path in this case for simplicity
        user_data = {"photo_path": photo_path, "text": "", "text_position": (0, 0), "size_multiplier": 1, "glow_color": "red"}
        
        await message.reply_text("Now send the text you want on the logo.")

# Handler for receiving logo text after photo
@app.on_message(filters.text & filters.private)
async def text_handler(_, message: Message) -> None:
    """Handles text input for the logo."""
    user_text = message.text.strip()

    if not user_text:
        await message.reply_text("Please send the text you want to add to the logo.")
        return

    user_data = {"text": user_text}

    # Send font selection buttons from private_buttons
    font_buttons = create_font_buttons()

    await message.reply_text(
        "Choose your font:", 
        reply_markup=InlineKeyboardMarkup(font_buttons)
    )

# Handler for font selection
@app.on_callback_query(filters.regex("^font_"))
async def font_button_handler(_, callback_query: CallbackQuery):
    """Handles the selection of font for the logo."""
    selected_font_name = callback_query.data.split("_")[1]
    selected_font = next((font for font in FONT_OPTIONS if font['name'] == selected_font_name), None)

    if selected_font:
        user_data = {"selected_font": selected_font['path']}

        # Generate logo with selected font
        photo_path = user_data["photo_path"]
        user_text = user_data["text"]
        output_path = f"logos/{user_text}_logo.png"
        
        result = await add_text_to_image(photo_path, user_text, output_path, font_path=selected_font['path'])

        if result:
            media = InputMediaPhoto(media=output_path, caption="")
            await callback_query.message.edit_media(media=media)
            await callback_query.answer(f"Font changed to {selected_font_name}")

            # Send position, size, and glow color adjustment buttons
            await callback_query.message.edit_text(
                "Now, adjust the position, size, and glow color for your logo.",
                reply_markup=InlineKeyboardMarkup([
                    *POSITION_SIZE_BUTTONS,
                    *GLOW_COLOR_BUTTONS
                ])
            )

# Handler for position adjustments, size changes, and glow color changes
@app.on_callback_query(filters.regex("^(left|right|up|down|smaller|bigger|glow_[a-z]+)$"))
async def button_handler(_, callback_query: CallbackQuery):
    """Handles position, size, and glow adjustments."""
    user_data = {"text_position": (0, 0), "size_multiplier": 1, "glow_color": "red"}
    action = callback_query.data
    x_offset, y_offset = user_data['text_position']
    size_multiplier = user_data['size_multiplier']
    text = user_data['text']
    glow_color = user_data['glow_color']
    font_path = user_data['selected_font']

    # Adjust position, size, and glow color based on action
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
    user_data['text_position'] = (x_offset, y_offset)
    user_data['size_multiplier'] = size_multiplier
    user_data['glow_color'] = glow_color

    # Regenerate the logo with new adjustments
    output_path = await add_text_to_image(user_data['photo_path'], text, f"logos/{text}_logo.png", x_offset, y_offset, size_multiplier, glow_color, font_path)

    if output_path:
        media = InputMediaPhoto(media=output_path, caption="Here is your updated logo!")
        await callback_query.message.edit_media(media=media)
        await callback_query.answer(f"Logo updated with {action}.")

# Start the bot
if __name__ == "__main__":
    app.run()
    
