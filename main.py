import os
import logging
import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from config import Config  # Ensure you have this file for your bot's config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Client(
    "catbox_uploader",
    bot_token=Config.BOT_TOKEN,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
)

def upload_file(file_path):
    url = "https://catbox.moe/user/api.php"
    data = {"reqtype": "fileupload", "json": "true"}
    
    try:
        with open(file_path, "rb") as file:
            files = {"fileToUpload": file}
            response = requests.post(url, data=data, files=files)
        
        logger.info("Response from Catbox: %s", response.text)

        if response.status_code == 200:
            try:
                response_json = response.json()
                return True, response_json.get("url", "")
            except ValueError:
                return True, response.text.strip()
        else:
            return False, f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"Exception occurred: {str(e)}"

@app.on_message(filters.command("start"))
async def start_command(_, message: Message) -> None:
    """Welcomes the user with instructions."""
    welcome_text = (
        "👋 Welcome to the Media Uploader Bot!\n\n"
        "With this bot, you can:\n"
        " • Upload photos: Just send a photo, and I'll upload it to Telegraph!\n"
        " • Get a quick link: Receive a link immediately after uploading.\n"
    )

    keyboard = [
        [InlineKeyboardButton("Join 👋", url="https://t.me/BABY09_WORLD")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await message.reply_text(welcome_text, reply_markup=reply_markup, disable_web_page_preview=True)

@app.on_message(filters.photo & filters.incoming & filters.private)
async def photo_handler(_, message: Message) -> None:
    """Handles incoming photo messages by uploading to Catbox.moe."""
    media = message
    file_size = media.photo.file_size if media.photo else 0

    if file_size > 200 * 1024 * 1024:
        return await message.reply_text("Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴘʜᴏᴛᴏ ᴜɴᴅᴇʀ 200MB.")

    try:
        text = await message.reply("Processing...")

        local_path = await media.download()
        await text.edit_text("Uploading 100%...")

        success, upload_url = upload_file(local_path)

        if success:
            await text.edit_text(
                f"❍ | [ʜᴏʟᴅ ᴛʜᴇ ʟɪɴᴋ]({upload_url})",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "❍ ᴄʀᴇᴀᴛᴇ ʙʏ ˹ ʙᴀʙʏ-ᴍᴜsɪᴄ ™˼𓅂",
                                url=upload_url,
                            )
                        ]
                    ]
                ),
            )
        else:
            await text.edit_text("❍ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ᴜᴘʟᴏᴀᴅɪɴɢ.")

        os.remove(local_path)  # Clean up local file

    except Exception as e:
        logger.error(e)
        await text.edit_text("File upload failed.")
        if os.path.exists(local_path):
            os.remove(local_path)  # Clean up if download fails

if __name__ == "__main__":
    app.run()
