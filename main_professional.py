#!/usr/bin/env python3
"""
Professional Options Flow Analyzer
Advanced institutional-grade options flow monitoring system
"""

import sys
import os
import logging
import argparse
from datetime import datetime
import pandas as pd

# Add src and config to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([
    os.path.join(current_dir, 'src'),
    os.path.join(current_dir, 'config')
])

try:
    from advanced_settings import *
    from data_collector import OptionsDataCollector
    from advanced_analytics import AdvancedFlowAnalyzer, BlackScholesCalculator
    from dashboard import ProfessionalOptionsDashboard
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Please ensure all required files are in place.")
    sys.exit(1)

class ProfessionalOptionsFlowAnalyzer:
    """Main application class for professional options flow analysis"""
    
    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.collector = OptionsDataCollector()
        self.analyzer = AdvancedFlowAnalyzer()
        self.bs_calculator = BlackScholesCalculator()
        
        # Create necessary directories
        self.setup_directories()
        
        self.logger.info("🚀 Professional Options Flow Analyzer initialized")
    
    def setup_logging(self):
        """Set up professional logging configuration"""
        import logging.config
        logging.config.dictConfig(LOGGING_CONFIG)
    
    def setup_directories(self):
        """Create necessary directories"""
        directories = ['data', 'logs', 'exports', 'reports']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def analyze_single_symbol_advanced(self, symbol: str) -> Dict:
        """Perform comprehensive analysis on a single symbol"""
        
        self.logger.info(f"🔍 Starting advanced analysis for {symbol}")
        
        # Get basic options data
        result = self.collector.get_full_analysis(symbol)
        
        if 'error' in result:
            self.logger.error(f"Failed to get data for {symbol}: {result['error']}")
            return result
        
        options_data = result['data']
        stock_price = result['stock_price']
        
        # Enhanced analytics
        enhanced_result = result.copy()
        
        # 1. Greeks Analysis
        self.logger.info("📊 Calculating Greeks for all options...")
        enhanced_result['greeks_analysis'] = self.calculate_portfolio_greeks(options_data, stock_price)
        
        # 2. Max Pain Analysis
        self.logger.info("💰 Calculating Max Pain levels...")
        max_pain, pain_levels = self.analyzer.calculate_max_pain(options_data, stock_price)
        enhanced_result['max_pain'] = max_pain
        enhanced_result['pain_levels'] = pain_levels
        
        # 3. Put/Call Ratio Analysis
        self.logger.info("⚖️ Analyzing Put/Call ratios...")
        pc_analysis = self.analyzer.calculate_put_call_ratio(options_data)
        enhanced_result['put_call_analysis'] = pc_analysis
        
        # 4. Flow Classification
        self.logger.info("🌊 Classifying option flows...")
        flow_summary = self.classify_all_flows(options_data)
        enhanced_result['flow_classification'] = flow_summary
        
        # 5. Institutional Activity Detection
        self.logger.info("🏛️ Detecting institutional activity...")
        institutional_analysis = self.detect_institutional_activity(options_data)
        enhanced_result['institutional_activity'] = institutional_analysis
        
        # 6. Volatility Analysis
        self.logger.info("📈 Analyzing implied volatility patterns...")
        vol_analysis = self.analyze_volatility_surface(options_data)
        enhanced_result['volatility_analysis'] = vol_analysis
        
        self.logger.info(f"✅ Advanced analysis complete for {symbol}")
        return enhanced_result
    
    def calculate_portfolio_greeks(self, options_data: pd.DataFrame, stock_price: float) -> Dict:
        """Calculate portfolio-level Greeks"""
        
        if options_data.empty:
            return {}
        
        total_delta = 0
        total_gamma = 0
        total_theta = 0
        total_vega = 0
        
        for _, option in options_data.iterrows():
            # Calculate time to expiry
            expiry_str = option.get('expiration', '')
            try:
                expiry_date = datetime.strptime(expiry_str, '%Y-%m-%d')
                days_to_expiry = (expiry_date - datetime.now()).days
                T = max(days_to_expiry / 365, 0.001)  # Avoid division by zero
            except:
                T = 0.1  # Default to ~36 days
            
            # Get option parameters
            strike = option.get('strike', stock_price)
            option_type = option.get('option_type', 'call')
            volume = option.get('volume', 0)
            
            # Estimate implied volatility (use a default if not available)
            iv = option.get('impliedVolatility', 0.25)
            if iv <= 0:
                iv = 0.25  # Default 25% volatility
            
            # Calculate Greeks
            try:
                greeks = self.bs_calculator.calculate_greeks(
                    S=stock_price,
                    K=strike,
                    T=T,
                    r=MARKET_PARAMETERS['risk_free_rate'],
                    sigma=iv,
                    option_type=option_type
                )
                
                # Weight by volume
                total_delta += greeks.delta * volume
                total_gamma += greeks.gamma * volume
                total_theta += greeks.theta * volume
                total_vega += greeks.vega * volume
                
            except Exception as e:
                self.logger.warning(f"Could not calculate Greeks for option: {e}")
                continue
        
        return {
            'total_delta': total_delta,
            'total_gamma': total_gamma,
            'total_theta': total_theta,
            'total_vega': total_vega,
            'delta_exposure': abs(total_delta) * stock_price * 100,  # Dollar delta
            'gamma_risk': total_gamma * stock_price * stock_price * 0.01,  # 1% move
            'theta_decay': total_theta,  # Daily decay
            'vega_exposure': total_vega  # 1% vol move
        }
    
    def classify_all_flows(self, options_data: pd.DataFrame) -> Dict:
        """Classify all option flows"""
        
        if options_data.empty:
            return {}
        
        classifications = {
            'block_trades': 0,
            'sweep_trades': 0,
            'single_trades': 0,
            'institutional_flows': 0,
            'retail_flows': 0,
            'whale_flows': 0
        }
        
        detailed_flows = []
        
        for _, option in options_data.iterrows():
            flow_analysis = self.analyzer.analyze_single_trade(option.to_dict())
            
            # Count by flow type
            if flow_analysis.flow_type == 'block':
                classifications['block_trades'] += 1
            elif flow_analysis.flow_type == 'sweep':
                classifications['sweep_trades'] += 1
            else:
                classifications['single_trades'] += 1
            
            # Count by size
            if flow_analysis.size_category == 'institutional':
                classifications['institutional_flows'] += 1
            elif flow_analysis.size_category == 'whale':
                classifications['whale_flows'] += 1
            else:
                classifications['retail_flows'] += 1
            
            # Store detailed analysis
            detailed_flows.append({
                'contract': option.get('contractSymbol', ''),
                'flow_type': flow_analysis.flow_type,
                'size_category': flow_analysis.size_category,
                'sentiment': flow_analysis.sentiment,
                'unusual_score': flow_analysis.unusual_score,
                'confidence': flow_analysis.confidence
            })
        
        return {
            'summary': classifications,
            'detailed_flows': detailed_flows
        }
    
    def detect_institutional_activity(self, options_data: pd.DataFrame) -> Dict:
        """Detect potential institutional trading activity"""
        
        if options_data.empty:
            return {}
        
        # Institutional indicators
        large_trades = options_data[options_data['total_premium'] >= flow_config.institutional_threshold]
        dark_pool_indicators = options_data[options_data['volume'] > 1000]  # Large size
        
        # Cross-strike activity (same expiry, multiple strikes)
        expiry_groups = options_data.groupby('expiration')
        multi_strike_activity = []
        
        for expiry, group in expiry_groups:
            if len(group['strike'].unique()) >= 3:  # 3+ strikes
                total_premium = group['total_premium'].sum()
                if total_premium >= 250000:  # $250K+ across strikes
                    multi_strike_activity.append({
                        'expiry': expiry,
                        'strikes': len(group['strike'].unique()),
                        'total_premium': total_premium,
                        'total_volume': group['volume'].sum()
                    })
        
        return {
            'large_trade_count': len(large_trades),
            'large_trade_premium': large_trades['total_premium'].sum(),
            'potential_dark_pool_volume': dark_pool_indicators['volume'].sum(),
            'multi_strike_strategies': multi_strike_activity,
            'institutional_probability': self.calculate_institutional_probability(options_data)
        }
    
    def calculate_institutional_probability(self, options_data: pd.DataFrame) -> float:
        """Calculate probability that activity is institutional"""
        
        score = 0.0
        
        # Large premium indicator (0-30 points)
        total_premium = options_data['total_premium'].sum()
        if total_premium >= 5000000:  # $5M+
            score += 30
        elif total_premium >= 1000000:  # $1M+
            score += 25
        elif total_premium >= 500000:   # $500K+
            score += 20
        elif total_premium >= 100000:   # $100K+
            score += 15
        
        # Volume concentration (0-25 points)
        large_volume_trades = len(options_data[options_data['volume'] >= 500])
        if large_volume_trades >= 5:
            score += 25
        elif large_volume_trades >= 3:
            score += 20
        elif large_volume_trades >= 1:
            score += 15
        
        # Strike diversity (0-20 points)
        unique_strikes = len(options_data['strike'].unique())
        if unique_strikes >= 10:
            score += 20
        elif unique_strikes >= 5:
            score += 15
        elif unique_strikes >= 3:
            score += 10
        
        # Time spread (0-15 points)
        unique_expiries = len(options_data['expiration'].unique())
        if unique_expiries >= 3:
            score += 15
        elif unique_expiries >= 2:
            score += 10
        
        # Options mix (0-10 points)
        call_count = len(options_data[options_data['option_type'] == 'call'])
        put_count = len(options_data[options_data['option_type'] == 'put'])
        if call_count > 0 and put_count > 0:  # Both calls and puts
            score += 10
        
        return min(100.0, score)
    
    def analyze_volatility_surface(self, options_data: pd.DataFrame) -> Dict:
        """Analyze implied volatility patterns"""
        
        if options_data.empty:
            return {}
        
        # Filter options with valid IV
        valid_iv = options_data[
            (options_data['impliedVolatility'] > 0) & 
            (options_data['impliedVolatility'] < 5.0)  # Less than 500% IV
        ]
        
        if valid_iv.empty:
            return {'error': 'No valid implied volatility data'}
        
        # Calculate IV statistics
        iv_stats = {
            'mean_iv': valid_iv['impliedVolatility'].mean(),
            'median_iv': valid_iv['impliedVolatility'].median(),
            'iv_std': valid_iv['impliedVolatility'].std(),
            'min_iv': valid_iv['impliedVolatility'].min(),
            'max_iv': valid_iv['impliedVolatility'].max()
        }
        
        # IV by moneyness
        iv_by_moneyness = valid_iv.groupby('moneyness')['impliedVolatility'].agg([
            'mean', 'std', 'count'
        ]).to_dict()
        
        # IV skew analysis (calls vs puts)
        call_iv = valid_iv[valid_iv['option_type'] == 'call']['impliedVolatility'].mean()
        put_iv = valid_iv[valid_iv['option_type'] == 'put']['impliedVolatility'].mean()
        
        iv_skew = put_iv - call_iv if (call_iv > 0 and put_iv > 0) else 0
        
        return {
            'iv_statistics': iv_stats,
            'iv_by_moneyness': iv_by_moneyness,
            'iv_skew': iv_skew,
            'skew_interpretation': self.interpret_iv_skew(iv_skew)
        }
    
    def interpret_iv_skew(self, skew: float) -> str:
        """Interpret IV skew values"""
        if skew > 0.05:
            return "High put skew - Fear/hedging demand"
        elif skew > 0.02:
            return "Moderate put skew - Some defensive positioning"
        elif skew < -0.02:
            return "Negative skew - Call demand exceeds puts"
        else:
            return "Neutral skew - Balanced options demand"
    
    def generate_professional_report(self, analysis_result: Dict, symbol: str) -> str:
        """Generate a professional analysis report"""
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    PROFESSIONAL OPTIONS FLOW ANALYSIS REPORT                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Symbol: {symbol:<10} │ Generated: {timestamp:<20} │ Status: LIVE        ║
╚══════════════════════════════════════════════════════════════════════════════╝

