import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json
import os

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
            'TSM': {'purchase_date': '2025-06-12'},
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
        
        print(f"🔄 מביא נתוני קנייה עבור: {all_symbols}")
        
        try:
            purchase_data = yf.download(all_symbols, start=purchase_date, end=end_date, progress=False)
            print(f"✅ הורד בהצלחה נתונים לתאריך {purchase_date}")
            
            if len(all_symbols) == 1:
                purchase_prices = {all_symbols[0]: float(purchase_data['Close'].iloc[0])}
            else:
                purchase_prices = {}
                for symbol in all_symbols:
                    try:
                        price = float(purchase_data['Close'][symbol].iloc[0])
                        purchase_prices[symbol] = price
                        print(f"✅ {symbol}: ${price:.2f}")
                    except (KeyError, IndexError) as e:
                        print(f"⚠️ לא נמצא נתון עבור {symbol} בתאריך {purchase_date}")
                        # נסה תאריך קודם
                        try:
                            alt_data = yf.download(symbol, start='2025-06-11', end='2025-06-13', progress=False)
                            if not alt_data.empty:
                                price = float(alt_data['Close'].iloc[0])
                                purchase_prices[symbol] = price
                                print(f"✅ {symbol}: ${price:.2f} (מתאריך חלופי)")
                        except Exception:
                            print(f"❌ לא ניתן לקבל נתונים עבור {symbol}")
                            
        except Exception as e:
            print(f"❌ שגיאה בהורדת נתונים: {e}")
            # fallback - נסה תאריך אחר
            try:
                purchase_data = yf.download(all_symbols, start='2025-06-11', end='2025-06-14', progress=False)
                if len(all_symbols) == 1:
                    purchase_prices = {all_symbols[0]: float(purchase_data['Close'].iloc[0])}
                else:
                    purchase_prices = {}
                    for symbol in all_symbols:
                        try:
                            price = float(purchase_data['Close'][symbol].iloc[0])
                            purchase_prices[symbol] = price
                        except:
                            print(f"❌ נכשל גם בתאריך חלופי עבור {symbol}")
            except Exception as fallback_error:
                print(f"❌ שגיאה גם בתאריך חלופי: {fallback_error}")
                return {}
            
        # שמירת מחירי הקנייה לקובץ JSON
        os.makedirs('data', exist_ok=True)
        with open('data/purchase_prices.json', 'w') as f:
            json.dump(purchase_prices, f, indent=2)
            
        print(f"💾 נשמרו מחירי קנייה עבור {len(purchase_prices)} מניות")
        return purchase_prices
    
    def get_current_prices(self):
        """מביא מחירים נוכחיים"""
        all_symbols = list(self.portfolio.keys()) + list(self.benchmarks.keys())
        
        try:
            print(f"🔄 מביא מחירים נוכחיים עבור: {all_symbols}")
            # מביא נתונים אחרונים
            current_data = yf.download(all_symbols, period='5d', interval='1d', progress=False)
            
            if len(all_symbols) == 1:
                current_prices = {all_symbols[0]: float(current_data['Close'].iloc[-1])}
            else:
                current_prices = {}
                for symbol in all_symbols:
                    try:
                        price = float(current_data['Close'][symbol].iloc[-1])
                        current_prices[symbol] = price
                    except (KeyError, IndexError):
                        print(f"⚠️ לא נמצא מחיר נוכחי עבור {symbol}")
                        # נסה להביא את המניה לבד
                        try:
                            single_data = yf.download(symbol, period='5d', progress=False)
                            if not single_data.empty:
                                price = float(single_data['Close'].iloc[-1])
                                current_prices[symbol] = price
                                print(f"✅ {symbol}: ${price:.2f} (הורדה נפרדת)")
                        except Exception:
                            print(f"❌ לא ניתן לקבל מחיר נוכחי עבור {symbol}")
                
            print(f"✅ התקבלו מחירים נוכחיים עבור {len(current_prices)} מניות")
            return current_prices
        except Exception as e:
            print(f"❌ שגיאה בהבאת מחירים נוכחיים: {e}")
            return {}
    
    def load_or_fetch_purchase_prices(self):
        """כופה רענון נתונים - תמיד מביא נתונים טריים"""
        purchase_file = 'data/purchase_prices.json'
        
        # כפה רענון - מחק קובץ ישן אם קיים
        if os.path.exists(purchase_file):
            os.remove(purchase_file)
            print("🗑️ מחק נתונים ישנים לכפיית רענון")
        
        print("🆕 מביא מחירי קנייה מחדש...")
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
        
        print(f"📊 מחשב ביצועים עבור {len(self.portfolio)} מניות")
        
        for symbol in self.portfolio.keys():
            if symbol not in purchase_prices or symbol not in current_prices:
                print(f"⚠️ חסרים נתונים עבור {symbol}")
                continue
                
            purchase_price = float(purchase_prices[symbol])
            current_price = float(current_prices[symbol])
            
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
            
            print(f"✅ {symbol}: ${purchase_price:.2f} → ${current_price:.2f} ({change_percent:+.1f}%)")
        
        # ביצועי מדדים
        benchmark_data = []
        print(f"📈 מחשב ביצועי מדדים")
        
        for symbol, name in self.benchmarks.items():
            if symbol not in purchase_prices or symbol not in current_prices:
                print(f"⚠️ חסרים נתונים עבור מדד {symbol}")
                continue
                
            purchase_price = float(purchase_prices[symbol])
            current_price = float(current_prices[symbol])
            
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
            
            print(f"✅ {name} ({symbol}): {return_percent:+.1f}%")
        
        # תשואת התיק הכללית
        portfolio_return = ((total_current_value - total_invested) / total_invested) * 100 if total_invested > 0 else 0
        
        print(f"💰 סיכום: השקעה ${total_invested:.2f} → ${total_current_value:.2f} ({portfolio_return:+.1f}%)")
        
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
        print(f"💾 שומר נתונים...")
        
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
            
        print(f"✅ נתונים נשמרו בהצלחה")
    
    def generate_html_report(self, data):
        """יוצר דוח HTML מתקדם"""
        
        print(f"🌐 מתחיל יצירת דוח HTML...")
        print(f"📂 נתיב עבודה נוכחי: {os.getcwd()}")
        
        # HTML מתקדם עם כל התכונות
        html_content = f"""<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TOP AI 10 - דוח תיק מניות</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
            margin: 0;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 30px;
            text-align: center;
            position: relative;
        }}
        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="1" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
            opacity: 0.3;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; position: relative; z-index: 1; }}
        .header p {{ font-size: 1.2em; opacity: 0.9; position: relative; z-index: 1; }}
        .section {{ padding: 30px; border-bottom: 1px solid #eee; }}
        .section:last-child {{ border-bottom: none; }}
        .section-title {{
            font-size: 1.8em;
            margin-bottom: 20px;
            color: #2c3e50;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .portfolio-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .portfolio-table th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: center;
            font-weight: 600;
        }}
        .portfolio-table td {{
            padding: 12px;
            text-align: center;
            border-bottom: 1px solid #eee;
            transition: background-color 0.3s ease;
        }}
        .portfolio-table tbody tr:hover {{ background-color: #f8f9ff; }}
        .profit {{ color: #27ae60; font-weight: bold; }}
        .loss {{ color: #e74c3c; font-weight: bold; }}
        .neutral {{ color: #f39c12; font-weight: bold; }}
        .summary-box {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            margin: 20px 0;
            text-align: center;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }}
        .summary-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        .stat-item {{
            background: rgba(255,255,255,0.2);
            padding: 15px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }}
        .stat-value {{ font-size: 1.3em; font-weight: bold; margin-top: 5px; }}
        .benchmark-section {{
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
        }}
        .comparison-section {{
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
        }}
        .comparison-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid rgba(0,0,0,0.1);
        }}
        .comparison-item:last-child {{ border-bottom: none; }}
        .winner {{
            background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
            padding: 5px 10px;
            border-radius: 20px;
            color: #2c3e50;
            font-weight: bold;
            font-size: 0.9em;
        }}
        .loser {{
            background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
            padding: 5px 10px;
            border-radius: 20px;
            color: #2c3e50;
            font-weight: bold;
            font-size: 0.9em;
        }}
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .section {{ animation: fadeInUp 0.6s ease-out; }}
        .update-time {{
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 TOP AI 10 - דוח תיק מניות</h1>
            <p>עדכון אחרון: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        </div>

        <div class="section">
            <h2 class="section-title">🎯 ביצועי התיק האישי <span style="font-size: 1.5em;">💼</span></h2>
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
                <tbody>"""
        
        # הוספת שורות המניות
        for stock in data['portfolio']:
            profit_loss_class = "profit" if stock['profit_loss'] > 0 else "loss" if stock['profit_loss'] < 0 else "neutral"
            change_class = "profit" if stock['change_percent'] > 5 else "loss" if stock['change_percent'] < -5 else "neutral"
            
            html_content += f"""
                    <tr>
                        <td><strong>{stock['symbol']}</strong></td>
                        <td>${stock['purchase_price']:.2f}</td>
                        <td>${stock['current_price']:.2f}</td>
                        <td class="{change_class}">{stock['change_percent']:+.1f}%</td>
                        <td>${stock['investment']}</td>
                        <td>${stock['current_value']:.2f}</td>
                        <td class="{profit_loss_class}">${stock['profit_loss']:+.2f}</td>
                    </tr>"""
        
        html_content += f"""
                </tbody>
            </table>
        </div>

        <div class="section">
            <div class="summary-box">
                <h3>💰 סיכום התיק</h3>
                <div class="summary-stats">
                    <div class="stat-item">
                        <div>סה"כ השקעה</div>
                        <div class="stat-value">${data['summary']['total_invested']:,.2f}</div>
                    </div>
                    <div class="stat-item">
                        <div>ערך נוכחי</div>
                        <div class="stat-value">${data['summary']['total_current_value']:,.2f}</div>
                    </div>
                    <div class="stat-item">
                        <div>רווח/הפסד</div>
                        <div class="stat-value {'profit' if data['summary']['total_profit_loss'] > 0 else 'loss'}">${data['summary']['total_profit_loss']:+,.2f}</div>
                    </div>
                    <div class="stat-item">
                        <div>תשואה כללית</div>
                        <div class="stat-value {'profit' if data['summary']['portfolio_return'] > 0 else 'loss'}">{data['summary']['portfolio_return']:+.1f}%</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">📈 השוואה למדדים <span style="font-size: 1.5em;">📊</span></h2>
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
                    <tbody>"""
        
        # הוספת מדדים
        for benchmark in data['benchmarks']:
            return_class = "profit" if benchmark['return_percent'] > 0 else "loss"
            html_content += f"""
                        <tr>
                            <td><strong>{benchmark['symbol']}</strong><br><small>{benchmark['name']}</small></td>
                            <td>${benchmark['purchase_price']:.2f}</td>
                            <td>${benchmark['current_price']:.2f}</td>
                            <td>${benchmark['current_value']:.2f}</td>
                            <td class="{return_class}">{benchmark['return_percent']:+.1f}%</td>
                        </tr>"""
        
        html_content += """
                    </tbody>
                </table>
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">🏆 סיכום השוואתי <span style="font-size: 1.5em;">⚡</span></h2>
            <div class="comparison-section">
                <div class="comparison-item">
                    <div><strong>TOP AI 10:</strong> 
                        <span class="{}">{:+.1f}%</span>
                    </div>
                    <div style="font-size: 1.5em;">🎯</div>
                </div>""".format(
            "profit" if data['summary']['portfolio_return'] > 0 else "loss",
            data['summary']['portfolio_return']
        )
        
        # השוואה למדדים
        for benchmark in data['benchmarks']:
            comparison_class = "winner" if data['summary']['portfolio_return'] > benchmark['return_percent'] else "loser"
            comparison_text = "TOP AI 10 מנצח! 🚀" if data['summary']['portfolio_return'] > benchmark['return_percent'] else "המדד טוב יותר 📉"
            return_class = "profit" if benchmark['return_percent'] > 0 else "loss"
            
            html_content += f"""
                <div class="comparison-item">
                    <div><strong>{benchmark['name']} ({benchmark['symbol']}):</strong> 
                        <span class="{return_class}">{benchmark['return_percent']:+.1f}%</span>
                    </div>
                    <div class="{comparison_class}">
                        {comparison_text}
                    </div>
                </div>"""
        
        html_content += """
            </div>
        </div>

        <div class="section" style="text-align: center; border-bottom: none;">
            <p class="update-time">
                ✅ הדוח הושלם בהצלחה! הרצה הבאה: 1 לחודש הבא ב-23:10<br>
                <small>מניות: ANET, AVGO, ASML, CEG, CRWD, NVDA, PLTR, TSLA, TSM, VRT</small>
            </p>
        </div>
    </div>
</body>
</html>"""
        
        # שמירת קובץ HTML
        print(f"📁 יוצר תיקיית docs...")
        try:
            os.makedirs('docs', exist_ok=True)
            print(f"✅ תיקיית docs נוצרה")
            
            html_file_path = 'docs/index.html'
            print(f"📄 כותב קובץ HTML ל-{html_file_path}")
            
            with open(html_file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ נוצר קובץ: {html_file_path} ({len(html_content):,} תווים)")
            
            # בדיקה שהקובץ נוצר
            if os.path.exists(html_file_path):
                file_size = os.path.getsize(html_file_path)
                print(f"📂 אומת: הקובץ קיים וגודלו {file_size:,} bytes")
                print(f"📂 תוכן תיקיית docs: {os.listdir('docs')}")
            else:
                print(f"❌ הקובץ לא נוצר!")
            
        except Exception as e:
            print(f"❌ שגיאה ביצירת קובץ HTML: {e}")
            import traceback
            traceback.print_exc()
        
        print("✅ דוח HTML הושלם!")

def main():
    """הפונקציה הראשית"""
    print("🚀 מתחיל יצירת דוח תיק TOP AI 10...")
    
    tracker = AdvancedPortfolioTracker()
    
    try:
        # חישוב נתונים
        print("📊 שלב 1: חישוב נתוני ביצועים...")
        data = tracker.calculate_performance_data()
        
        if data is None:
            print("❌ שגיאה בחישוב נתונים")
            return
        
        # שמירת נתונים
        print("💾 שלב 2: שמירת נתונים...")
        tracker.save_data(data)
        
        # יצירת דוח HTML
        print("🌐 שלב 3: יצירת דוח HTML...")
        tracker.generate_html_report(data)
        
        # הדפסת סיכום
        summary = data['summary']
        print(f"\n📊 סיכום מהיר:")
        print(f"   💰 השקעה כוללת: ${summary['total_invested']:,.2f}")
        print(f"   📈 ערך נוכחי: ${summary['total_current_value']:,.2f}")
        print(f"   🎯 תשואה: {summary['portfolio_return']:+.1f}%")
        print(f"   📈 מספר מניות בתיק: {len(data['portfolio'])}")
        print(f"   📊 מספר מדדים: {len(data['benchmarks'])}")
        
        print(f"\n🎉 התהליך הושלם בהצלחה!")
        
    except Exception as e:
        print(f"❌ שגיאה כללית: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
