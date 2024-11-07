import os

# Define constants for directories and API details
API_KEY_FILE = "apikey.txt"
CHAR_FILE = "char.txt"
FONT_DOWNLOAD_URL = "https://www.googleapis.com/webfonts/v1/webfonts"
FONTS_DIR = "fonts"
OUTPUT_DIR = "output"

# Define resolution sizes
SIZES = [454, 416, 390, 360, 280, 260, 240]
BASE_RESOLUTION = 454
MAX_ROW_WIDTH = 500

# Style filename mappings
STYLE_FILENAME = {
    "regular": "regular",
    "bold": "700",
    "italic": "italic",
    "bolditalic": "700italic"
}