📊 MARKET OVERVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Stock Price: ${analysis_result.get('stock_price', 0):.2f}
Total Contracts: {analysis_result.get('total_contracts', 0):,}
Total Premium Volume: ${analysis_result.get('total_premium_volume', 0):,.0f}
Unusual Activity Count: {analysis_result.get('unusual_activity_count', 0)}

⚖️ PUT/CALL ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        
        if 'put_call_analysis' in analysis_result:
            pc_analysis = analysis_result['put_call_analysis']
            report += f"""
Volume P/C Ratio: {pc_analysis.get('volume_put_call_ratio', 0):.3f}
Premium P/C Ratio: {pc_analysis.get('premium_put_call_ratio', 0):.3f}
Market Sentiment: {pc_analysis.get('sentiment', 'Unknown').upper()}
Total Call Volume: {pc_analysis.get('total_call_volume', 0):,}
Total Put Volume: {pc_analysis.get('total_put_volume', 0):,}"""
        
        report += f"""

💰 MAX PAIN ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Max Pain Level: ${analysis_result.get('max_pain', 0):.2f}
Distance from Current: {abs(analysis_result.get('stock_price', 0) - analysis_result.get('max_pain', 0)):.2f} ({((analysis_result.get('max_pain', 0) / analysis_result.get('stock_price', 1) - 1) * 100):+.1f}%)"""
        
        if 'greeks_analysis' in analysis_result:
            greeks = analysis_result['greeks_analysis']
            report += f"""

🔬 PORTFOLIO GREEKS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Delta: {greeks.get('total_delta', 0):,.0f}
Total Gamma: {greeks.get('total_gamma', 0):,.2f}
Total Theta: ${greeks.get('total_theta', 0):,.0f}/day
Total Vega: {greeks.get('total_vega', 0):,.0f}
Delta Exposure: ${greeks.get('delta_exposure', 0):,.0f}"""
        
        if 'flow_classification' in analysis_result:
            flows = analysis_result['flow_classification']['summary']
            report += f"""

🌊 FLOW CLASSIFICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Block Trades: {flows.get('block_trades', 0)}
Sweep Trades: {flows.get('sweep_trades', 0)}
Single Trades: {flows.get('single_trades', 0)}
Institutional Flows: {flows.get('institutional_flows', 0)}
Whale Activity: {flows.get('whale_flows', 0)}"""
        
        if 'institutional_activity' in analysis_result:
            inst = analysis_result['institutional_activity']
            report += f"""

🏛️ INSTITUTIONAL ACTIVITY ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Institutional Probability: {inst.get('institutional_probability', 0):.1f}%
Large Trade Count: {inst.get('large_trade_count', 0)}
Large Trade Premium: ${inst.get('large_trade_premium', 0):,.0f}
Multi-Strike Strategies: {len(inst.get('multi_strike_strategies', []))}"""
        
        if 'volatility_analysis' in analysis_result and 'iv_statistics' in analysis_result['volatility_analysis']:
            vol = analysis_result['volatility_analysis']
            iv_stats = vol['iv_statistics']
            report += f"""

📈 IMPLIED VOLATILITY ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Mean IV: {iv_stats.get('mean_iv', 0):.1%}
IV Range: {iv_stats.get('min_iv', 0):.1%} - {iv_stats.get('max_iv', 0):.1%}
IV Skew: {vol.get('iv_skew', 0):+.3f}
Interpretation: {vol.get('skew_interpretation', 'N/A')}"""
        
        report += f"""

🎯 TRADING INSIGHTS & RECOMMENDATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        
        # Add trading insights based on analysis
        insights = self.generate_trading_insights(analysis_result)
        for insight in insights:
            report += f"\n• {insight}"
        
        report += f"""

