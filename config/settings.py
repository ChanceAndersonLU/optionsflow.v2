import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '')
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY', '')

# Data Collection Settings
DEFAULT_SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'SPY', 'QQQ']
DATA_REFRESH_INTERVAL = 30  # seconds
MAX_DAYS_HISTORY = 5

# Flow Detection Thresholds
MIN_PREMIUM_THRESHOLD = 50000  # $50K minimum premium
VOLUME_MULTIPLIER_THRESHOLD = 10  # 10x average volume
UNUSUAL_OI_CHANGE_THRESHOLD = 1000  # Minimum OI change

# Database Configuration (using Windows path format)
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/options_flow.db')

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = 'logs/options_flow.log'

# Display Settings
CHART_HEIGHT = 600
CHART_WIDTH = 1200
UPDATE_FREQUENCY = 5000  # milliseconds for dashboard updates