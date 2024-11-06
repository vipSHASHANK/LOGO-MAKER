import os
import logging
import tempfile
from PIL import Image, ImageDraw, ImageFont, ImageColor, ImageFilter
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery, InputMediaPhoto
from config import Config
from buttons import get_adjustment_keyboard  # Importing the function from button.py

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

# Apply Blur Effect to the Background Image Only (no blur on text)
async def apply_blur(photo_path, blur_intensity):
    try:
        image = Image.open(photo_path).convert("RGBA")
        
        # Create a blurred version of the background
        blurred_image = image.filter(ImageFilter.GaussianBlur(radius=blur_intensity))

        # Save the blurred image temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            blurred_image.save(temp_file, "PNG")
            return temp_file.name
    except Exception as e:
        logger.error(f"Error applying blur: {e}")
        return None

# Add text to image with adjustments and color (This ensures text is on top of the image, no blur)
async def add_text_to_image(photo_path, text, output_path, font_path, text_position, size_multiplier, text_color):
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

        # Outline effect in white (shadow effect)
        outline_width = 3
        for dx in [-outline_width, outline_width]:
            for dy in [-outline_width, outline_width]:
                draw.text((x + dx, y + dy), text, font=font, fill="white")

        # Apply main text color
        draw.text((x, y), text, font=font, fill=text_color)

        # Save the image with text (this should be added after blur is applied to keep text sharp)
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
        text = await message.reply("❖ ᴘʀᴏᴄᴇssɪɴɢ...")
        local_path = await media.download()
        await text.edit_text("❖ ᴘʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ʟᴏɢᴏ...")
        await save_user_data(message.from_user.id, {'photo_path': local_path, 'text': '', 'text_position': (0, 0), 'size_multiplier': 1, 'text_color': 'red', 'font': 'fonts/Deadly Advance.ttf', 'blur_intensity': 0})
        await message.reply_text("✎ ɴᴏᴡ sᴇɴᴅ ᴍᴇ ʏᴏᴜʀ ʟᴏɢᴏ ᴛᴇxᴛ.")
    except Exception as e:
        logger.error(e)
        await text.edit_text("❖ ғɪʟᴇ ᴘʀᴏᴄᴇssɪɴɢ ғᴀɪʟᴇᴅ.")

@app.on_message(filters.text & filters.private)
async def text_handler(_, message: Message) -> None:
    user_id = message.from_user.id
    user_data = await get_user_data(user_id)

    if not user_data:
        await message.reply_text("❖ ғɪʀsᴛ sᴇɴᴅ ᴍᴇ ᴀ ᴘʜᴏᴛᴏ ғᴏʀ ʟᴏɢᴏ ʙᴀᴄᴋɢʀᴏɴᴜɴᴅ.")
        return
    
    if user_data['text']:
        await message.reply_text("❖ ʏᴏᴜ ʜᴀᴠᴇ ᴀʟʀᴇᴀᴅʏ ᴇɴᴛᴇʀᴇᴅ ᴛᴇxᴛ!")
        return
    
    user_text = message.text.strip()
    if not user_text:
        await message.reply_text("❖ ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴛᴇxᴛ.")
        return
    
    user_data['text'] = user_text
    font_path = user_data.get("font", "fonts/Deadly Advance.ttf")
    text_color = ImageColor.getrgb(user_data['text_color'])
    
    # Apply blur if needed
    output_path = user_data['photo_path']
    if user_data['blur_intensity'] > 0:
        blurred_image_path = await apply_blur(user_data['photo_path'], user_data['blur_intensity'])
        if blurred_image_path:
            output_path = blurred_image_path

    # Now add text to the blurred image (if blurred) or original image
    output_path = await add_text_to_image(output_path, user_text, None, font_path, user_data['text_position'], user_data['size_multiplier'], text_color)

    await message.reply_photo(output_path, caption="❖ ʏᴏᴜʀ ʟᴏɢᴏ ᴄʜᴀɴɪɴɢ....!", reply_markup=get_adjustment_keyboard(output_path))
    await message.delete()

@app.on_callback_query()
async def callback_handler(_, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user_data = await get_user_data(user_id)

    if not user_data or not user_data.get("photo_path"):
        await callback_query.answer("Please upload a photo first.", show_alert=True)
        return

    # Handle text adjustments
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
    elif callback_query.data == "color_red":
        user_data['text_color'] = "red"
    elif callback_query.data == "color_blue":
        user_data['text_color'] = "blue"
    elif callback_query.data == "color_green":
        user_data['text_color'] = "green"
    elif callback_query.data == "color_black":
        user_data['text_color'] = "black"
    elif callback_query.data == "color_yellow":
        user_data['text_color'] = "yellow"
    elif callback_query.data == "color_orange":
        user_data['text_color'] = "orange"
    elif callback_query.data == "color_purple":
        user_data['text_color'] = "purple"

# Font selection logic
    if callback_query.data == "font_deadly_advance_italic":
        user_data['font'] = "fonts/UTTAM1.ttf"
    elif callback_query.data == "font_deadly_advance":
        user_data['font'] = "fonts/Deadly Advance.ttf"
    elif callback_query.data == "font_trick_or_treats":
        user_data['font'] = "fonts/Trick or Treats.ttf"
    elif callback_query.data == "font_vampire_wars_italic":
        user_data['font'] = "fonts/Vampire Wars Italic.ttf"
    elif callback_query.data == "font_lobster":
        user_data['font'] = "fonts/FIGHTBACK.ttf"

    # Adjust blur intensity
    if callback_query.data == "blur_plus":
        user_data['blur_intensity'] = min(user_data['blur_intensity'] + 1, 10)  # Max blur intensity of 10
    elif callback_query.data == "blur_minus":
        user_data['blur_intensity'] = max(user_data['blur_intensity'] - 1, 0)  # Min blur intensity of 0

    await save_user_data(user_id, user_data)

    # Regenerate the logo with the new adjustments
    font_path = user_data.get("font", "fonts/Deadly Advance.ttf")
    text_color = ImageColor.getrgb(user_data['text_color'])
    
    output_path = user_data['photo_path']
    if user_data['blur_intensity'] > 0:
        blurred_image_path = await apply_blur(user_data['photo_path'], user_data['blur_intensity'])
        if blurred_image_path:
            output_path = blurred_image_path

    # Now add text to the blurred image (if blurred) or original image
    output_path = await add_text_to_image(output_path, user_data['text'], None, font_path, user_data['text_position'], user_data['size_multiplier'], text_color)

    await callback_query.message.edit_media(InputMediaPhoto(output_path), reply_markup=get_adjustment_keyboard(output_path))
    await callback_query.answer()

    # Handle the download button callback
    if callback_query.data == "download_logo":
        await callback_query.answer("Downloading your logo...")
        with open(output_path, "rb") as file:
            await callback_query.message.reply_document(file, caption="Your logo is ready for download.")
        await callback_query.message.edit_reply_markup(reply_markup=None)
    
if __name__ == "__main__":
    app.run()
        
