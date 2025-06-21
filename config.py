import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Game Configuration
GAME_CONFIG = {
    'default_rounds': 6,
    'max_rounds': 10,
    'min_rounds': 3,
    'turn_time_limit': 120,  # seconds
    'image_size': (1024, 1024),  # BFL Flux supports higher resolutions
    'supported_formats': ['.jpg', '.jpeg', '.png', '.webp']
}

# Black Forest Labs Flux API Configuration
FLUX_CONFIG = {
    'api_url': 'https://api.bfl.ai/v1',
    'initial_model_endpoint': '/flux-pro-1.1',
    'alter_model_endpoint': '/flux-kontext-pro',
    'api_key': os.getenv('BFL_API_KEY'),
    'max_retries': 3,
    'timeout': 60  # Increased timeout for image generation
}

# File Structure Configuration
FILE_CONFIG = {
    'primary_image_dir': 'primary_image',
    'rounds_dir': 'rounds',
    'prompts_dir': 'prompts',
    'output_dir': 'output',
    'logs_dir': 'logs'
}

# UI Configuration
UI_CONFIG = {
    'window_title': 'Prompt Chain - AI Image Transformation Game (BFL Flux)',
    'window_size': '1200x800',
    'image_display_size': (400, 400),
    'font_family': 'Arial',
    'font_size': 12,
    'theme': {
        'bg_color': '#2b2b2b',
        'fg_color': '#ffffff',
        'accent_color': '#4CAF50',
        'error_color': '#f44336',
        'success_color': '#4CAF50'
    }
} 