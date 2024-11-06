# callbacks.py

from pyrogram.types import CallbackQuery
from main import save_user_data, get_user_data, add_text_to_image, convert_to_jpg, get_adjustment_keyboard
from random import randint
import os


async def handle_callback(_, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user_data = await get_user_data(user_id)

    if not user_data or not user_data.get("photo_path"):
        await callback_query.answer("Please upload a photo first.", show_alert=True)
        return

    # Handle button presses and update user data accordingly
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
    elif callback_query.data == "blur_decrease":
        user_data['blur_radius'] = max(user_data['blur_radius'] - 1, 0)  # Prevent going below 0
    elif callback_query.data == "blur_increase":
        user_data['blur_radius'] += 1  # Increase blur radius
    elif callback_query.data == "font_deadly_advance_italic":
        user_data['font'] = "fonts/Deadly Advance Italic (1).ttf"
    elif callback_query.data == "font_deadly_advance":
        user_data['font'] = "fonts/Deadly Advance.ttf"
    elif callback_query.data == "font_trick_or_treats":
        user_data['font'] = "fonts/Trick or Treats.ttf"
    elif callback_query.data == "font_vampire_wars_italic":
        user_data['font'] = "fonts/Vampire Wars Italic.ttf"
    elif callback_query.data == "font_lobster":
        user_data['font'] = "fonts/FIGHTBACK.ttf"
    elif callback_query.data == "download_jpg":
        # Convert the current final image to JPG and send it
        final_image_path = await add_text_to_image(user_data['photo_path'], user_data['text'], user_data['font'], user_data['text_position'], user_data['size_multiplier'], user_data['text_color'], user_data['blur_radius'])
        
        if final_image_path:
            # Convert to JPG
            jpg_path = convert_to_jpg(final_image_path)
            if jpg_path:
                with open(jpg_path, "rb") as jpg_file:
                    await callback_query.message.reply_document(jpg_file, caption="Here is your logo as a JPG file.")
                os.remove(jpg_path)  # Clean up the temporary JPG file after sending it
                os.remove(final_image_path)  # Clean up the temporary PNG file after sending it
            else:
                await callback_query.message.reply_text("Error converting image to JPG.")
        else:
            await callback_query.message.reply_text("Error generating the final logo.")

        return

    await save_user_data(user_id, user_data)

    # Regenerate the logo with the new adjustments
    font_path = user_data.get("font", "fonts/Deadly Advance.ttf")  # Default to Deadly Advance font if no font is set
    output_path = await add_text_to_image(user_data['photo_path'], user_data['text'], font_path, user_data['text_position'], user_data['size_multiplier'], user_data['text_color'], user_data['blur_radius'])

    if output_path is None:
        await callback_query.message.reply_text("There was an error generating the logo. Please try again.")
        return

    # Keep the buttons and update the image
    await callback_query.message.edit_media(InputMediaPhoto(media=output_path, caption="Here is your logo with the changes!"), reply_markup=get_adjustment_keyboard())
    await callback_query.answer()
