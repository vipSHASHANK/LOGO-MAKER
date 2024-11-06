from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Function to create color selection buttons
def create_colour_buttons():
    colour_buttons = [
        [InlineKeyboardButton("Red", callback_data="colour_red")],
        [InlineKeyboardButton("Green", callback_data="colour_green")],
        [InlineKeyboardButton("Blue", callback_data="colour_blue")],
        [InlineKeyboardButton("Yellow", callback_data="colour_yellow")],
        [InlineKeyboardButton("White", callback_data="colour_white")],
        [InlineKeyboardButton("Black", callback_data="colour_black")]
    ]
    return InlineKeyboardMarkup(colour_buttons)

# Function to create position (left, right, up, down) buttons
def create_position_buttons():
    position_buttons = [
        [InlineKeyboardButton("Up", callback_data="position_up"), 
         InlineKeyboardButton("Down", callback_data="position_down")],
        [InlineKeyboardButton("Left", callback_data="position_left"), 
         InlineKeyboardButton("Center", callback_data="position_center"), 
         InlineKeyboardButton("Right", callback_data="position_right")]
    ]
    return InlineKeyboardMarkup(position_buttons)

# Function to create size (small, big) buttons
def create_size_buttons():
    size_buttons = [
        [InlineKeyboardButton("Small", callback_data="size_small"), 
         InlineKeyboardButton("Big", callback_data="size_big")]
    ]
    return InlineKeyboardMarkup(size_buttons)

# Function to create font selection buttons
def create_font_buttons():
    font_buttons = [
        [InlineKeyboardButton("FIGHTBACK", callback_data="font_fightback")],
        [InlineKeyboardButton("Arial", callback_data="font_arial")],
        [InlineKeyboardButton("Times New Roman", callback_data="font_times_new_roman")],
        [InlineKeyboardButton("Courier", callback_data="font_courier")]
    ]
    return InlineKeyboardMarkup(font_buttons)
