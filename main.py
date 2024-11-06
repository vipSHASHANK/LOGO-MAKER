import os
from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from config import Config
from private_buttons import create_position_buttons, create_size_buttons, create_color_buttons

# User data store
user_data_store = {}

# Initialize the Pyrogram Client
session_name = "logo_creator_bot"
app = Client(
    session_name,
    bot_token=Config.BOT_TOKEN,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    workdir=os.getcwd()
)

# Adjust font size dynamically
def get_dynamic_font(image, text, max_width, max_height):
    draw = ImageDraw.Draw(image)
    font_size = 100
    while font_size > 10:
        font = ImageFont.truetype("fonts/FIGHTBACK.ttf", font_size)
        text_width, text_height = draw.textsize(text, font=font)
        if text_width <= max_width and text_height <= max_height:
            return font, text_width, text_height
        font_size -= 5
    return font, text_width, text_height

# Add text to image
async def add_text_to_image(photo_path, text, output_path, x_offset=0, y_offset=0, size_multiplier=1, glow_color="red"):
    try:
        user_image = Image.open(photo_path).convert("RGBA")
        max_width, max_height = user_image.size
        font, text_width, text_height = get_dynamic_font(user_image, text, max_width, max_height)
        text_width = int(text_width * size_multiplier)
        text_height = int(text_height * size_multiplier)
        x = (max_width - text_width) // 2 + x_offset
        y = (max_height - text_height) // 2 + y_offset
        draw = ImageDraw.Draw(user_image)
        draw.text((x, y), text, font=font, fill="white")
        user_image.save(output_path, "PNG")
        return output_path
    except Exception as e:
        print(f"Error adding text to image: {e}")
        return None

# Save user data
async def save_user_data(user_id, data):
    user_data_store[user_id] = data

# Get user data
async def get_user_data(user_id):
    return user_data_store.get(user_id, None)

@app.on_message(filters.command("start"))
async def start_command(_, message: Message) -> None:
    welcome_text = (
        "👋 Welcome to the Logo Creator Bot!\n\n"
        "With this bot, you can create a custom logo by sending a photo and adding text to it!\n"
    )
    await message.reply_text(welcome_text)

@app.on_message(filters.photo & filters.private)
async def photo_handler(_, message: Message) -> None:
    media = message
    try:
        local_path = await media.download()
        await save_user_data(message.from_user.id, {'photo_path': local_path, 'text': '', 'text_position': (0, 0), 'size_multiplier': 1, 'glow_color': 'red'})
        await message.reply_text("Please send the text you want for your logo.")
    except Exception as e:
        await message.reply_text("File processing failed.")

@app.on_message(filters.text & filters.private)
async def text_handler(_, message: Message) -> None:
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
    
    # After receiving the text, prompt the user to select font, position, size, and color
    position_buttons = create_position_buttons()
    size_buttons = create_size_buttons()
    color_buttons = create_color_buttons()
    
    await message.reply_text("Choose position, size, and color for the logo text:", 
                             reply_markup=InlineKeyboardMarkup([
                                 position_buttons,
                                 size_buttons,
                                 color_buttons
                             ]))

@app.on_message(filters.CallbackQuery)
async def button_handler(_, callback_query):
    user_id = callback_query.from_user.id
    user_data = await get_user_data(user_id)
    if not user_data:
        return await callback_query.answer("Please start over by sending a photo.")
    
    # Handle position, size, and color adjustments here
    if callback_query.data.startswith("position_"):
        position = callback_query.data.split("_")[1]
        # Update position logic
        user_data['text_position'] = position
    elif callback_query.data.startswith("size_"):
        size = callback_query.data.split("_")[1]
        # Update size logic
        user_data['size_multiplier'] = float(size)
    elif callback_query.data.startswith("color_"):
        color = callback_query.data.split("_")[1]
        # Update color logic
        user_data['glow_color'] = color

    await save_user_data(user_id, user_data)

    # Regenerate the logo with updated settings
    photo_path = user_data['photo_path']
    text = user_data['text']
    output_path = "output_logo.png"
    await add_text_to_image(photo_path, text, output_path, user_data['text_position'], user_data['size_multiplier'], user_data['glow_color'])
    
    # Send the modified image to the user
    await callback_query.message.reply_photo(photo=output_path, caption="Here's your logo!")

if __name__ == "__main__":
    app.run()
    
