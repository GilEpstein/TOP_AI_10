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
                'total_profit_loss': total_current_value - total_invested,
                'portfolio_return': portfolio_return
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def save_data(self, data):
        """שומר נתונים לקובץ JSON"""
        os.makedirs('data', exist_ok=True)
        
        # שמירת נתונים עכשוויים
        with open('data/latest_report.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # שמירת היסטוריה
        history_file = 'data/portfolio_history.json'
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        else:
            history = []
        
        history.append({
            'date': data['timestamp'],
            'portfolio_return': data['summary']['portfolio_return'],
            'total_value': data['summary']['total_current_value'],
            'benchmarks': {b['symbol']: b['return_percent'] for b in data['benchmarks']}
        })
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    
    def generate_html_report(self, data):
        """יוצר דוח HTML יפה"""
        
        html_template = """
<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TOP AI 10 - דוח תיק מניות</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .section { padding: 30px; border-bottom: 1px solid #eee; }
        .section:last-child { border-bottom: none; }
        .section-title {
            font-size: 1.8em;
            margin-bottom: 20px;
            color: #2c3e50;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .portfolio-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .portfolio-table th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: center;
            font-weight: 600;
        }
        .portfolio-table td {
            padding: 12px;
            text-align: center;
            border-bottom: 1px solid #eee;
            transition: background-color 0.3s ease;
        }
        .portfolio-table tbody tr:hover { background-color: #f8f9ff; }
        .profit { color: #27ae60; font-weight: bold; }
        .loss { color: #e74c3c; font-weight: bold; }
        .neutral { color: #f39c12; font-weight: bold; }
        .summary-box {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            margin: 20px 0;
            text-align: center;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }
        .summary-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .stat-item {
            background: rgba(255,255,255,0.2);
            padding: 15px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }
        .stat-value { font-size: 1.3em; font-weight: bold; margin-top: 5px; }
        .benchmark-section {
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
        }
        .comparison-section {
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
        }
        .comparison-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid rgba(0,0,0,0.1);
        }
        .comparison-item:last-child { border-bottom: none; }
        .winner {
            background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
            padding: 5px 10px;
            border-radius: 20px;
            color: #2c3e50;
            font-weight: bold;
            font-size: 0.9em;
        }
        .loser {
            background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
            padding: 5px 10px;
            border-radius: 20px;
            color: #2c3e50;
            font-weight: bold;
            font-size: 0.9em;
        }
        .update-time {
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 TOP AI 10 - דוח תיק מניות</h1>
            <p>עדכון אחרון: {{ timestamp_formatted }}</p>
        </div>

        <div class="section">
            <h2 class="section-title">🎯 ביצועי התיק האישי</h2>
            <table class="portfolio-table">
                <thead>
                    <tr>
                        <th>סימול</th>
                        <th>מחיר קנייה</th>
                        <th>מחיר נוכחי</th>
                        <th>שינוי %</th>
                        <th>השקעה</th>
                        <th>ערך נוכחי</th>
                        <th>רווח/הפסד</th>
                    </tr>
                </thead>
                <tbody>
                    {% for stock in portfolio %}
                    <tr>
                        <td><strong>{{ stock.symbol }}</strong></td>
                        <td>${{ "%.2f"|format(stock.purchase_price) }}</td>
                        <td>${{ "%.2f"|format(stock.current_price) }}</td>
                        <td class="{% if stock.change_percent > 5 %}profit{% elif stock.change_percent < -5 %}loss{% else %}neutral{% endif %}">
                            {{ "{:+.1f}%"|format(stock.change_percent) }}
                        </td>
                        <td>${{ stock.investment }}</td>
                        <td>${{ "%.2f"|format(stock.current_value) }}</td>
                        <td class="{% if stock.profit_loss > 0 %}profit{% elif stock.profit_loss < 0 %}loss{% else %}neutral{% endif %}">
                            {{ "${:+.2f}"|format(stock.profit_loss) }}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="section">
            <div class="summary-box">
                <h3>💰 סיכום התיק</h3>
                <div class="summary-stats">
                    <div class="stat-item">
                        <div>סה"כ השקעה</div>
                        <div class="stat-value">${{ "{:,.2f}"|format(summary.total_invested) }}</div>
                    </div>
                    <div class="stat-item">
                        <div>ערך נוכחי</div>
                        <div class="stat-value">${{ "{:,.2f}"|format(summary.total_current_value) }}</div>
                    </div>
                    <div class="stat-item">
                        <div>רווח/הפסד</div>
                        <div class="stat-value {% if summary.total_profit_loss > 0 %}profit{% else %}loss{% endif %}">
                            {{ "${:+,.2f}"|format(summary.total_profit_loss) }}
                        </div>
                    </div>
                    <div class="stat-item">
                        <div>תשואה כללית</div>
                        <div class="stat-value {% if summary.portfolio_return > 0 %}profit{% else %}loss{% endif %}">
                            {{ "{:+.1f}%"|format(summary.portfolio_return) }}
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">📈 השוואה למדדים</h2>
            <div class="benchmark-section">
                <table class="portfolio-table">
                    <thead>
                        <tr>
                            <th>מדד</th>
                            <th>מחיר קנייה</th>
                            <th>מחיר נוכחי</th>
                            <th>ערך נוכחי</th>
                            <th>תשואה %</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for benchmark in benchmarks %}
                        <tr>
                            <td><strong>{{ benchmark.symbol }}</strong><br><small>{{ benchmark.name }}</small></td>
                            <td>${{ "%.2f"|format(benchmark.purchase_price) }}</td>
                            <td>${{ "%.2f"|format(benchmark.current_price) }}</td>
                            <td>${{ "%.2f"|format(benchmark.current_value) }}</td>
                            <td class="{% if benchmark.return_percent > 0 %}profit{% else %}loss{% endif %}">
                                {{ "{:+.1f}%"|format(benchmark.return_percent) }}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">🏆 סיכום השוואתי</h2>
            <div class="comparison-section">
                <div class="comparison-item">
                    <div><strong>TOP AI 10:</strong> 
                        <span class="{% if summary.portfolio_return > 0 %}profit{% else %}loss{% endif %}">
                            {{ "{:+.1f}%"|format(summary.portfolio_return) }}
                        </span>
                    </div>
                    <div>🤖</div>
                </div>
                
                {% for benchmark in benchmarks %}
                <div class="comparison-item">
                    <div><strong>{{ benchmark.name }} ({{ benchmark.symbol }}):</strong> 
                        <span class="{% if benchmark.return_percent > 0 %}profit{% else %}loss{% endif %}">
                            {{ "{:+.1f}%"|format(benchmark.return_percent) }}
                        </span>
                    </div>
                    <div class="{% if summary.portfolio_return > benchmark.return_percent %}winner{% else %}loser{% endif %}">
                        {% if summary.portfolio_return > benchmark.return_percent %}
                        TOP AI 10 מנצח! 🚀
                        {% else %}
                        המדד טוב יותר 📉
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <div class="section" style="text-align: center; border-bottom: none;">
            <p class="update-time">
                ✅ הדוח הושלם בהצלחה! הרצה הבאה: 1 לחודש הבא ב-23:10
            </p>
        </div>
    </div>
</body>
</html>
        """
        
        template = Template(html_template)
        
        # פורמט תאריך יפה
        timestamp_formatted = datetime.now().strftime('%d/%m/%Y %H:%M')
        
        html_content = template.render(
            portfolio=data['portfolio'],
            benchmarks=data['benchmarks'],
            summary=data['summary'],
            timestamp_formatted=timestamp_formatted
        )
        
        # שמירת קובץ HTML
        os.makedirs('docs', exist_ok=True)
        with open('docs/index.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("✅ דוח HTML נוצר בהצלחה!")

def main():
    """הפונקציה הראשית"""
    print("🚀 מתחיל יצירת דוח תיק TOP AI 10...")
    
    tracker = AdvancedPortfolioTracker()
    
    try:
        # חישוב נתונים
        data = tracker.calculate_performance_data()
        
        if data is None:
            print("❌ שגיאה בחישוב נתונים")
            return
        
        # שמירת נתונים
        tracker.save_data(data)
        print("✅ נתונים נשמרו")
        
        # יצירת דוח HTML
        tracker.generate_html_report(data)
        print("✅ דוח HTML נוצר")
        
        # הדפסת סיכום
        summary = data['summary']
        print(f"\n📊 סיכום מהיר:")
        print(f"   💰 השקעה כוללת: ${summary['total_invested']:,.2f}")
        print(f"   📈 ערך נוכחי: ${summary['total_current_value']:,.2f}")
        print(f"   🎯 תשואה: {summary['portfolio_return']:+.1f}%")
        
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
