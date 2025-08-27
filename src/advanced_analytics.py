"""
Advanced Options Analytics Engine
Professional-grade options analysis with Greeks, IV, and flow detection
"""

import numpy as np
import pandas as pd
from scipy.stats import norm
from scipy.optimize import minimize_scalar
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

@dataclass
class GreeksResult:
    """Container for options Greeks calculations"""
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float
    implied_volatility: float

@dataclass
class FlowAnalysis:
    """Container for flow analysis results"""
    flow_type: str  # 'block', 'sweep', 'single'
    sentiment: str  # 'bullish', 'bearish', 'neutral'
    size_category: str  # 'retail', 'institutional', 'whale'
    unusual_score: float  # 0-100 scale
    confidence: float  # 0-1 scale

class BlackScholesCalculator:
    """Professional Black-Scholes implementation for Greeks calculations"""
    
    @staticmethod
    def d1(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """Calculate d1 parameter for Black-Scholes"""
        if T <= 0 or sigma <= 0:
            return 0.0
        return (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    
    @staticmethod
    def d2(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """Calculate d2 parameter for Black-Scholes"""
        if T <= 0 or sigma <= 0:
            return 0.0
        return BlackScholesCalculator.d1(S, K, T, r, sigma) - sigma * np.sqrt(T)
    
    @staticmethod
    def call_price(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """Calculate theoretical call option price"""
        if T <= 0:
            return max(S - K, 0)
        
        d1 = BlackScholesCalculator.d1(S, K, T, r, sigma)
        d2 = BlackScholesCalculator.d2(S, K, T, r, sigma)
        
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    
    @staticmethod
    def put_price(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """Calculate theoretical put option price"""
        if T <= 0:
            return max(K - S, 0)
        
        d1 = BlackScholesCalculator.d1(S, K, T, r, sigma)
        d2 = BlackScholesCalculator.d2(S, K, T, r, sigma)
        
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    
    @staticmethod
    def calculate_greeks(S: float, K: float, T: float, r: float, sigma: float, 
                        option_type: str) -> GreeksResult:
        """Calculate all Greeks for an option"""
        if T <= 0:
            return GreeksResult(0, 0, 0, 0, 0, 0)
        
        d1 = BlackScholesCalculator.d1(S, K, T, r, sigma)
        d2 = BlackScholesCalculator.d2(S, K, T, r, sigma)
        
        # Common calculations
        sqrt_T = np.sqrt(T)
        norm_d1 = norm.pdf(d1)
        norm_cdf_d1 = norm.cdf(d1)
        norm_cdf_d2 = norm.cdf(d2)
        
        if option_type.lower() == 'call':
            delta = norm_cdf_d1
            rho = K * T * np.exp(-r * T) * norm_cdf_d2
        else:  # put
            delta = norm_cdf_d1 - 1
            rho = -K * T * np.exp(-r * T) * norm.cdf(-d2)
        
        # Greeks that are same for calls and puts
        gamma = norm_d1 / (S * sigma * sqrt_T)
        theta_common = -(S * norm_d1 * sigma) / (2 * sqrt_T) - r * K * np.exp(-r * T)
        
        if option_type.lower() == 'call':
            theta = (theta_common * norm_cdf_d2) / 365  # Convert to per day
        else:
            theta = (theta_common * norm.cdf(-d2)) / 365
        
        vega = S * norm_d1 * sqrt_T / 100  # Convert to percentage
        
        return GreeksResult(delta, gamma, theta, vega, rho, sigma)

class ImpliedVolatilityCalculator:
    """Calculate implied volatility using Newton-Raphson method"""
    
    @staticmethod
    def calculate_iv(market_price: float, S: float, K: float, T: float, r: float, 
                    option_type: str, max_iterations: int = 100, tolerance: float = 1e-6) -> float:
        """Calculate implied volatility"""
        if T <= 0 or market_price <= 0:
            return 0.0
        
        # Initial guess based on at-the-money approximation
        sigma = np.sqrt(2 * np.pi / T) * market_price / S
        sigma = max(0.01, min(5.0, sigma))  # Bound between 1% and 500%
        
        for _ in range(max_iterations):
            if option_type.lower() == 'call':
                price = BlackScholesCalculator.call_price(S, K, T, r, sigma)
            else:
                price = BlackScholesCalculator.put_price(S, K, T, r, sigma)
            
            diff = price - market_price
            
            if abs(diff) < tolerance:
                return sigma
            
            # Vega for Newton-Raphson
            d1 = BlackScholesCalculator.d1(S, K, T, r, sigma)
            vega = S * norm.pdf(d1) * np.sqrt(T)
            
            if vega < 1e-10:  # Avoid division by zero
                break
            
            sigma = sigma - diff / vega
            sigma = max(0.001, min(10.0, sigma))  # Keep reasonable bounds
        
        return sigma

class AdvancedFlowAnalyzer:
    """Advanced options flow analysis with institutional detection"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.bs_calc = BlackScholesCalculator()
        self.iv_calc = ImpliedVolatilityCalculator()
    
    def analyze_single_trade(self, trade_data: Dict) -> FlowAnalysis:
        """Analyze a single options trade for institutional characteristics"""
        
        # Extract trade parameters
        volume = trade_data.get('volume', 0)
        premium = trade_data.get('total_premium', 0)
        open_interest = trade_data.get('openInterest', 1)
        bid_ask_spread = trade_data.get('bid', 0) - trade_data.get('ask', 0)
        option_type = trade_data.get('option_type', '').lower()
        
        # Calculate flow characteristics
        flow_type = self._determine_flow_type(volume, premium, bid_ask_spread)
        size_category = self._categorize_trade_size(volume, premium)
        sentiment = self._analyze_sentiment(trade_data)
        unusual_score = self._calculate_unusual_score(trade_data)
        confidence = self._calculate_confidence(trade_data)
        
        return FlowAnalysis(flow_type, sentiment, size_category, unusual_score, confidence)
    
    def _determine_flow_type(self, volume: int, premium: float, spread: float) -> str:
        """Determine if trade is block, sweep, or single order"""
        
        # Block trade indicators
        if volume >= 500 and premium >= 100000:
            return 'block'
        
        # Sweep indicators (multiple exchanges, aggressive pricing)
        if volume >= 100 and spread > 0.05:  # Wide spread suggests aggressive order
            return 'sweep'
        
        return 'single'
    
    def _categorize_trade_size(self, volume: int, premium: float) -> str:
        """Categorize trade size as retail, institutional, or whale"""
        
        if premium >= 1000000 or volume >= 2000:  # $1M+ or 2000+ contracts
            return 'whale'
        elif premium >= 100000 or volume >= 500:  # $100K+ or 500+ contracts
            return 'institutional'
        else:
            return 'retail'
    
    def _analyze_sentiment(self, trade_data: Dict) -> str:
        """Analyze bullish/bearish sentiment from trade data"""
        
        option_type = trade_data.get('option_type', '').lower()
        moneyness = trade_data.get('moneyness', 'unknown').lower()
        volume = trade_data.get('volume', 0)
        
        # Simple sentiment heuristics
        if option_type == 'call':
            if moneyness in ['itm', 'atm']:
                return 'bullish'
            elif volume > 1000:  # Large OTM call volume can be bullish
                return 'bullish'
        elif option_type == 'put':
            if moneyness in ['itm', 'atm']:
                return 'bearish'
            elif volume > 1000:  # Large OTM put volume can be bearish
                return 'bearish'
        
        return 'neutral'
    
    def _calculate_unusual_score(self, trade_data: Dict) -> float:
        """Calculate 0-100 unusual activity score"""
        
        score = 0.0
        
        # Volume component (0-40 points)
        volume = trade_data.get('volume', 0)
        avg_volume = trade_data.get('avg_volume', volume)
        if avg_volume > 0:
            volume_ratio = volume / avg_volume
            score += min(40, volume_ratio * 5)
        
        # Premium component (0-30 points)
        premium = trade_data.get('total_premium', 0)
        if premium >= 1000000:  # $1M+
            score += 30
        elif premium >= 500000:  # $500K+
            score += 25
        elif premium >= 100000:  # $100K+
            score += 20
        elif premium >= 50000:   # $50K+
            score += 15
        
        # Open Interest component (0-20 points)
        volume = trade_data.get('volume', 0)
        open_interest = trade_data.get('openInterest', 1)
        oi_ratio = volume / open_interest if open_interest > 0 else 0
        if oi_ratio >= 1.0:  # Volume equals or exceeds OI
            score += 20
        elif oi_ratio >= 0.5:
            score += 15
        elif oi_ratio >= 0.25:
            score += 10
        
        # Time to expiry component (0-10 points)
        # (Would need expiry date calculation here)
        
        return min(100, score)
    
    def _calculate_confidence(self, trade_data: Dict) -> float:
        """Calculate confidence level (0-1) in the analysis"""
        
        confidence = 0.5  # Base confidence
        
        # Higher confidence with more data points
        if trade_data.get('bid', 0) > 0 and trade_data.get('ask', 0) > 0:
            confidence += 0.1
        
        if trade_data.get('impliedVolatility', 0) > 0:
            confidence += 0.1
        
        if trade_data.get('openInterest', 0) > 0:
            confidence += 0.1
        
        # Higher confidence with larger trades
        premium = trade_data.get('total_premium', 0)
        if premium >= 100000:
            confidence += 0.2
        
        return min(1.0, confidence)
    
    def calculate_max_pain(self, options_data: pd.DataFrame, stock_price: float) -> Tuple[float, Dict]:
        """Calculate max pain point and pain by strike"""
        
        if options_data.empty:
            return stock_price, {}
        
        # Group by strike
        strikes = options_data['strike'].unique()
        strikes.sort()
        
        pain_by_strike = {}
        
        for strike in strikes:
            total_pain = 0
            
            # Calculate pain for calls (ITM calls lose money as stock price falls)
            calls_data = options_data[
                (options_data['strike'] == strike) & 
                (options_data['option_type'] == 'call')
            ]
            
            for _, call in calls_data.iterrows():
                if stock_price > strike:
                    pain = call['openInterest'] * (stock_price - strike) * 100
                    total_pain += pain
            
            # Calculate pain for puts (ITM puts lose money as stock price rises)
            puts_data = options_data[
                (options_data['strike'] == strike) & 
                (options_data['option_type'] == 'put')
            ]
            
            for _, put in puts_data.iterrows():
                if stock_price < strike:
                    pain = put['openInterest'] * (strike - stock_price) * 100
                    total_pain += pain
            
            pain_by_strike[strike] = total_pain
        
        # Find strike with minimum pain (max pain point)
        if pain_by_strike:
            max_pain_strike = min(pain_by_strike.keys(), key=lambda k: pain_by_strike[k])
            return max_pain_strike, pain_by_strike
        
        return stock_price, {}
    
    def calculate_put_call_ratio(self, options_data: pd.DataFrame) -> Dict:
        """Calculate various put/call ratios"""
        
        if options_data.empty:
            return {}
        
        calls = options_data[options_data['option_type'] == 'call']
        puts = options_data[options_data['option_type'] == 'put']
        
        # Volume-based ratios
        call_volume = calls['volume'].sum()
        put_volume = puts['volume'].sum()
        volume_pcr = put_volume / call_volume if call_volume > 0 else 0
        
        # Open Interest ratios
        call_oi = calls['openInterest'].sum()
        put_oi = puts['openInterest'].sum()
        oi_pcr = put_oi / call_oi if call_oi > 0 else 0
        
        # Premium ratios
        call_premium = calls['total_premium'].sum()
        put_premium = puts['total_premium'].sum()
        premium_pcr = put_premium / call_premium if call_premium > 0 else 0
        
        return {
            'volume_put_call_ratio': volume_pcr,
            'oi_put_call_ratio': oi_pcr,
            'premium_put_call_ratio': premium_pcr,
            'total_call_volume': int(call_volume),
            'total_put_volume': int(put_volume),
            'total_call_oi': int(call_oi),
            'total_put_oi': int(put_oi),
            'sentiment': self._interpret_pcr(volume_pcr)
        }
    
    def _interpret_pcr(self, pcr: float) -> str:
        """Interpret put/call ratio for market sentiment"""
        if pcr > 1.2:
            return 'very_bearish'
        elif pcr > 1.0:
            return 'bearish'
        elif pcr > 0.8:
            return 'neutral'
        elif pcr > 0.6:
            return 'bullish'
        else:
            return 'very_bullish'

# Example usage and testing
if __name__ == "__main__":
    print("🔬 Testing Advanced Analytics Engine...")
    
    # Test Greeks calculation
    bs_calc = BlackScholesCalculator()
    greeks = bs_calc.calculate_greeks(
        S=150,      # Stock price
        K=155,      # Strike price
        T=30/365,   # 30 days to expiry
        r=0.045,    # Risk-free rate
        sigma=0.25, # 25% volatility
        option_type='call'
    )
    
    print(f"✅ Greeks calculated:")
    print(f"   Delta: {greeks.delta:.4f}")
    print(f"   Gamma: {greeks.gamma:.4f}")
    print(f"   Theta: {greeks.theta:.4f}")
    print(f"   Vega: {greeks.vega:.4f}")
    
    # Test IV calculation
    iv_calc = ImpliedVolatilityCalculator()
    implied_vol = iv_calc.calculate_iv(
        market_price=5.50,
        S=150, K=155, T=30/365, r=0.045,
        option_type='call'
    )
    
    print(f"✅ Implied Volatility: {implied_vol:.2%}")
    print("🎯 Advanced Analytics Engine ready!")