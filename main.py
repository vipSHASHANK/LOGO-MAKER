import os
import logging
import tempfile
from PIL import Image, ImageDraw, ImageFont, ImageColor, ImageFilter
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery, InputMediaPhoto
from config import Config

# लॉगिंग सेटअप
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# यूजर डेटा स्टोर
user_data_store = {}

# फॉन्ट साइज़ को डायनेमिकली एडजस्ट करने का फंक्शन
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

# इमेज एडजस्टमेंट के लिए कीबोर्ड बनाने का फंक्शन
def get_adjustment_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Left", callback_data="move_left"),
         InlineKeyboardButton("➡️ Right", callback_data="move_right")],
        [InlineKeyboardButton("⬆️ Up", callback_data="move_up"),
         InlineKeyboardButton("⬇️ Down", callback_data="move_down")],
        [InlineKeyboardButton("🔍 Increase", callback_data="increase_size"),
         InlineKeyboardButton("🔎 Decrease", callback_data="decrease_size")],
        
        # रंग चयन बटन
        [InlineKeyboardButton("🔴 Red", callback_data="color_red"),
         InlineKeyboardButton("🔵 Blue", callback_data="color_blue"),
         InlineKeyboardButton("🟢 Green", callback_data="color_green"),
         InlineKeyboardButton("⚫ Black", callback_data="color_black"),
         InlineKeyboardButton("🟡 Yellow", callback_data="color_yellow"),
         InlineKeyboardButton("🟠 Orange", callback_data="color_orange"),
         InlineKeyboardButton("🟣 Purple", callback_data="color_purple")],
        
        # फॉन्ट चयन बटन
        [InlineKeyboardButton("Deadly Advance Italic", callback_data="font_deadly_advance_italic"),
         InlineKeyboardButton("Deadly Advance", callback_data="font_deadly_advance"),
         InlineKeyboardButton("Trick or Treats", callback_data="font_trick_or_treats"),
         InlineKeyboardButton("Vampire Wars Italic", callback_data="font_vampire_wars_italic"),
         InlineKeyboardButton("Lobster", callback_data="font_lobster")],
        
        # ब्लर बटन
        [InlineKeyboardButton("Blur+", callback_data="blur_plus"),
         InlineKeyboardButton("Blur-", callback_data="blur_minus")]
    ])

# इमेज पर टेक्स्ट जोड़ने का फंक्शन
async def add_text_to_image(photo_path, text, output_path, font_path, text_position, size_multiplier, text_color):
    try:
        user_image = Image.open(photo_path).convert("RGBA")
        max_width, max_height = user_image.size

        # फॉन्ट साइज़ को साइज मल्टीप्लायर के आधार पर एडजस्ट करें
        font = get_dynamic_font(user_image, text, max_width, max_height, font_path)
        font = ImageFont.truetype(font_path, int(font.size * size_multiplier))
        
        draw = ImageDraw.Draw(user_image)
        text_width, text_height = draw.textsize(text, font=font)
        
        # टेक्स्ट की पोजीशन को लागू करें
        x = text_position[0]
        y = text_position[1]

        # टेक्स्ट का आउटलाइन (शैडो इफेक्ट)
        outline_width = 3
        for dx in [-outline_width, outline_width]:
            for dy in [-outline_width, outline_width]:
                draw.text((x + dx, y + dy), text, font=font, fill="white")

        # टेक्स्ट का मुख्य रंग
        draw.text((x, y), text, font=font, fill=text_color)

        # इमेज को टेम्परेरी फाइल में सेव करें
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            output_path = temp_file.name
            user_image.save(output_path, "PNG")
        
        return output_path, text_width, text_height
    except Exception as e:
        logger.error(f"Error adding text to image: {e}")
        return None, 0, 0

# बैकग्राउंड इमेज पर ब्लर इफेक्ट लागू करने का फंक्शन (टेक्स्ट पर नहीं)
async def apply_blur(photo_path, blur_intensity, text_position, text_size):
    try:
        image = Image.open(photo_path).convert("RGBA")
        image_copy = image.copy()

        # मास्क बनाएं जिसमें टेक्स्ट का क्षेत्र न दिखाई दे
        mask = Image.new("L", image.size, 255)
        draw = ImageDraw.Draw(mask)

        # टेक्स्ट के क्षेत्र को मास्क पर ड्रा करें ताकि ब्लर उस क्षेत्र को न छुए
        text_width, text_height = text_size
        x, y = text_position

        # टेक्स्ट का क्षेत्र मास्क पर (0 से मतलब है कि यहां ब्लर नहीं होगा)
        draw.rectangle([x, y, x + text_width, y + text_height], fill=0)  # 0 = कोई ब्लर नहीं

        # इमेज पर गॉसियन ब्लर लागू करें
        blurred_image = image_copy.filter(ImageFilter.GaussianBlur(radius=blur_intensity))
        
        # मूल इमेज (टेक्स्ट वाला हिस्सा) को ब्लर्ड इमेज पर चिपकाएं
        image_copy.paste(image, (0, 0), mask)

        # मास्क का उपयोग करते हुए ब्लर और ओरिजिनल इमेज को मर्ज करें
        result_image = Image.composite(blurred_image, image_copy, mask)

        # अंतिम इमेज को सेव करें
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            output_path = temp_file.name
            result_image.save(output_path, "PNG")
        
        return output_path
    except Exception as e:
        logger.error(f"Error applying blur: {e}")
        return None

