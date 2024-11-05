from pyrogram.types import InlineKeyboardButton

position_buttons = [
    [InlineKeyboardButton("⬅️ Left", callback_data="left"),
     InlineKeyboardButton("⬆️ Up", callback_data="up"),
     InlineKeyboardButton("➡️ Right", callback_data="right")],
    [InlineKeyboardButton("⬇️ Down", callback_data="down"),
     InlineKeyboardButton("🔽 Smaller", callback_data="smaller"),
     InlineKeyboardButton("🔼 Bigger", callback_data="bigger")]
]
