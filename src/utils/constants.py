"""
Application Constants
Centralized location for constants used throughout the application.
"""
import os.path

# Application information
APP_TITLE = "Google Tasks Desktop"
APP_SETTINGS = "Google Tasks Desktop"
ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "asset", "Google_Tasks_2021.svg.png")

# Theme constants
SETTING_THEME = "theme"
THEME_LIGHT = "light"
THEME_DARK = "dark"

# API constants
MAX_RESULTS = 10

# UI Constants
UI_FONT_FAMILY = "Microsoft JhengHei"
UI_BUTTON_HEIGHT = 24
UI_BUTTON_MAX_WIDTH = 50
UI_TASK_FONT_SIZE = 8
UI_LIST_FONT_SIZE = 10
UI_TITLE_FONT_SIZE = 10
UI_SMALL_ICON_SIZE = 20
UI_TREE_INDENTATION = 12
UI_PIN_BUTTON_SIZE = 18
UI_ANCHOR_BUTTON_SIZE = 18
UI_OPACITY_BUTTON_SIZE = 18