# यूजर डेटा को सेव करने का फंक्शन
async def save_user_data(user_id, data):
    user_data_store[user_id] = data
    logger.info(f"User {user_id} data saved: {data}")

# यूजर डेटा प्राप्त करने का फंक्शन
async def get_user_data(user_id):
    return user_data_store.get(user_id, None)

# बोट की शुरुआत
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
        "👋 स्वागत है आपके लोगो क्रिएटर बोट में!\n\n"
        "इस बोट के द्वारा आप एक कस्टम लोगो बना सकते हैं, बस फोटो भेजें और टेक्स्ट जोड़ें!\n"
    )
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Join 👋", url="https://t.me/BABY09_WORLD")]])
    await message.reply_text(welcome_text, reply_markup=keyboard, disable_web_page_preview=True)

@app.on_message(filters.photo & filters.private)
async def photo_handler(_, message: Message) -> None:
    media = message
    file_size = media.photo.file_size if media.photo else 0
    if file_size > 200 * 1024 * 1024:
        return await message.reply_text("कृपया 200MB से कम आकार की फोटो भेजें।")
    try:
        text = await message.reply("प्रोसेसिंग...")
        local_path = await media.download()
        await text.edit_text("आपके लोगो को प्रोसेस किया जा रहा है...")
        await save_user_data(message.from_user.id, {'photo_path': local_path, 'text': '', 'text_position': (0, 0), 'size_multiplier': 1, 'text_color': 'red', 'font': 'fonts/Deadly Advance.ttf', 'blur_intensity': 0})
        await message.reply_text("कृपया अपना लोगो टेक्स्ट भेजें।")
    except Exception as e:
        logger.error(e)
        await text.edit_text("फाइल प्रोसेसिंग में त्रुटि हुई।")

@app.on_message(filters.text & filters.private)
async def text_handler(_, message: Message) -> None:
    user_id = message.from_user.id
    user_data = await get_user_data(user_id)

    if not user_data:
        await message.reply_text("कृपया पहले एक फोटो भेजें।")
        return
    
    if user_data['text']:
        await message.reply_text("आप पहले ही लोगो के लिए टेक्स्ट भेज चुके हैं। पोजीशन एडजस्ट करने के लिए कीबोर्ड का उपयोग करें।")
        return
    
    text = message.text
    user_data['text'] = text
    await save_user_data(user_id, user_data)
    
    # टेक्स्ट और फोटो को जोड़ने और फॉन्ट पोजीशन तय करने के बाद अंतिम लोगो बनाना
    font_path = user_data.get("font", "fonts/Deadly Advance.ttf")
    output_path, text_width, text_height = await add_text_to_image(user_data['photo_path'], user_data['text'], None, font_path, user_data['text_position'], user_data['size_multiplier'], ImageColor.getrgb(user_data['text_color']))

    # ब्लर अप्लाई करने के बाद आउटपुट भेजना
    output_path = await apply_blur(output_path, user_data['blur_intensity'], user_data['text_position'], (text_width, text_height))
    
    if output_path:
        await message.reply_photo(photo=output_path, caption="यह रहा आपका लोगो!")
    else:
        await message.reply_text("लोगो बनाते समय समस्या हुई। कृपया फिर से प्रयास करें।")

# कॉलबैक हैंडलर (कीबोर्ड बटन के लिए)
@app.on_callback_query()
async def callback_handler(_, callback_query: CallbackQuery) -> None:
    user_id = callback_query.from_user.id
    user_data = await get_user_data(user_id)
    
    if callback_query.data in ["blur_plus", "blur_minus"]:
        blur_intensity_change = 1 if callback_query.data == "blur_plus" else -1
        user_data['blur_intensity'] = max(min(user_data['blur_intensity'] + blur_intensity_change, 10), 0)
        await save_user_data(user_id, user_data)

        font_path = user_data.get("font", "fonts/Deadly Advance.ttf")
        output_path, text_width, text_height = await add_text_to_image(user_data['photo_path'], user_data['text'], None, font_path, user_data['text_position'], user_data['size_multiplier'], ImageColor.getrgb(user_data['text_color']))
        
        if output_path is None:
            await callback_query.message.reply_text("लोगो बनाने में समस्या आई।")
            return
        
        # ब्लर को बैकग्राउंड इमेज पर लागू करना
        output_path = await apply_blur(output_path, user_data['blur_intensity'], user_data['text_position'], (text_width, text_height))

        # नए लोगो के साथ कीबोर्ड अपडेट करें
        await callback_query.message.edit_media(InputMediaPhoto(media=output_path, caption="यह रहा आपका लोगो!"), reply_markup=get_adjustment_keyboard())
    await callback_query.answer()

if __name__ == "__main__":
    app.run()
        
