from pyrogram.types import InlineKeyboardButton

# Function to create position buttons (left, right, up, down)
def create_position_buttons():
    return [
        [
            InlineKeyboardButton("Left", callback_data="position_left"),
            InlineKeyboardButton("Right", callback_data="position_right")
        ],
        [
            InlineKeyboardButton("Up", callback_data="position_up"),
            InlineKeyboardButton("Down", callback_data="position_down")
        ]
    ]

# Function to create size buttons (zoom in, zoom out)
def create_size_buttons():
    return [
        [
            InlineKeyboardButton("Zoom In", callback_data="size_1.5"),
            InlineKeyboardButton("Zoom Out", callback_data="size_0.8")
        ]
    ]

# Function to create color buttons (red, blue, white)
def create_color_buttons():
    return [
        [
            InlineKeyboardButton("Red", callback_data="color_red"),
            InlineKeyboardButton("Blue", callback_data="color_blue"),
            InlineKeyboardButton("White", callback_data="color_white")
        ]
    ]
