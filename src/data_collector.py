import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time
import logging
import os
import sys

# Add config to path for Windows
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
from settings import *

class OptionsDataCollector:
    """Collects options chain data from various sources"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.session = requests.Session()
        
    def _setup_logger(self):
        """Set up logging configuration for Windows"""
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        logging.basicConfig(
            level=getattr(logging, LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/options_flow.log'),
                logging.StreamHandler()  # Also print to console
            ]
        )
        return logging.getLogger(__name__)
    
    def get_options_chain(self, symbol: str, expiration_date: str = None) -> pd.DataFrame:
        """
        Get options chain data for a given symbol using Yahoo Finance
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
            expiration_date: Specific expiration date (YYYY-MM-DD format)
        
        Returns:
            DataFrame with options data
        """
        try:
            self.logger.info(f"Fetching options data for {symbol}")
            ticker = yf.Ticker(symbol)
            
            # Get available expiration dates
            expirations = ticker.options
            if not expirations:
                self.logger.warning(f"No options available for {symbol}")
                return pd.DataFrame()
            
            # Use specified expiration or nearest one
            if expiration_date and expiration_date in expirations:
                target_exp = expiration_date
            else:
                target_exp = expirations[0]  # Use nearest expiration
                if expiration_date:
                    self.logger.warning(f"Expiration {expiration_date} not found, using {target_exp}")
            
            # Get options chain
            options_data = ticker.option_chain(target_exp)
            
            # Combine calls and puts
            calls = options_data.calls.copy()
            puts = options_data.puts.copy()
            
            if calls.empty and puts.empty:
                self.logger.warning(f"No options data found for {symbol}")
                return pd.DataFrame()
            
            # Add option type identifier
            calls['option_type'] = 'call'
            puts['option_type'] = 'put'
            
            # Combine both types
            combined = pd.concat([calls, puts], ignore_index=True)
            
            # Add metadata
            combined['symbol'] = symbol.upper()
            combined['timestamp'] = datetime.now()
            combined['expiration'] = target_exp
            
            # Calculate additional metrics
            combined['total_premium'] = combined['lastPrice'] * combined['volume'] * 100
            combined['moneyness'] = 'Unknown'  # We'll calculate this when we have stock price
            
            self.logger.info(f"Successfully retrieved {len(combined)} options contracts for {symbol}")
            return combined
            
        except Exception as e:
            self.logger.error(f"Error getting options chain for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def get_stock_price(self, symbol: str) -> float:
        """Get current stock price"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="5m")
            if not data.empty:
                current_price = data['Close'].iloc[-1]
                self.logger.info(f"Current price for {symbol}: ${current_price:.2f}")
                return current_price
            return 0.0
        except Exception as e:
            self.logger.error(f"Error getting stock price for {symbol}: {str(e)}")
            return 0.0
    
    def calculate_moneyness(self, options_df: pd.DataFrame, stock_price: float) -> pd.DataFrame:
        """Calculate whether options are ITM, ATM, or OTM"""
        if options_df.empty or stock_price == 0:
            return options_df
            
        def get_moneyness(row):
            if row['option_type'] == 'call':
                if row['strike'] < stock_price * 0.98:
                    return 'ITM'  # In the money
                elif row['strike'] > stock_price * 1.02:
                    return 'OTM'  # Out of the money
                else:
                    return 'ATM'  # At the money (within 2%)
            else:  # put
                if row['strike'] > stock_price * 1.02:
                    return 'ITM'
                elif row['strike'] < stock_price * 0.98:
                    return 'OTM'
                else:
                    return 'ATM'
        
        options_df['moneyness'] = options_df.apply(get_moneyness, axis=1)
        return options_df
    
    def identify_unusual_activity(self, options_df: pd.DataFrame) -> pd.DataFrame:
        """Identify potentially unusual options activity"""
        if options_df.empty:
            return options_df
        
        # High premium threshold
        options_df['high_premium'] = options_df['total_premium'] >= MIN_PREMIUM_THRESHOLD
        
        # High volume (relative to open interest)
        options_df['high_volume_ratio'] = (
            options_df['volume'] / (options_df['openInterest'] + 1)
        ) >= 0.5
        
        # Large single trades (approximation)
        options_df['potential_block'] = (
            (options_df['volume'] > 100) & 
            (options_df['total_premium'] > 25000)
        )
        
        # Mark unusual activity
        options_df['unusual_activity'] = (
            options_df['high_premium'] | 
            options_df['high_volume_ratio'] | 
            options_df['potential_block']
        )
        
        return options_df
    
    def get_full_analysis(self, symbol: str) -> Dict:
        """Get complete options analysis for a symbol"""
        try:
            # Get stock price
            stock_price = self.get_stock_price(symbol)
            
            # Get options data
            options_data = self.get_options_chain(symbol)
            
            if options_data.empty:
                return {'symbol': symbol, 'error': 'No options data available'}
            
            # Calculate moneyness
            options_data = self.calculate_moneyness(options_data, stock_price)
            
            # Identify unusual activity
            options_data = self.identify_unusual_activity(options_data)
            
            # Generate summary statistics
            unusual_count = options_data['unusual_activity'].sum()
            total_premium = options_data['total_premium'].sum()
            
            summary = {
                'symbol': symbol,
                'stock_price': stock_price,
                'total_contracts': len(options_data),
                'unusual_activity_count': int(unusual_count),
                'total_premium_volume': total_premium,
                'timestamp': datetime.now(),
                'data': options_data
            }
            
            self.logger.info(f"Analysis complete for {symbol}: {unusual_count} unusual activities found")
            return summary
            
        except Exception as e:
            self.logger.error(f"Error in full analysis for {symbol}: {str(e)}")
            return {'symbol': symbol, 'error': str(e)}
    
    def save_to_csv(self, data: pd.DataFrame, filename: str):
        """Save data to CSV file in the data directory"""
        try:
            # Create data directory if it doesn't exist
            os.makedirs('data', exist_ok=True)
            
            filepath = os.path.join('data', filename)
            data.to_csv(filepath, index=False)
            self.logger.info(f"Data saved to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error saving data to {filename}: {str(e)}")

# Test the collector if run directly
if __name__ == "__main__":
    print("🔍 Testing Options Data Collector...")
    
    collector = OptionsDataCollector()
    
    # Test with AAPL
    print("\n📊 Getting AAPL options data...")
    result = collector.get_full_analysis("AAPL")
    
    if 'error' not in result:
        print(f"✅ Success! Found {result['total_contracts']} contracts")
        print(f"📈 AAPL Stock Price: ${result['stock_price']:.2f}")
        print(f"⚡ Unusual Activities: {result['unusual_activity_count']}")
        
        # Save sample data
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"aapl_analysis_{timestamp}.csv"
        collector.save_to_csv(result['data'], filename)
        print(f"💾 Data saved to data/{filename}")
        
    else:
        print(f"❌ Error: {result['error']}")
    
    print("\n🎯 Test complete!")