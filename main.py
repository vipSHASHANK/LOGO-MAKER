import os
import logging
import cv2
import numpy as np
from pyrogram import Client, filters
from pyrogram.types import Message
from PIL import Image, ImageEnhance, ImageFilter
from config import Config  # सुनिश्चित करें कि आपके पास यह कॉन्फ़िग फ़ाइल है
from pyrogram.errors import SessionRevoked

# लॉगिंग सेटअप करें
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# बोट के लिए नया क्लाइंट बनाने का तरीका
def create_client(session_name):
    return Client(
        session_name,
        bot_token=Config.BOT_TOKEN,
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
    )

# इमेज की शार्पनेस चेक करने के लिए फ़ंक्शन
def is_image_sharp(image_path):
    """ इमेज की शार्पनेस चेक करें। """
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray_image, cv2.CV_64F).var()
    
    # यदि शार्पनेस कम हो तो इमेज खराब है (ज्यादा वैरिएंस मतलब शार्प इमेज)
    if laplacian_var < 100:
        return False  # इमेज बहुत धुंधली है
    return True

# इमेज को सुधारने के लिए फ़ंक्शन
def enhance_image(input_image_path, output_image_path):
    try:
        # पिलो (Pillow) का उपयोग करके इमेज खोलें
        img = Image.open(input_image_path)

        # 1. कंट्रास्ट सुधारें (हल्का कंट्रास्ट)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)  # कंट्रास्ट हल्का बढ़ाएं

        # 2. ब्राइटनेस सुधारें (हल्की ब्राइटनेस)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.1)  # ब्राइटनेस हल्का बढ़ाएं

        # 3. शार्पनेस सुधारें (हल्की शार्पनेस)
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.7)  # शार्पनेस बढ़ाएं, लेकिन ज्यादा नहीं

        # 4. कलर सैचुरेशन बढ़ाएं (हल्का सैचुरेशन)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.4)  # कलर सैचुरेशन हल्का बढ़ाएं

        # इमेज को सेव करें
        img.save(output_image_path)

        # OpenCV का उपयोग करके इमेज को और सुधारें
        return apply_opencv_enhancements(output_image_path)
    
    except Exception as e:
        logger.error(f"इमेज सुधारते वक्त एरर: {str(e)}")
        return None

def apply_opencv_enhancements(image_path):
    """OpenCV का उपयोग करके डीनॉइज़िंग, कांट्रास्ट स्ट्रेचिंग, और एज शार्पनिंग।"""
    # OpenCV का उपयोग करके इमेज को पढ़ें
    image = cv2.imread(image_path)

    # 1. डीनॉइज़िंग (शोर को कम करना)
    denoised_image = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)

    # 2. कांट्रास्ट स्ट्रेचिंग (कांट्रास्ट को ऑटो एडजस्ट करना)
    lab = cv2.cvtColor(denoised_image, cv2.COLOR_BGR2Lab)
    l, a, b = cv2.split(lab)
    l = cv2.equalizeHist(l)  # L चैनल (ल्यूमिनेंस) पर हिस्टोग्राम बराबर करें
    lab = cv2.merge((l, a, b))
    contrast_stretched_image = cv2.cvtColor(lab, cv2.COLOR_Lab2BGR)

    # 3. एज शार्पनिंग (एक कर्नल का उपयोग करना)
    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])  # शार्पनिंग कर्नल
    sharpened_image = cv2.filter2D(contrast_stretched_image, -1, kernel)

    # अंतिम इमेज को सेव करें
    enhanced_image_path = "enhanced_" + os.path.basename(image_path)
    cv2.imwrite(enhanced_image_path, sharpened_image)

    return enhanced_image_path

# अब बोट को चलाने के लिए क्लाइंट को डिफाइन करें
app = create_client("photo_enhancer_session")

@app.on_message(filters.command("start"))
async def start_command(_, message: Message) -> None:
    """यूज़र को वेलकम करें और निर्देश दें।"""
    welcome_text = (
        "👋 Welcome to the Image Enhancer Bot!\n\n"
        "Send me a photo, and I'll enhance it using AI!"
    )

    await message.reply_text(welcome_text, disable_web_page_preview=True)

@app.on_message(filters.photo & filters.incoming & filters.private)
async def photo_handler(_, message: Message) -> None:
    """आने वाली फोटो को हैंडल करें, उसे सुधारें और वापस भेजें।"""
    media = message
    file_size = media.photo.file_size if media.photo else 0

    # चेक करें कि इमेज बहुत बड़ी तो नहीं है (मैक्स 200MB)
    if file_size > 200 * 1024 * 1024:
        return await message.reply_text("Please provide a photo under 200MB.")

    try:
        # फोटो प्रोसेस होने का संदेश भेजें
        text = await message.reply("Processing...")

        # इमेज को डाउनलोड करें
        local_path = await media.download()

        # चेक करें कि इमेज शार्प है या नहीं
        if not is_image_sharp(local_path):
            await text.edit_text("This image seems blurry or of low quality. Please send a better one.")
            os.remove(local_path)
            return

        # सुधारित इमेज का पथ सेट करें
        enhanced_image_path = "enhanced_" + os.path.basename(local_path)

        # इमेज को सुधारें
        enhanced_image = enhance_image(local_path, enhanced_image_path)

        if enhanced_image:
            await text.edit_text("Sending enhanced image...")
            # सुधारित इमेज को यूज़र को भेजें
            await message.reply_photo(enhanced_image)
        else:
            await text.edit_text("Error enhancing the image. Please try again later.")

        # प्रोसेसिंग के बाद ओरिजिनल और सुधारित इमेज को हटा दें
        os.remove(local_path)
        os.remove(enhanced_image_path)

    except Exception as e:
        logger.error(f"फोटो हैंडलर में एरर: {str(e)}")
        await text.edit_text("कुछ गड़बड़ हो गया। कृपया फिर से प्रयास करें।")
        if os.path.exists(local_path):
            os.remove(local_path)  # अगर डाउनलोड में समस्या हो तो इमेज हटा दें

if __name__ == "__main__":
    try:
        # बोट को चलाने के लिए नया क्लाइंट बनाएं और उसे रन करें
        app.run()
    except SessionRevoked:
        logger.error("सत्र रद्द कर दिया गया है। कृपया बोट को फिर से शुरू करें।")
    except Exception as e:
        logger.error(f"कुछ गड़बड़ हो गई: {e}")
