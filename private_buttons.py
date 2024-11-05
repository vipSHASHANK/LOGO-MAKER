# private_buttons.py
from pyrogram.types import InlineKeyboardButton

# Font options for user selection
FONT_OPTIONS = [
    {"name": "FIGHTBACK", "callback_data": "font_FIGHTBACK"},
    {"name": "Arial", "callback_data": "font_Arial"},
    {"name": "Times New Roman", "callback_data": "font_Times New Roman"},
    {"name": "Courier", "callback_data": "font_Courier"},
    {"name": "Verdana", "callback_data": "font_Verdana"},
]

# Function to create font selection buttons
def create_font_buttons():
    buttons = []
    for font in FONT_OPTIONS:
        buttons.append(InlineKeyboardButton(font["name"], callback_data=font["callback_data"]))
    return buttons

# Position buttons (left, right, up, down) and size adjustment buttons (smaller, bigger)
POSITION_SIZE_BUTTONS = [
    [InlineKeyboardButton("⬅️ Left", callback_data="left"),
     InlineKeyboardButton("➡️ Right", callback_data="right")],
    [InlineKeyboardButton("⬆️ Up", callback_data="up"),
     InlineKeyboardButton("⬇️ Down", callback_data="down")],
    [InlineKeyboardButton("🔻 Smaller", callback_data="smaller"),
     InlineKeyboardButton("🔺 Bigger", callback_data="bigger")],
]

# Glow color buttons (red, green, blue)
GLOW_COLOR_BUTTONS = [
    [InlineKeyboardButton("🔴 Red", callback_data="glow_red"),
     InlineKeyboardButton("🟢 Green", callback_data="glow_green")],
    [InlineKeyboardButton("🔵 Blue", callback_data="glow_blue")],
]
