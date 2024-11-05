from pyrogram.types import InlineKeyboardButton

# Define the buttons for position adjustment and text color
position_buttons = [
    [InlineKeyboardButton("⬅️ Left", callback_data="left"),
     InlineKeyboardButton("⬆️ Up", callback_data="up"),
     InlineKeyboardButton("➡️ Right", callback_data="right")],
    [InlineKeyboardButton("⬇️ Down", callback_data="down"),
     InlineKeyboardButton("🔽 Smaller", callback_data="smaller"),
     InlineKeyboardButton("🔼 Bigger", callback_data="bigger")],
    # Adding color change buttons
    [InlineKeyboardButton("⚪ White Text", callback_data="color_white"),
     InlineKeyboardButton("🔴 Red Text", callback_data="color_red"),
     InlineKeyboardButton("🟢 Green Text", callback_data="color_green")]
]
