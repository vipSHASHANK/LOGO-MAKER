import os
import logging
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.handlers import CallbackQueryHandler
from PIL import Image, ImageDraw, ImageFont
from config import Config  # Ensure you have your correct bot token and API credentials
from private_buttons import get_position_buttons  # Importing buttons

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Dictionary to store user data
user_data = {}

# Function to dynamically adjust text size based on available space
def get_dynamic_font(image, text, max_width, max_height):
    # Create ImageDraw object to calculate text size
    draw = ImageDraw.Draw(image)
    
    # Try different font sizes
    font_size = 100
    while font_size > 10:
        font = ImageFont.truetype("fonts/FIGHTBACK.ttf", font_size)
        text_width, text_height = draw.textsize(text, font=font)
        
        # If the text fits within the available space, break the loop
        if text_width <= max_width and text_height <= max_height:
            return font, text_width, text_height
        
        font_size -= 5  # Reduce font size if text is too big

    # Return the smallest font if no suitable size is found
    return font, text_width, text_height

# Function to add text to an image at a specified position
def add_text_to_image(photo_path, text, output_path, x_offset=0, y_offset=0, size_multiplier=1):
    try:
        # Load the image
        user_image = Image.open(photo_path)
        user_image = user_image.convert("RGBA")  # Convert to RGBA for transparency

        # Dynamically calculate the font size to fit within the image
        max_width, max_height = user_image.size
        font, text_width, text_height = get_dynamic_font(user_image, text, max_width, max_height)

        # Apply size multiplier and adjust position
        text_width = int(text_width * size_multiplier)
        text_height = int(text_height * size_multiplier)

        # Center the text based on the image size, then apply offsets
        x = (max_width - text_width) // 2 + x_offset
        y = (max_height - text_height) // 2 + y_offset
        text_position = (x, y)

        # Add refined glow effect to text
        draw = ImageDraw.Draw(user_image)
        add_refined_glow(draw, text_position, text, font, glow_color="red", text_color="white", glow_strength=10)

        # Save the final image with transparent background where necessary
        user_image.save(output_path, "PNG")
        return output_path
    except Exception as e:
        logger.error(f"Error adding text to image: {e}")
        return None

# Add refined glow effect to text
def add_refined_glow(draw, position, text, font, glow_color, text_color, glow_strength=5):
    x, y = position
    # Draw glow around the text with limited strength for edges
    for offset in range(1, glow_strength + 1):
        draw.text((x - offset, y - offset), text, font=font, fill=glow_color)
        draw.text((x + offset, y - offset), text, font=font, fill=glow_color)
        draw.text((x - offset, y + offset), text, font=font, fill=glow_color)
        draw.text((x + offset, y + offset), text, font=font, fill=glow_color)
    # Draw the main text in the center with the normal color
    draw.text(position, text, font=font, fill=text_color)

# Handler for when a user sends a photo
async def photo_handler(_, message: Message):
    if message.photo:
        # Save the received photo
        photo_path = f"user_photos/{message.photo.file_id}.jpg"
        await message.download(photo_path)

        # Ask the user to send the logo text
        await message.reply_text("Ab apna logo text bheje.")

        # Store the user's photo path and wait for text
        user_data[message.from_user.id] = {'photo_path': photo_path}

# Handler for receiving text and creating the logo
async def text_handler(_, message: Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        await message.reply_text("Pehle apna photo bheje.")
        return

    if message.text:
        user_text = message.text.strip()

        if not user_text:
            await message.reply_text("Logo text dena hoga.")
            return

        # Get the user's photo path
        photo_path = user_data[user_id]['photo_path']
        output_path = f"logos/{user_text}_logo.png"

        # Add the logo text to the photo and create the initial logo
        result = add_text_to_image(photo_path, user_text, output_path)

        if result:
            # Send the initial logo image to the user with buttons for position adjustments
            buttons = get_position_buttons()  # Get position buttons from the private_buttons file
            await message.reply_photo(output_path, reply_markup=InlineKeyboardMarkup(buttons))

            # Store the current state of the image and user adjustments
            user_data[user_id]['output_path'] = output_path
            user_data[user_id]['text_position'] = (0, 0)  # Default offset
            user_data[user_id]['size_multiplier'] = 1  # Default size multiplier

# Handler for position adjustments through buttons
async def button_handler(_, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id not in user_data:
        return

    # Extract the action from the button pressed
    action = callback_query.data
    user_info = user_data[user_id]
    
    # Adjust position or size based on action
    x_offset, y_offset = user_info['text_position']
    size_multiplier = user_info['size_multiplier']

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

    # Update user data with new position and size
    user_info['text_position'] = (x_offset, y_offset)
    user_info['size_multiplier'] = size_multiplier

    # Get the photo path and text to re-create the logo with new adjustments
    photo_path = user_info['photo_path']
    text = user_info.get('text', '')  # Keep original text from user
    output_path = f"logos/updated_{text}_logo.png"

    # Regenerate the logo with the new position and size
    add_text_to_image(photo_path, text, output_path, x_offset, y_offset, size_multiplier)

    # Send the updated logo image using edit_media
    await callback_query.message.edit_media(
        media={"type": "photo", "media": output_path},
        caption="Logo with updated position."
    )

# Main entry point to run the bot
if __name__ == "__main__":
    try:
        app = Client(
            "stylish_text_logo_bot_session",  # Session name
            bot_token=Config.BOT_TOKEN,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
        )

        # Register handlers
        app.add_handler(filters.photo, photo_handler)
        app.add_handler(filters.text, text_handler)
        app.add_handler(CallbackQueryHandler(button_handler))  # Correct handler for button presses

        # Run the bot
        app.run()
    except Exception as e:
        logger.error(f"Error starting the bot: {e}")
        
