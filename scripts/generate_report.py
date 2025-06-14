import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json
import os
from jinja2 import Template

class AdvancedPortfolioTracker:
    def __init__(self):
        # המניות שלך עם תאריך קנייה 12.6.2025
        self.portfolio = {
            'ANET': {'purchase_date': '2025-06-12'},
            'AVGO': {'purchase_date': '2025-06-12'},
            'ASML': {'purchase_date': '2025-06-12'},
            'CEG': {'purchase_date': '2025-06-12'},
            'CRWD': {'purchase_date': '2025-06-12'},
            'NVDA': {'purchase_date': '2025-06-12'},
            'PLTR': {'purchase_date': '2025-06-12'},
            'TSLA': {'purchase_date': '2025-06-12'},
            'TMS': {'purchase_date': '2025-06-12'},
            'VRT': {'purchase_date': '2025-06-12'}
        }
        
        # מדדי השוואה
        self.benchmarks = {
            'SPY': 'S&P 500',  # S&P 500
            'QQQ': 'NASDAQ 100',  # NASDAQ 100
            'TQQQ': 'NASDAQ 3x'   # NASDAQ 3x leveraged
        }
        
        self.investment_per_stock = 100  # דולר לכל מניה
        
    def get_purchase_prices(self):
        """מביא מחירי סגירה מ-12.6.2025"""
        all_symbols = list(self.portfolio.keys()) + list(self.benchmarks.keys())
        
        # מביא נתונים היסטוריים לתאריך הקנייה
        purchase_date = '2025-06-12'
        end_date = '2025-06-13'  # יום אחרי כדי לוודא שיש נתונים
        
        purchase_data = yf.download(all_symbols, start=purchase_date, end=end_date)
        
        if len(all_symbols) == 1:
            purchase_prices = {all_symbols[0]: purchase_data['Close'].iloc[0]}
        else:
            purchase_prices = purchase_data['Close'].iloc[0].to_dict()
            
        # שמירת מחירי הקנייה לקובץ JSON
        os.makedirs('data', exist_ok=True)
        with open('data/purchase_prices.json', 'w') as f:
            json.dump(purchase_prices, f, indent=2)
            
        return purchase_prices
    
    def get_current_prices(self):
        """מביא מחירים נוכחיים"""
        all_symbols = list(self.portfolio.keys()) + list(self.benchmarks.keys())
        
        try:
            # מביא נתונים אחרונים
            current_data = yf.download(all_symbols, period='5d', interval='1d')
            
            if len(all_symbols) == 1:
                current_prices = {all_symbols[0]: current_data['Close'].iloc[-1]}
            else:
                current_prices = current_data['Close'].iloc[-1].to_dict()
                
            return current_prices
        except Exception as e:
            print(f"שגיאה בהבאת מחירים נוכחיים: {e}")
            return {}
    
    def load_or_fetch_purchase_prices(self):
        """טוען מחירי קנייה קיימים או מביא חדשים"""
        purchase_file = 'data/purchase_prices.json'
        
        if os.path.exists(purchase_file):
            with open(purchase_file, 'r') as f:
                return json.load(f)
        else:
            print("מביא מחירי קנייה לראשונה...")
            return self.get_purchase_prices()
    
    def calculate_performance_data(self):
        """מחשב את כל נתוני הביצועים"""
        purchase_prices = self.load_or_fetch_purchase_prices()
        current_prices = self.get_current_prices()
        
        if not current_prices:
            print("❌ לא ניתן לקבל מחירים נוכחיים")
            return None
        
        # נתוני התיק
        portfolio_data = []
        total_invested = 0
        total_current_value = 0
        
        for symbol in self.portfolio.keys():
            if symbol not in purchase_prices or symbol not in current_prices:
                print(f"⚠️ חסרים נתונים עבור {symbol}")
                continue
                
            purchase_price = purchase_prices[symbol]
            current_price = current_prices[symbol]
            
            # חישוב ביצועים
            change_percent = ((current_price - purchase_price) / purchase_price) * 100
            shares_bought = self.investment_per_stock / purchase_price
            current_value = shares_bought * current_price
            profit_loss = current_value - self.investment_per_stock
            
            total_invested += self.investment_per_stock
            total_current_value += current_value
            
            portfolio_data.append({
                'symbol': symbol,
                'purchase_price': purchase_price,
                'current_price': current_price,
                'change_percent': change_percent,
                'investment': self.investment_per_stock,
                'current_value': current_value,
                'profit_loss': profit_loss,
                'shares': shares_bought
            })
        
        # ביצועי מדדים
        benchmark_data = []
        for symbol, name in self.benchmarks.items():
            if symbol not in purchase_prices or symbol not in current_prices:
                continue
                
            purchase_price = purchase_prices[symbol]
            current_price = current_prices[symbol]
            
            shares_bought = self.investment_per_stock / purchase_price
            current_value = shares_bought * current_price
            return_percent = ((current_value - self.investment_per_stock) / self.investment_per_stock) * 100
            
            benchmark_data.append({
                'symbol': symbol,
                'name': name,
                'purchase_price': purchase_price,
                'current_price': current_price,
                'current_value': current_value,
                'return_percent': return_percent
            })
        
        # תשואת התיק הכללית
        portfolio_return = ((total_current_value - total_invested) / total_invested) * 100 if total_invested > 0 else 0
        
        return {
            'portfolio': portfolio_data,
            'benchmarks': benchmark_data,
            'summary': {
                'total_invested': total_invested,
                'total_current_value': total_current_value,
