import os
import logging
from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.storage import MemoryStorage  # सही से आयात करें
from config import Config
from private_buttons import create_font_buttons, create_position_buttons, create_size_buttons, create_color_buttons

# लॉगिंग सेटअप
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# इन-मेमोरी यूज़र डेटा स्टोर
user_data_store = {}

# बॉट सेटअप
storage = MemoryStorage("logo_creator_memory")  # यूनिक नाम के साथ स्टोरेज सेट करें

app = Client(
    "logo_creator_bot",  # यूनिक सत्र नाम
    bot_token=Config.BOT_TOKEN,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    storage=storage  # स्टोरेज को क्लाइंट में पास करें
)

# फ़ॉन्ट विकल्प (अपने फ़ॉन्ट्स का पथ)
FONT_OPTIONS = [
    {"name": "FIGHTBACK", "path": "fonts/FIGHTBACK.ttf"},
    {"name": "Arial", "path": "fonts/Lobster-Regular.ttf"},
    {"name": "Times New Roman", "path": "fonts/OpenSans-Regular.ttf"},
    {"name": "Courier", "path": "fonts/Pacifico-Regular.ttf"},
    {"name": "Verdana", "path": "fonts/Roboto-Regular.ttf"},
]

# फ़ॉन्ट साइज को गतिशील रूप से समायोजित करने का फ़ंक्शन
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

# 3D टेक्स्ट इफेक्ट जोड़ने का फ़ंक्शन
def add_3d_text(draw, position, text, font, glow_color, text_color, shadow_offset=(5, 5), glow_strength=5):
    x, y = position
    
    # शैडो
    shadow_x = x + shadow_offset[0]
    shadow_y = y + shadow_offset[1]
    draw.text((shadow_x, shadow_y), text, font=font, fill="black")

    # ग्लो प्रभाव
    for offset in range(1, glow_strength + 1):
        draw.text((x - offset, y - offset), text, font=font, fill=glow_color)
        draw.text((x + offset, y - offset), text, font=font, fill=glow_color)
        draw.text((x - offset, y + offset), text, font=font, fill=glow_color)
        draw.text((x + offset, y + offset), text, font=font, fill=glow_color)

    # मुख्य टेक्स्ट
    draw.text((x, y), text, font=font, fill=text_color)

# चित्र पर टेक्स्ट जोड़ने का फ़ंक्शन
async def add_text_to_image(photo_path, text, output_path, x_offset=0, y_offset=0, size_multiplier=1, glow_color="red", font_path=None):
    try:
        user_image = Image.open(photo_path)
        user_image = user_image.convert("RGBA")  # RGBA मोड में बदलें

        max_width, max_height = user_image.size
        font, text_width, text_height = get_dynamic_font(user_image, text, max_width, max_height, font_path)

        # टेक्स्ट आकार समायोजित करें
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
        logger.error(f"चित्र में टेक्स्ट जोड़ने में त्रुटि: {e}")
        return None

# फोटो हैंडलर
@app.on_message(filters.photo & filters.private)
async def photo_handler(_, message: Message):
    if message.photo:
        photo_path = f"user_photos/{message.photo.file_id}.jpg"
        await message.download(photo_path)

        await save_user_data(message.from_user.id, {'photo_path': photo_path, 'text': '', 'text_position': (0, 0), 'size_multiplier': 1, 'glow_color': 'red'})

        await message.reply_text("अब अपना लोगो टेक्स्ट भेजें।")

# यूज़र डेटा सेव करने का फ़ंक्शन
async def save_user_data(user_id, data):
    user_data_store[user_id] = data
    logger.info(f"यूज़र {user_id} का डेटा सेव किया गया: {data}")

# यूज़र डेटा प्राप्त करने का फ़ंक्शन
async def get_user_data(user_id):
    return user_data_store.get(user_id, None)

# टेक्स्ट हैंडलर
@app.on_message(filters.text & filters.private)
async def text_handler(_, message: Message):
    user_id = message.from_user.id
    user_data = await get_user_data(user_id)

    if not user_data:
        await message.reply_text("पहले अपना फोटो भेजें।")
        return

    user_text = message.text.strip()

    if not user_text:
        await message.reply_text("लोगो टेक्स्ट देना होगा।")
        return

    user_data['text'] = user_text
    await save_user_data(user_id, user_data)

    font_buttons = create_font_buttons()
    await message.reply_text(
        "अपना फ़ॉन्ट चुनें:", 
        reply_markup=InlineKeyboardMarkup([font_buttons])
    )

# फ़ॉन्ट चयन हैंडलर
@app.on_message(filters.regex("font_") & filters.private)
async def font_handler(_, message: Message):
    user_id = message.from_user.id
    user_data = await get_user_data(user_id)

    if not user_data:
        await message.reply_text("पहले अपना फोटो भेजें।")
        return

    font_choice = message.text.strip().split('_')[1]
    selected_font = next((font for font in FONT_OPTIONS if font['name'].lower() == font_choice.lower()), None)

    if selected_font:
        user_data['font'] = selected_font
        await save_user_data(user_id, user_data)

        await message.reply_text(f"आपने फ़ॉन्ट '{selected_font['name']}' को चुना है।")

        color_buttons = create_color_buttons()
        await message.reply_text("अपना लोगो टेक्स्ट का रंग बताएं:", reply_markup=InlineKeyboardMarkup(color_buttons))

# रंग चयन हैंडलर
@app.on_message(filters.regex("color_") & filters.private)
async def color_handler(_, message: Message):
    user_id = message.from_user.id
    user_data = await get_user_data(user_id)

    if not user_data:
        await message.reply_text("पहले अपना फोटो भेजें।")
        return

    user_color = message.text.strip().split('_')[1]
    user_data['glow_color'] = user_color
    await save_user_data(user_id, user_data)

    await message.reply_text(f"आपने रंग '{user_color}' को चुना है।")

    position_buttons = create_position_buttons()
    await message.reply_text("अपना लोगो स्थिति चुनें:", reply_markup=InlineKeyboardMarkup(position_buttons))

# स्थिति चयन हैंडलर
@app.on_message(filters.regex("position_") & filters.private)
async def position_handler(_, message: Message):
    user_id = message.from_user.id
    user_data = await get_user_data(user_id)

    if not user_data:
        await message.reply_text("पहले अपना फोटो भेजें।")
        return

    position = message.text.strip().split('_')[1]
    user_data['position'] = position
    await save_user_data(user_id, user_data)

    await message.reply_text(f"स्थिति '{position}' चुनी गई है।")

    size_buttons = create_size_buttons()
    await message.reply_text("अपना लोगो आकार चुनें:", reply_markup=InlineKeyboardMarkup(size_buttons))

# आकार चयन हैंडलर
@app.on_message(filters.regex("size_") & filters.private)
async def size_handler(_, message: Message):
    user_id = message.from_user.id
    user_data = await get_user_data(user_id)

    if not user_data:
        await message.reply_text("पहले अपना फोटो भेजें।")
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
        await message.reply_photo(added_text_image, caption="यह रहा आपका लोगो!")
    else:
        await message.reply_text("लोगो बनाते समय कुछ गलत हो गया।")

# स्टार्ट कमांड हैंडलर
@app.on_message(filters.command("start") & filters.private)
async def start(_, message: Message):
    await message.reply_text("Logo Creator Bot में आपका स्वागत है! शुरुआत करने के लिए एक फोटो भेजें।")

if __name__ == "__main__":
    app.run()
    
