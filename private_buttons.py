from pyrogram.types import InlineKeyboardButton

# Define the buttons for position adjustment and glow color
position_buttons = [
    [InlineKeyboardButton("⬅️ Left", callback_data="left"),
     InlineKeyboardButton("⬆️ Up", callback_data="up"),
     InlineKeyboardButton("➡️ Right", callback_data="right")],
    [InlineKeyboardButton("⬇️ Down", callback_data="down"),
     InlineKeyboardButton("🔽 Smaller", callback_data="smaller"),
     InlineKeyboardButton("🔼 Bigger", callback_data="bigger")],
    # Adding glow color change buttons
    [InlineKeyboardButton("🔴 Red Glow", callback_data="glow_red"),
     InlineKeyboardButton("🟢 Green Glow", callback_data="glow_green"),
     InlineKeyboardButton("🔵 Blue Glow", callback_data="glow_blue")]
]
