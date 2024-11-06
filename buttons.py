# buttons.py

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_adjustment_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Left", callback_data="move_left"),
         InlineKeyboardButton("➡️ Right", callback_data="move_right")],
        [InlineKeyboardButton("⬆️ Up", callback_data="move_up"),
         InlineKeyboardButton("⬇️ Down", callback_data="move_down")],
        [InlineKeyboardButton("🔍 Increase", callback_data="increase_size"),
         InlineKeyboardButton("🔎 Decrease", callback_data="decrease_size")],
        
        # Color selection buttons
        [InlineKeyboardButton("🔴 Red", callback_data="color_red"),
         InlineKeyboardButton("🔵 Blue", callback_data="color_blue"),
         InlineKeyboardButton("🟢 Green", callback_data="color_green"),
         InlineKeyboardButton("⚫ Black", callback_data="color_black"),
         InlineKeyboardButton("🟡 Yellow", callback_data="color_yellow"),
         InlineKeyboardButton("🟠 Orange", callback_data="color_orange"),
         InlineKeyboardButton("🟣 Purple", callback_data="color_purple")],
        
        # Blur effect buttons
        [InlineKeyboardButton("🔵 Blur -", callback_data="blur_decrease"),
         InlineKeyboardButton("🔴 Blur +", callback_data="blur_increase")],
        
        # Font selection buttons
        [InlineKeyboardButton("Deadly Advance Italic", callback_data="font_deadly_advance_italic"),
         InlineKeyboardButton("Deadly Advance", callback_data="font_deadly_advance"),
         InlineKeyboardButton("Trick or Treats", callback_data="font_trick_or_treats"),
         InlineKeyboardButton("Vampire Wars Italic", callback_data="font_vampire_wars_italic"),
         InlineKeyboardButton("Lobster", callback_data="font_lobster")],

        # Download button
        [InlineKeyboardButton("Download JPG", callback_data="download_jpg")]
    ])
  
