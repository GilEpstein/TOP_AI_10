import pandas as pd
import yfinance as yf
import json
from datetime import datetime, timedelta
import os

def get_stock_data(symbol, period="1mo"):
    """מקבל נתוני מניה"""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        current_price = data['Close'].iloc[-1]
        previous_price = data['Close'].iloc[0]
        change = current_price - previous_price
        change_percent = (change / previous_price) * 100
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'change': change,
            'change_percent': change_percent
        }
    except Exception as e:
        print(f"שגיאה בקבלת נתונים עבור {symbol}: {e}")
        return None

def load_portfolio():
    """טוען את התיק מהקובץ"""
    try:
        with open('data/portfolio.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("קובץ התיק לא נמצא")
        return {}

def generate_html_report(portfolio_data, market_data):
    """יוצר דוח HTML מעוצב"""
    
    # חישוב סיכום כללי
    total_value = sum(stock['value'] for stock in portfolio_data.values())
    total_cost = sum(stock['cost'] for stock in portfolio_data.values())
    total_profit = total_value - total_cost
    total_profit_percent = (total_profit / total_cost) * 100 if total_cost > 0 else 0
    
    # תאריך נוכחי בעברית
    current_date = datetime.now()
    hebrew_months = {
        1: 'ינואר', 2: 'פברואר', 3: 'מרץ', 4: 'אפריל',
        5: 'מאי', 6: 'יוני', 7: 'יולי', 8: 'אוגוסט',
        9: 'ספטמבר', 10: 'אוקטובר', 11: 'נובמבר', 12: 'דצמבר'
    }
    hebrew_date = f"{current_date.day} {hebrew_months[current_date.month]} {current_date.year}"
    
    html = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="he">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>דוח תיק השקעות - {hebrew_date}</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
                direction: rtl;
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
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                color: white;
                padding: 40px;
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
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="75" cy="75" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="50" cy="10" r="0.5" fill="rgba(255,255,255,0.1)"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
                opacity: 0.3;
            }}
            
            .header h1 {{
                font-size: 2.5em;
                margin-bottom: 10px;
                position: relative;
                z-index: 1;
            }}
            
            .header .subtitle {{
                font-size: 1.2em;
                opacity: 0.9;
                position: relative;
                z-index: 1;
            }}
            
            .summary-section {{
                padding: 50px 40px;
                text-align: center;
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                border-bottom: 2px solid #dee2e6;
            }}
            
            .summary-title {{
                font-size: 2.5em;
                color: #2c3e50;
                margin-bottom: 40px;
                font-weight: 800;
            }}
            
            .summary-cards {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 30px;
                max-width: 1000px;
                margin: 0 auto;
            }}
            
            .summary-card {{
                background: white;
                padding: 35px;
                border-radius: 20px;
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
                border: 2px solid #f1f3f4;
                transition: all 0.3s ease;
            }}
            
            .summary-card:hover {{
                transform: translateY(-10px);
                box-shadow: 0 25px 50px rgba(0,0,0,0.15);
                border-color: #667eea;
            }}
            
            .summary-card h3 {{
                font-size: 1.1em;
                color: #6c757d;
                margin-bottom: 20px;
                text-transform: uppercase;
                letter-spacing: 1.5px;
                font-weight: 700;
            }}
            
            .summary-card .value {{
                font-size: 2.3em;
                font-weight: 800;
                margin-bottom: 10px;
                direction: ltr;
                text-align: center;
            }}
            
            .summary-card .profit {{
                font-size: 1.4em;
                font-weight: 700;
                direction: ltr;
                text-align: center;
            }}
            
            .profit-positive {{
                color: #10b981 !important;
            }}
            
            .profit-negative {{
                color: #ef4444 !important;
            }}
            
            .profit-neutral {{
                color: #6b7280 !important;
            }}
            
            .section {{
                padding: 50px 40px;
            }}
            
            .section-title {{
                font-size: 2em;
                color: #2c3e50;
                margin-bottom: 40px;
                text-align: center;
                font-weight: 700;
                position: relative;
            }}
            
            .section-title::after {{
                content: '';
                position: absolute;
                bottom: -15px;
                left: 50%;
                transform: translateX(-50%);
                width: 100px;
                height: 4px;
                background: linear-gradient(90deg, #667eea, #764ba2);
                border-radius: 2px;
            }}
            
            .market-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 25px;
                margin-bottom: 30px;
            }}
            
            .market-item {{
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 8px 25px rgba(0,0,0,0.08);
                border: 2px solid #f1f3f4;
                display: flex;
                justify-content: space-between;
                align-items: center;
                transition: all 0.3s ease;
            }}
            
            .market-item:hover {{
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(0,0,0,0.12);
                border-color: #667eea;
            }}
            
            .market-name {{
                font-weight: 700;
                color: #2c3e50;
                font-size: 1.2em;
                text-align: right;
            }}
            
            .market-change {{
                font-weight: 800;
                font-size: 1.3em;
                direction: ltr;
                text-align: left;
            }}
            
            .portfolio-table {{
                width: 100%;
                border-collapse: collapse;
                background: white;
                border-radius: 15px;
                overflow: hidden;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                border: 2px solid #f1f3f4;
            }}
            
            .portfolio-table th {{
                background: linear-gradient(135deg, #374151 0%, #4b5563 100%);
                color: white;
                padding: 25px 20px;
                text-align: center;
                font-weight: 700;
                font-size: 1.1em;
                letter-spacing: 1px;
            }}
            
            .portfolio-table td {{
                padding: 20px;
                text-align: center;
                border-bottom: 1px solid #e5e7eb;
                font-size: 1em;
            }}
            
            .portfolio-table tr:hover {{
                background-color: #f9fafb;
            }}
            
            .portfolio-table tr:last-child td {{
                border-bottom: none;
            }}
            
            .stock-symbol {{
                font-weight: 800;
                color: #1f2937;
                font-size: 1.2em;
            }}
            
            .number-cell {{
                direction: ltr;
                text-align: center;
                font-weight: 600;
            }}
            
            .footer {{
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                color: white;
                text-align: center;
                padding: 40px;
                font-size: 1em;
            }}
            
            .footer a {{
                color: #74b9ff;
                text-decoration: none;
            }}
            
            .emoji {{
                font-size: 1.3em;
                margin: 0 8px;
            }}
            
            .date-badge {{
                display: inline-block;
                background: rgba(255,255,255,0.2);
                padding: 10px 20px;
                border-radius: 25px;
                margin-top: 15px;
                font-size: 1em;
                font-weight: 600;
            }}
            
            @media (max-width: 768px) {{
                .summary-cards {{
                    grid-template-columns: 1fr;
                }}
                
                .market-grid {{
                    grid-template-columns: 1fr;
                }}
                
                .portfolio-table {{
                    font-size: 0.85em;
                }}
                
                .portfolio-table th,
                .portfolio-table td {{
                    padding: 15px 10px;
                }}
                
                .header h1 {{
                    font-size: 2em;
                }}
                
                .summary-title {{
                    font-size: 2em;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1><span class="emoji">📊</span>סיכום השקעותי<span class="emoji">🏆</span></h1>
                <div class="subtitle">דוח חודשי מעודכן</div>
                <div class="date-badge">
                    <span class="emoji">📅</span>{hebrew_date}
                </div>
            </div>
            
            <div class="summary-section">
                <h2 class="summary-title">סיכום התיק</h2>
                <div class="summary-cards">
                    <div class="summary-card">
                        <h3>הערך הנוכחי</h3>
                        <div class="value">${total_value:,.2f}</div>
                    </div>
                    <div class="summary-card">
                        <h3>עלות רכישה</h3>
                        <div class="value">${total_cost:,.2f}</div>
                    </div>
                    <div class="summary-card">
                        <h3>רווח/הפסד</h3>
                        <div class="value profit-{'positive' if total_profit >= 0 else 'negative'}">${total_profit:+,.2f}</div>
                        <div class="profit profit-{'positive' if total_profit_percent >= 0 else 'negative'}">
                            {total_profit_percent:+.2f}%
                        </div>
                    </div>
                </div>
            </div>
    """
    
    # הוספת מדדי השוק
    html += f"""
            <div class="section">
                <h2 class="section-title"><span class="emoji">⚡</span>סיכום השווקים</h2>
                <div class="market-grid">
    """
    
    for name, data in market_data.items():
        change_class = 'profit-positive' if data['change_percent'] >= 0 else 'profit-negative'
        html += f"""
                    <div class="market-item">
                        <div class="market-name">{name}</div>
                        <div class="market-change {change_class}">
                            {data['change_percent']:+.1f}%
                        </div>
                    </div>
        """
    
    html += """
                </div>
            </div>
    """
    
    # הוספת טבלת התיק
    html += f"""
            <div class="section">
                <h2 class="section-title"><span class="emoji">💼</span>פירוט התיק</h2>
                <table class="portfolio-table">
                    <thead>
                        <tr>
                            <th>מניה</th>
                            <th>כמות</th>
                            <th>מחיר ממוצע</th>
                            <th>מחיר נוכחי</th>
                            <th>שווי נוכחי</th>
                            <th>רווח/הפסד</th>
                            <th>אחוז שינוי</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    for symbol, data in portfolio_data.items():
        profit = data['value'] - data['cost']
        profit_percent = (profit / data['cost']) * 100 if data['cost'] > 0 else 0
        profit_class = 'profit-positive' if profit >= 0 else 'profit-negative'
        
        html += f"""
                        <tr>
                            <td class="stock-symbol">{symbol}</td>
                            <td class="number-cell">{data['quantity']:.2f}</td>
                            <td class="number-cell">${data['avg_price']:.2f}</td>
                            <td class="number-cell">${data['current_price']:.2f}</td>
                            <td class="number-cell">${data['value']:.2f}</td>
                            <td class="number-cell {profit_class}">${profit:+.2f}</td>
                            <td class="number-cell {profit_class}">{profit_percent:+.2f}%</td>
                        </tr>
        """
    
    html += f"""
                    </tbody>
                </table>
            </div>
            
            <div class="footer">
                <p>
                    <span class="emoji">🤖</span>
                    דוח זה נוצר אוטומטית על ידי GitHub Actions
                    <span class="emoji">📈</span>
                </p>
                <p>עודכן ב-{datetime.now().strftime('%d/%m/%Y בשעה %H:%M')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def save_data_to_json(portfolio_data, market_data):
    """שומר נתונים לקובץ JSON"""
    data = {
        'timestamp': datetime.now().isoformat(),
        'portfolio': portfolio_data,
        'market': market_data
    }
    
    os.makedirs('data', exist_ok=True)
    with open('data/latest_report.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    """הפונקציה הראשית"""
    print("🚀 מתחיל ליצור דוח תיק השקעות...")
    
    # טעינת התיק
    portfolio = load_portfolio()
    if not portfolio:
        print("❌ לא נמצא תיק השקעות")
        return
    
    # קבלת נתוני מניות
    portfolio_data = {}
    for symbol, details in portfolio.items():
        stock_data = get_stock_data(symbol)
        if stock_data:
            portfolio_data[symbol] = {
                'quantity': details['quantity'],
                'avg_price': details['avg_price'],
                'cost': details['quantity'] * details['avg_price'],
                'current_price': stock_data['current_price'],
                'value': details['quantity'] * stock_data['current_price']
            }
    
    # קבלת נתוני מדדים
    market_indices = {
        'TOP AI 10': 'TQQQ',
        'S&P 500 (SPY)': 'SPY',
        'NASDAQ 100 (QQQ)': 'QQQ',
        'NASDAQ 3x (TQQQ)': 'TQQQ'
    }
    
    market_data = {}
    for name, symbol in market_indices.items():
        data = get_stock_data(symbol)
        if data:
            market_data[name] = data
    
    # יצירת דוח HTML
    html_report = generate_html_report(portfolio_data, market_data)
    
    # שמירת הדוח
    os.makedirs('docs', exist_ok=True)
    with open('docs/index.html', 'w', encoding='utf-8') as f:
        f.write(html_report)
    
    # שמירת נתונים
    save_data_to_json(portfolio_data, market_data)
    
    print("✅ דוח נוצר בהצלחה!")
    print("📁 הדוח נשמר ב: docs/index.html")

if __name__ == "__main__":
    main()
