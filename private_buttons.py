from pyrogram.types import InlineKeyboardButton

# Function to create color selection buttons
def create_color_buttons():
    colors = ["Red", "Green", "Blue", "Yellow", "White", "Black"]
    # Return a list of lists directly
    buttons = [
        [InlineKeyboardButton(color, callback_data=f"color_{color.lower()}")] for color in colors
    ]
    return buttons

# Function to create position (left, right, up, down) buttons
def create_position_buttons():
    position_buttons = [
        [InlineKeyboardButton("Up", callback_data="position_up"), 
         InlineKeyboardButton("Down", callback_data="position_down")],
        [InlineKeyboardButton("Left", callback_data="position_left"), 
         InlineKeyboardButton("Center", callback_data="position_center"), 
         InlineKeyboardButton("Right", callback_data="position_right")]
    ]
    return position_buttons

# Function to create size (small, big) buttons
def create_size_buttons():
    size_buttons = [
        [InlineKeyboardButton("Small", callback_data="size_small"), 
         InlineKeyboardButton("Big", callback_data="size_big")]
    ]
    return size_buttons

# Function to create font selection buttons
def create_font_buttons():
    fonts = ["FIGHTBACK", "Arial", "Times New Roman", "Courier"]
    buttons = [
        [InlineKeyboardButton(font, callback_data=f"font_{font.lower()}")] for font in fonts
    ]
    return buttons
