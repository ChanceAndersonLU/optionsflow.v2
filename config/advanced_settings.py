"""
Advanced Configuration for Professional Options Flow Analyzer
"""
import os
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime

load_dotenv()

@dataclass
class APIConfig:
    """API Configuration and Rate Limiting"""
    alpha_vantage_key: str = os.getenv('ALPHA_VANTAGE_API_KEY', '')
    polygon_key: str = os.getenv('POLYGON_API_KEY', '')
    tradier_key: str = os.getenv('TRADIER_API_KEY', '')
    cboe_key: str = os.getenv('CBOE_API_KEY', '')
    
    # Rate limiting
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    cache_duration_minutes: int = 5

@dataclass
class FlowDetectionConfig:
    """Advanced Flow Detection Parameters"""
    # Volume thresholds
    min_volume_threshold: int = 100
    unusual_volume_multiplier: float = 10.0
    block_trade_min_size: int = 500
    
    # Premium thresholds
    min_premium_threshold: float = 25000.0  # $25K
    large_premium_threshold: float = 100000.0  # $100K
    institutional_threshold: float = 500000.0  # $500K
    
    # Greeks sensitivity
    min_delta_change: float = 0.1
    high_gamma_threshold: float = 0.05
    min_vega_exposure: float = 1000.0
    
    # Time-based filters
    exclude_expiry_days: int = 2  # Exclude options expiring within 2 days
    min_days_to_expiry: int = 7
    max_days_to_expiry: int = 90
    
    # Sentiment analysis
    bullish_flow_ratio: float = 1.5  # Call/Put ratio for bullish sentiment
    bearish_flow_ratio: float = 0.67  # Call/Put ratio for bearish sentiment

@dataclass
class DatabaseConfig:
    """Database Configuration"""
    database_url: str = os.getenv('DATABASE_URL', 'sqlite:///data/options_flow.db')
    connection_pool_size: int = 10
    echo_sql: bool = False
    backup_frequency_hours: int = 24

@dataclass
class VisualizationConfig:
    """Dashboard and Visualization Settings"""
    # Chart settings
    chart_height: int = 600
    chart_width: int = 1200
    update_frequency_ms: int = 3000
    
    # Color scheme (Professional Dark Theme)
    colors: Dict[str, str] = None
    
    def __post_init__(self):
        if self.colors is None:
            self.colors = {
                'background': '#1e1e1e',
                'paper': '#2d2d2d',
                'text': '#ffffff',
                'bullish': '#00ff88',
                'bearish': '#ff6b6b',
                'neutral': '#ffd93d',
                'volume': '#74b9ff',
                'premium': '#fd79a8'
            }

@dataclass
class AlertingConfig:
    """Real-time Alerting Configuration"""
    # Email settings
    smtp_server: str = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port: int = int(os.getenv('SMTP_PORT', '587'))
    email_user: str = os.getenv('EMAIL_USER', '')
    email_password: str = os.getenv('EMAIL_PASSWORD', '')
    
    # Alert thresholds
    unusual_activity_threshold: int = 5
    large_trade_alert_threshold: float = 100000.0
    sentiment_shift_threshold: float = 0.3
    
    # Webhook settings
    discord_webhook: str = os.getenv('DISCORD_WEBHOOK', '')
    slack_webhook: str = os.getenv('SLACK_WEBHOOK', '')

# Main configuration instances
api_config = APIConfig()
flow_config = FlowDetectionConfig()
db_config = DatabaseConfig()
viz_config = VisualizationConfig()
alert_config = AlertingConfig()

# Market data settings
MARKET_SYMBOLS = {
    'MEGA_CAP': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'BRK-A'],
    'TECH': ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META', 'NFLX', 'CRM', 'ADBE'],
    'MEME_STOCKS': ['GME', 'AMC', 'BBBY', 'PLTR', 'WISH', 'CLOV'],
    'ETFS': ['SPY', 'QQQ', 'IWM', 'VIX', 'XLF', 'XLK', 'XLE'],
    'CRYPTO_RELATED': ['COIN', 'MSTR', 'RIOT', 'MARA', 'SQ'],
    'EARNINGS_WATCHLIST': []  # Dynamically populated
}

# Advanced market parameters
MARKET_PARAMETERS = {
    'trading_hours': {
        'market_open': '09:30',
        'market_close': '16:00',
        'extended_hours': True
    },
    'risk_free_rate': 0.045,  # Current 10-year treasury rate
    'market_volatility_index': 'VIX',
    'benchmark_symbols': ['SPY', 'QQQ', 'IWM']
}

# Logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(funcName)s() %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/options_flow.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'detailed'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

# Feature flags
FEATURES = {
    'real_time_streaming': True,
    'dark_pool_analysis': True,
    'sentiment_analysis': True,
    'machine_learning': True,
    'backtesting': True,
    'portfolio_tracking': True,
    'alerts_system': True,
    'api_endpoints': True
}