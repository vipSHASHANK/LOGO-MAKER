from pyrogram.types import InlineKeyboardButton

# Inline keyboard buttons for adjusting the logo position
def get_position_buttons():
    buttons = [
        [InlineKeyboardButton("Left", callback_data="left"),
         InlineKeyboardButton("Right", callback_data="right")],
        [InlineKeyboardButton("Up", callback_data="up"),
         InlineKeyboardButton("Down", callback_data="down")],
        [InlineKeyboardButton("Smaller", callback_data="smaller"),
         InlineKeyboardButton("Bigger", callback_data="bigger")]
    ]
    return buttons
  