⚠️  RISK CONSIDERATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• This analysis is for informational purposes only
• Options trading involves substantial risk of loss
• Past performance does not guarantee future results
• Consider position sizing and risk management

Generated by Professional Options Flow Analyzer v2.0
Report ID: {symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}
"""
        
        return report
    
    def generate_trading_insights(self, analysis_result: Dict) -> List[str]:
        """Generate actionable trading insights"""
        
        insights = []
        
        # P/C Ratio insights
        if 'put_call_analysis' in analysis_result:
            pc_ratio = analysis_result['put_call_analysis'].get('volume_put_call_ratio', 0)
            if pc_ratio > 1.2:
                insights.append("High put activity suggests bearish sentiment or hedging demand")
            elif pc_ratio < 0.6:
                insights.append("High call activity indicates bullish positioning")
        
        # Institutional activity insights
        if 'institutional_activity' in analysis_result:
            inst_prob = analysis_result['institutional_activity'].get('institutional_probability', 0)
            if inst_prob > 70:
                insights.append("Strong institutional activity detected - monitor for directional bias")
            
            multi_strike = len(analysis_result['institutional_activity'].get('multi_strike_strategies', []))
            if multi_strike > 0:
                insights.append(f"Complex strategies detected across {multi_strike} expiration(s)")
        
        # Max pain insights
        stock_price = analysis_result.get('stock_price', 0)
        max_pain = analysis_result.get('max_pain', 0)
        if abs(stock_price - max_pain) / stock_price > 0.05:  # 5%+ difference
            direction = "above" if stock_price > max_pain else "below"
            insights.append(f"Stock trading {abs((stock_price/max_pain-1)*100):.1f}% {direction} max pain - potential magnet effect")
        
        # Greeks insights
        if 'greeks_analysis' in analysis_result:
            delta_exp = analysis_result['greeks_analysis'].get('delta_exposure', 0)
            if abs(delta_exp) > 1000000:  # $1M+ delta exposure
                direction = "long" if delta_exp > 0 else "short"
                insights.append(f"Significant {direction} delta exposure (${abs(delta_exp):,.0f}) - directional bias")
        
        # Volatility insights
        if 'volatility_analysis' in analysis_result:
            vol_data = analysis_result['volatility_analysis']
            if 'iv_statistics' in vol_data:
                mean_iv = vol_data['iv_statistics'].get('mean_iv', 0)
                if mean_iv > 0.4:  # 40%+ IV
                    insights.append("High implied volatility - potential volatility selling opportunities")
                elif mean_iv < 0.15:  # 15% IV
                    insights.append("Low implied volatility - potential volatility buying opportunities")
        
        if not insights:
            insights.append("Mixed signals - monitor for clearer directional bias")
        
        return insights
    
    def run_cli_interface(self):
        """Run the command line interface"""
        
        print("=" * 80)
        print("🚀 PROFESSIONAL OPTIONS FLOW ANALYZER")
        print("=" * 80)
        print("Advanced institutional-grade options analysis")
        print()
        
        while True:
            print("\n" + "=" * 50)
            print("MAIN MENU:")
            print("1. 🔍 Single Symbol Advanced Analysis")
            print("2. 📊 Multi-Symbol Screening")
            print("3. 🌐 Launch Web Dashboard")
            print("4. 📈 Market Overview")
            print("5. ⚙️  Settings & Configuration")
            print("6. 📋 Generate Report")
            print("7. 🚪 Exit")
            print("=" * 50)
            
            choice = input("Select option (1-7): ").strip()
            
            if choice == '1':
                self.single_symbol_analysis()
            elif choice == '2':
                self.multi_symbol_screening()
            elif choice == '3':
                self.launch_dashboard()
            elif choice == '4':
                self.market_overview()
            elif choice == '5':
                self.show_settings()
            elif choice == '6':
                self.generate_report_interface()
            elif choice == '7':
                print("\n👋 Thank you for using Professional Options Flow Analyzer!")
                break
            else:
                print("❌ Invalid choice. Please select 1-7.")
            
            input("\nPress Enter to continue...")
    
    def single_symbol_analysis(self):
        """Single symbol advanced analysis"""
        
        print("\n🔍 ADVANCED SYMBOL ANALYSIS")
        print("-" * 40)
        
        symbol = input("Enter symbol: ").strip().upper()
        if not symbol:
            print("❌ Invalid symbol")
            return
        
        print(f"\n🚀 Analyzing {symbol}...")
        print("This may take a few moments...")
        
        result = self.analyze_single_symbol_advanced(symbol)
        
        if 'error' in result:
            print(f"❌ Analysis failed: {result['error']}")
            return
        
        # Display results
        print(f"\n✅ Analysis complete for {symbol}")
        print(f"📊 Total contracts: {result.get('total_contracts', 0):,}")
        print(f"💰 Total premium: ${result.get('total_premium_volume', 0):,.0f}")
        print(f"⚡ Unusual activities: {result.get('unusual_activity_count', 0)}")
        
        # Show institutional probability
        if 'institutional_activity' in result:
            inst_prob = result['institutional_activity'].get('institutional_probability', 0)
            print(f"🏛️  Institutional probability: {inst_prob:.1f}%")
        
        # Offer to generate report
        generate = input("\nGenerate detailed report? (y/n): ").strip().lower()
        if generate == 'y':
            report = self.generate_professional_report(result, symbol)
            
            # Save report
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"reports/{symbol}_analysis_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"\n📋 Report saved to: {filename}")
            
            # Display key sections
            show_report = input("Display report now? (y/n): ").strip().lower()
            if show_report == 'y':
                print("\n" + "="*80)
                print(report)
                print("="*80)
    
    def multi_symbol_screening(self):
        """Screen multiple symbols"""
        
        print("\n📊 MULTI-SYMBOL SCREENING")
        print("-" * 40)
        
        # Use default symbol groups
        print("Available symbol groups:")
        for i, (group_name, symbols) in enumerate(MARKET_SYMBOLS.items(), 1):
            print(f"{i}. {group_name}: {', '.join(symbols[:5])}{'...' if len(symbols) > 5 else ''}")
        
        print(f"{len(MARKET_SYMBOLS) + 1}. Custom list")
        
        try:
            choice = int(input("Select group: ")) - 1
            group_names = list(MARKET_SYMBOLS.keys())
            
            if 0 <= choice < len(group_names):
                symbols = MARKET_SYMBOLS[group_names[choice]]
                print(f"\n🎯 Selected: {group_names[choice]}")
            elif choice == len(group_names):
                custom_input = input("Enter symbols (comma-separated): ")
                symbols = [s.strip().upper() for s in custom_input.split(',')]
            else:
                print("❌ Invalid choice")
                return
                
        except ValueError:
            print("❌ Invalid input")
            return
        
        print(f"\n🔄 Screening {len(symbols)} symbols...")
        
        results = []
        for i, symbol in enumerate(symbols, 1):
            print(f"Progress: {i}/{len(symbols)} - {symbol}")
            
            try:
                result = self.collector.get_full_analysis(symbol)
                if 'error' not in result:
                    results.append({
                        'Symbol': symbol,
                        'Stock_Price': result['stock_price'],
                        'Total_Premium': result['total_premium_volume'],
                        'Unusual_Count': result['unusual_activity_count'],
                        'Total_Contracts': result['total_contracts']
                    })
            except Exception as e:
                self.logger.error(f"Error analyzing {symbol}: {e}")
                continue
        
        if results:
            # Display results
            print(f"\n📈 SCREENING RESULTS")
            print("-" * 60)
            
            # Sort by unusual activity
            results.sort(key=lambda x: x['Unusual_Count'], reverse=True)
            
            print(f"{'Symbol':<8} {'Price':<10} {'Premium':<15} {'Unusual':<8} {'Contracts':<10}")
            print("-" * 60)
            
            for r in results[:10]:  # Top 10
                print(f"{r['Symbol']:<8} ${r['Stock_Price']:<9.2f} "
                      f"${r['Total_Premium']:<14,.0f} {r['Unusual_Count']:<8} "
                      f"{r['Total_Contracts']:<10}")
        else:
            print("❌ No results obtained")
    
    def launch_dashboard(self):
        """Launch the web dashboard"""
        
        print("\n🌐 LAUNCHING WEB DASHBOARD")
        print("-" * 40)
        
        try:
            dashboard = ProfessionalOptionsDashboard()
            dashboard.run(debug=False)
        except Exception as e:
            print(f"❌ Failed to launch dashboard: {e}")
            self.logger.error(f"Dashboard launch error: {e}")
    
    def market_overview(self):
        """Display market overview"""
        
        print("\n📈 MARKET OVERVIEW")
        print("-" * 40)
        print("Getting market data for key indices...")
        
        # Analyze key ETFs
        key_symbols = ['SPY', 'QQQ', 'IWM', 'VIX']
        
        for symbol in key_symbols:
            try:
                result = self.collector.get_full_analysis(symbol)
                if 'error' not in result:
                    print(f"\n{symbol}:")
                    print(f"  Price: ${result['stock_price']:.2f}")
                    print(f"  Premium Volume: ${result['total_premium_volume']:,.0f}")
                    print(f"  Unusual Activity: {result['unusual_activity_count']}")
                    
                    if 'put_call_analysis' in result:
                        pc_ratio = result['put_call_analysis'].get('volume_put_call_ratio', 0)
                        print(f"  P/C Ratio: {pc_ratio:.2f}")
                        
            except Exception as e:
                print(f"  {symbol}: Error - {e}")
    
    def show_settings(self):
        """Show current settings"""
        
        print("\n⚙️  CURRENT SETTINGS")
        print("-" * 40)
        print(f"Min Premium Threshold: ${flow_config.min_premium_threshold:,.0f}")
        print(f"Volume Multiplier: {flow_config.unusual_volume_multiplier}x")
        print(f"Risk-free Rate: {MARKET_PARAMETERS['risk_free_rate']:.1%}")
        print(f"Update Frequency: {viz_config.update_frequency_ms}ms")
        print("\nFeature Status:")
        for feature, enabled in FEATURES.items():
            status = "✅ Enabled" if enabled else "❌ Disabled"
            print(f"  {feature}: {status}")
    
    def generate_report_interface(self):
        """Generate report interface"""
        
        print("\n📋 GENERATE ANALYSIS REPORT")
        print("-" * 40)
        
        symbol = input("Enter symbol for report: ").strip().upper()
        if not symbol:
            print("❌ Invalid symbol")
            return
        
        print(f"🔄 Generating comprehensive report for {symbol}...")
        
        result = self.analyze_single_symbol_advanced(symbol)
        
        if 'error' in result:
            print(f"❌ Failed to generate report: {result['error']}")
            return
        
        report = self.generate_professional_report(result, symbol)
        
        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"reports/{symbol}_comprehensive_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ Report generated: {filename}")


def main():
    """Main function with command line argument parsing"""
    
    parser = argparse.ArgumentParser(description='Professional Options Flow Analyzer')
    parser.add_argument('--symbol', '-s', type=str, help='Analyze specific symbol')
    parser.add_argument('--dashboard', '-d', action='store_true', help='Launch web dashboard')
    parser.add_argument('--report', '-r', type=str, help='Generate report for symbol')
    parser.add_argument('--screening', '-sc', action='store_true', help='Run multi-symbol screening')
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = ProfessionalOptionsFlowAnalyzer()
    
    if args.dashboard:
        analyzer.launch_dashboard()
    elif args.symbol:
        result = analyzer.analyze_single_symbol_advanced(args.symbol.upper())
        if 'error' not in result:
            print(f"✅ Analysis complete for {args.symbol}")
            print(f"Premium Volume: ${result.get('total_premium_volume', 0):,.0f}")
            print(f"Unusual Activities: {result.get('unusual_activity_count', 0)}")
        else:
            print(f"❌ Analysis failed: {result['error']}")
    elif args.report:
        result = analyzer.analyze_single_symbol_advanced(args.report.upper())
        if 'error' not in result:
            report = analyzer.generate_professional_report(result, args.report.upper())
            print(report)
        else:
            print(f"❌ Report generation failed: {result['error']}")
    elif args.screening:
        analyzer.multi_symbol_screening()
    else:
        analyzer.run_cli_interface()


if __name__ == "__main__":
    main()