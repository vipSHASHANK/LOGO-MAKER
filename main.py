import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config  # Ensure you have this file for your bot's config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to create the client
def create_client():
    try:
        app = Client(
            "premium_text_bot_session",  # Session name
            bot_token=Config.BOT_TOKEN,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
        )
        return app
    except Exception as e:
        logger.error(f"Error creating client: {e}")
        return None

# Function to generate 10 premium stylish text variations
def generate_premium_text_styles(input_text):
    """Generate 10 premium styles of the text using various Unicode scripts."""
    
    # List of premium text styles using symbols and special characters
    styles = [
        f"𝐐ꭎ𝛆፝֠֩᷍𝛆𝛈◄⏤͟͟͞ {input_text}",
        f"🤍⃝⃪🅼︎𝐚𝐬𝐭𝐢 🅼︎𝐮𝐬𝐢𝐜🐬 ̶꯭𝅥ͦ𝆬 ⃪𝄄𝄀꯭𝄄꯭⎯꯭ͯ⟶⋆ {input_text}",
        f"ʂҽʂʂισɳʂ {input_text}",
        f"˹ sᴘꪮᴛιϝʏ ɱᴜsιᴄ ˼ {input_text}",
        f"♪𝚫꯭̌𝗥꯭❍꯭֟፝͝𝗛꯭𝗜𝄢 {input_text}",
        f"🌀⏝⏤⃪𝓜𝓾𝓼𝓲𝓬 🎵 𝗔𝑳𝓮𝑎 {input_text}",
        f"⨀𝒮𝒸𝓇𝒾𝓅𝓉𝒶𝓁 𝖭𝒾𝒸𝑒 {input_text}",
        f"⏺⟟⛂🅻ꭹ⩺𝓣𝑒𝑿𝒕⩮⧼ {input_text}",
        f"𝓢⩂𝗝𝒐𝓮𝕃🎤𝓡⧝𝓞𝔽𝒮🧷 {input_text}",
        f"𝖑𝖎𝖓𝖐𝑒𝗿𝑒𑁍⛀𝑳𝒊𝑳𝑬𝓈𝒾⧪ {input_text}"
    ]
    
    return styles

# Text handler (processing text)
async def text_handler(_, message: Message) -> None:
    """Handles incoming text messages and applies stylish transformations."""
    if message.text:
        user_text = message.text.strip()
        
        if not user_text:
            await message.reply_text("Please send some text for styling.")
            return
        
        # Generate the premium text styles
        premium_styles = generate_premium_text_styles(user_text)
        
        # Send the styled texts back to the user
        await message.reply_text("\n\n".join(premium_styles))

# Main entry point to run the bot
if __name__ == "__main__":
    app = create_client()
    if app:
        # Define handlers after the app is created
        app.on_message(filters.text & filters.private)(text_handler)

        # Run the bot
        app.run()
    else:
        logger.error("Failed to create the client.")
        
