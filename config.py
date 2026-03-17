"""Application configuration"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Database
    DB_NAME = os.getenv('DB_NAME', 'app.db')
    
    # Security
    RESET_CODE = os.getenv('RESET_CODE', '12218')
    MIN_PASSWORD_LENGTH = 4
    
    # UI Dimensions
    TOPBAR_HEIGHT = 50
    WINDOW_MARGIN = 40
    WIDGET_SPACING = 15
    INPUT_MAX_WIDTH = 500
    INPUT_WIDTH_RATIO = 0.5
    
    # UI Colors (Light Theme)
    WINDOW_BG = (240, 240, 240)
    WINDOW_TEXT = (0, 0, 0)
    BASE_BG = (255, 255, 255)
    ALTERNATE_BASE = (245, 245, 245)
    BUTTON_BG = (240, 240, 240)
    LINK_COLOR = (42, 130, 218)
    HIGHLIGHT_COLOR = (42, 130, 218)
    HIGHLIGHT_TEXT = (255, 255, 255)
    
    # Fonts
    FONT_FAMILY = 'Arial'
    FONT_SIZE_TITLE = 36
    FONT_SIZE_HEADING = 24
    FONT_SIZE_SUBHEADING = 14
    FONT_SIZE_NORMAL = 12
    FONT_SIZE_LABEL = 11
    FONT_SIZE_SMALL = 10
    
    # Timing
    SESSION_CHECK_DELAY = 100  # ms
