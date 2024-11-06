# button.py
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_adjustment_keyboard(final_image_path=None):
    buttons = [
        [InlineKeyboardButton("↼ʟᴇғᴛ", callback_data="move_left"),
         InlineKeyboardButton("ʀɪɢʜᴛ⇁", callback_data="move_right")],
        [InlineKeyboardButton("↿ᴜᴘ", callback_data="move_up"),
         InlineKeyboardButton("⇃ᴅᴏᴡɴ", callback_data="move_down")],
        [InlineKeyboardButton("⛶ ✙", callback_data="increase_size"),
         InlineKeyboardButton("⛶ –", callback_data="decrease_size")],
        
        # Color selection buttons
        [InlineKeyboardButton("🔴", callback_data="color_red"),
         InlineKeyboardButton("🔵", callback_data="color_blue"),
         InlineKeyboardButton("🟢", callback_data="color_green"),
         InlineKeyboardButton("⚫", callback_data="color_black"),
         InlineKeyboardButton("🟡", callback_data="color_yellow"),
         InlineKeyboardButton("🟠", callback_data="color_orange"),
         InlineKeyboardButton("🟣", callback_data="color_purple")],
        
        # Font selection buttons
        [InlineKeyboardButton("🄵ᴀ", callback_data="font_deadly_advance_italic"),
         InlineKeyboardButton("🄵ʙ", callback_data="font_deadly_advance"),
         InlineKeyboardButton("🄵ᴄ", callback_data="font_trick_or_treats"),
         InlineKeyboardButton("🄵ᴅ", callback_data="font_vampire_wars_italic"),
         InlineKeyboardButton("🄵ᴇ", callback_data="font_lobster")],
        
        # Blur buttons
        [InlineKeyboardButton("ʙʟᴜʀ +", callback_data="blur_plus"),
         InlineKeyboardButton("ʙʟᴜʀ -", callback_data="blur_minus")],

        # Always show the Download button
        [InlineKeyboardButton("ᴅᴏᴡɴʟᴏᴀᴅ ʏᴏᴜʀ ʟᴏɢᴏ", callback_data="download_logo")]
    ]
    
    return InlineKeyboardMarkup(buttons)
