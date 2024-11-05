import os
import logging
from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client, filters
from pyrogram.errors import Unauthorized
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery, InputMediaPhoto
from config import Config
from motor.motor_asyncio import AsyncIOMotorClient
from private_buttons import create_font_buttons, POSITION_SIZE_BUTTONS, GLOW_COLOR_BUTTONS  # Import buttons

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB Client Setup
mongo_client = AsyncIOMotorClient(Config.MONGO_URI)
db = mongo_client[Config.MONGO_DB_NAME]
users_collection = db["users"]  # MongoDB collection for user data

# Pyrogram Bot Setup
app = Client(
    "logo_creator_bot",
    bot_token=Config.BOT_TOKEN,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    workers=2  # Set number of workers to handle requests faster
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

# Function to get user data from MongoDB
async def get_user_data(user_id):
    user = await users_collection.find_one({"user_id": user_id})
    if user:
        return user
    else:
        return None

# Function to save/update user data in MongoDB
async def save_user_data(user_id, data):
    await users_collection.update_one(
        {"user_id": user_id},
        {"$set": data},
        upsert=True
    )

# Handler for when a user sends a photo
@app.on_message(filters.photo & filters.private)
async def photo_handler(_, message: Message):
    try:
        if message.photo:
            photo_path = f"user_photos/{message.photo.file_id}.jpg"
            await message.download(photo_path)

            # Save user data in MongoDB
            await save_user_data(message.from_user.id, {'photo_path': photo_path, 'text': '', 'text_position': (0, 0), 'size_multiplier': 1, 'glow_color': 'red'})

            await message.reply_text("Ab apna logo text bheje.")
    except Unauthorized as e:
        logger.error(f"Unauthorized error: {str(e)}. The bot token might have been revoked or the session expired.")
        await app.stop()
        await app.start()
        logger.info("Bot session restarted successfully.")
    except Exception as e:
        logger.error(f"Error in photo handler: {e}")
        await message.reply_text("An error occurred while processing your request.")

# Handler for receiving logo text after photo
@app.on_message(filters.text & filters.private)
async def text_handler(_, message: Message):
    try:
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
    except Unauthorized as e:
        logger.error(f"Unauthorized error: {str(e)}. The bot token might have been revoked or the session expired.")
        await app.stop()
        await app.start()
        logger.info("Bot session restarted successfully.")
    except Exception as e:
        logger.error(f"Error in text handler: {e}")
        await message.reply_text("An error occurred while processing your request.")

# Handler for font selection
@app.on_callback_query(filters.regex("^font_"))
async def font_button_handler(_, callback_query: CallbackQuery):
    try:
        user_id = callback_query.from_user.id
        user_data = await get_user_data(user_id)

        if not user_data:
            return

        selected_font_name = callback_query.data.split("_")[1]
        selected_font = next((font for font in FONT_OPTIONS if font['name'] == selected_font_name), None)

        if selected_font:
            user_data['selected_font'] = selected_font['path']
            font_path = selected_font['path']
            
            photo_path = user_data['photo_path']
            user_text = user_data['text']
            output_path = f"logos/updated_{user_text}_logo.png"
            
            result = await add_text_to_image(photo_path, user_text, output_path, font_path=font_path)

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
    except Unauthorized as e:
        logger.error(f"Unauthorized error: {str(e)}. The bot token might have been revoked or the session expired.")
        await app.stop()
        await app.start()
        logger.info("Bot session restarted successfully.")
    except Exception as e:
        logger.error(f"Error in font button handler: {e}")
        await callback_query.answer("An error occurred while processing your request.")

# Start command handler
@app.on_message(filters.command("start") & filters.private)
async def start(_, message: Message):
    await message.reply_text("Welcome to Logo Creator Bot! Send a photo to get started.")

# Start the bot
if __name__ == "__main__":
    app.run()
    
