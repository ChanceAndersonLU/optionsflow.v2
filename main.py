#!/usr/bin/env python3
"""
Options Flow Analyzer - Main Application
Windows Version for Python 3.13.7
"""

import sys
import os
from datetime import datetime
import pandas as pd

# Add src directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.append(src_path)

try:
    from data_collector import OptionsDataCollector
    from config.settings import DEFAULT_SYMBOLS
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

def print_banner():
    """Print application banner"""
    print("=" * 60)
    print("🚀 OPTIONS FLOW ANALYZER")
    print("=" * 60)
    print("📊 Real-time options activity monitoring")
    print("⚡ Unusual flow detection")
    print("💰 Large premium tracking")
    print("=" * 60)

def analyze_single_symbol(collector, symbol):
    """Analyze a single symbol and display results"""
    print(f"\n🔍 Analyzing {symbol}...")
    
    result = collector.get_full_analysis(symbol)
    
    if 'error' in result:
        print(f"❌ Error analyzing {symbol}: {result['error']}")
        return False
    
    # Display results
    print(f"✅ {symbol} Analysis Complete:")
    print(f"   📈 Stock Price: ${result['stock_price']:.2f}")
    print(f"   📋 Total Contracts: {result['total_contracts']:,}")
    print(f"   ⚡ Unusual Activities: {result['unusual_activity_count']}")
    print(f"   💰 Total Premium Volume: ${result['total_premium_volume']:,.0f}")
    
    # Show top unusual activities
    if result['unusual_activity_count'] > 0:
        unusual_data = result['data'][result['data']['unusual_activity'] == True]
        print(f"\n🎯 Top Unusual Activities for {symbol}:")
        
        # Sort by total premium and show top 5
        top_unusual = unusual_data.nlargest(5, 'total_premium')[
            ['contractSymbol', 'strike', 'option_type', 'volume', 'total_premium', 'moneyness']
        ]
        
        for idx, row in top_unusual.iterrows():
            print(f"   🔥 {row['option_type'].upper()} ${row['strike']} "
                  f"Vol: {row['volume']} Premium: ${row['total_premium']:,.0f} "
                  f"({row['moneyness']})")
    
    # Save data
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{symbol.lower()}_analysis_{timestamp}.csv"
    collector.save_to_csv(result['data'], filename)
    print(f"💾 Data saved to data/{filename}")
    
    return True

def analyze_multiple_symbols(collector, symbols):
    """Analyze multiple symbols"""
    print(f"\n📊 Analyzing {len(symbols)} symbols...")
    
    results = []
    for i, symbol in enumerate(symbols, 1):
        print(f"\nProgress: {i}/{len(symbols)} - {symbol}")
        
        result = collector.get_full_analysis(symbol)
        if 'error' not in result:
            results.append({
                'Symbol': symbol,
                'Stock_Price': result['stock_price'],
                'Total_Contracts': result['total_contracts'],
                'Unusual_Count': result['unusual_activity_count'],
                'Total_Premium': result['total_premium_volume']
            })
        
        # Small delay to avoid hitting rate limits
        import time
        time.sleep(1)
    
    # Create summary
    if results:
        summary_df = pd.DataFrame(results)
        print(f"\n📈 SUMMARY - Top Unusual Activity:")
        print("=" * 50)
        
        # Sort by unusual activity count
        top_activity = summary_df.nlargest(3, 'Unusual_Count')
        for idx, row in top_activity.iterrows():
            print(f"🏆 {row['Symbol']}: {row['Unusual_Count']} unusual activities "
                  f"(${row['Total_Premium']:,.0f} premium)")
        
        # Save summary
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        summary_filename = f"summary_{timestamp}.csv"
        collector.save_to_csv(summary_df, summary_filename)
        print(f"\n💾 Summary saved to data/{summary_filename}")

def main():
    """Main application function"""
    print_banner()
    
    # Create necessary directories
    for directory in ['data', 'logs']:
        os.makedirs(directory, exist_ok=True)
    
    # Initialize collector
    try:
        collector = OptionsDataCollector()
        print("✅ Options Data Collector initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize collector: {e}")
        return
    
    # Main menu loop
    while True:
        print(f"\n{'='*40}")
        print("MAIN MENU:")
        print("1. Analyze single symbol")
        print("2. Analyze default symbols (AAPL, MSFT, GOOGL, TSLA, NVDA)")
        print("3. Quick test with AAPL")
        print("4. Exit")
        print("="*40)
        
        choice = input("Choose an option (1-4): ").strip()
        
        if choice == '1':
            symbol = input("Enter symbol (e.g., AAPL): ").strip().upper()
            if symbol:
                analyze_single_symbol(collector, symbol)
            else:
                print("❌ Invalid symbol")
                
        elif choice == '2':
            print(f"🎯 Analyzing default symbols: {', '.join(DEFAULT_SYMBOLS[:5])}")
            analyze_multiple_symbols(collector, DEFAULT_SYMBOLS[:5])  # Limit to 5 to avoid rate limits
            
        elif choice == '3':
            print("🚀 Running quick test...")
            success = analyze_single_symbol(collector, "AAPL")
            if success:
                print("✅ Quick test completed successfully!")
            
        elif choice == '4':
            print("👋 Goodbye! Thanks for using Options Flow Analyzer")
            break
            
        else:
            print("❌ Invalid choice. Please select 1-4.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Application interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        input("Press Enter to exit...")