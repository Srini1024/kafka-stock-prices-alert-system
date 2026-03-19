import os
import json
import smtplib
import time
import ssl
from email.message import EmailMessage
from dotenv import load_dotenv
from kafka import KafkaConsumer

load_dotenv()

SENDER = os.getenv("SENDER_EMAIL")
PASSWORD = os.getenv("EMAIL_PASSWORD")
RECEIVER = os.getenv("RECEIVER_EMAIL")
BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")

portfolio = {
    "NVDA": {"shares": 10, "buy_price": 178.62, "current_price": 178.62, "alert_at": 179.00},
    "AAPL": {"shares": 5, "buy_price": 248.97, "current_price": 248.97, "alert_at": 249.38},
    "TSLA": {"shares": 2, "buy_price": 380.24, "current_price": 380.24, "alert_at": 382.00}
}

COOLDOWN = 300 
last_alert_time = {symbol: 0 for symbol in portfolio.keys()}

def send_alert(symbol, price, total_value, total_gain):
    global last_alert_time
    if time.time() - last_alert_time[symbol] < COOLDOWN:
        return

    email_body = f"""
    ⚠️ STOCK ALERT: {symbol} THRESHOLD REACHED
    -----------------------------------------
    Last Trade: ${price:.2f}
    Your Limit: ${portfolio[symbol]['alert_at']:.2f}
    
    📊 PORTFOLIO SNAPSHOT AT TIME OF ALERT:
    -----------------------------------------
    Total Portfolio Value: ${total_value:,.2f}
    Total Profit/Loss:     ${total_gain:+.2f}
    
    Action Required: Check your trading strategy for {symbol}.
    """

    msg = EmailMessage()
    msg.set_content(email_body)
    msg['Subject'] = f"🚨 ALERT: {symbol} @ ${price:.2f} (P/L: ${total_gain:+.2f})"
    msg['From'] = SENDER
    msg['To'] = RECEIVER
    
    context = ssl.create_default_context()

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls(context=context)
            smtp.login(SENDER, PASSWORD)
            smtp.send_message(msg)
            print(f"\n📧 ENHANCED Email sent for {symbol} with P/L stats!")
            last_alert_time[symbol] = time.time()
    except Exception as e:
        print(f"\n❌ Email failed: {e}")

consumer = KafkaConsumer(
    'market-ticks',
    bootstrap_servers=[BOOTSTRAP_SERVERS],
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    auto_offset_reset='latest'
)

print(f" Master Tracker Live | Watching: {', '.join(portfolio.keys())}")

try:
    for message in consumer:
        trade = message.value
        sym = trade.get('symbol')
        price = trade.get('price')

        if sym in portfolio:
            portfolio[sym]['current_price'] = price
    
            if price <= portfolio[sym]['alert_at']:
                send_alert(sym, price)

            total_value = sum(s['shares'] * s['current_price'] for s in portfolio.values())
            total_gain = sum((s['current_price'] - s['buy_price']) * s['shares'] for s in portfolio.values())
    
            status = f"💰 Portfolio: ${total_value:,.2f} | P/L: ${total_gain:+.2f} | Last Tick: {sym} @ ${price:.2f}"
            print(f"\r{status}", end="", flush=True)

except KeyboardInterrupt:
    print("\nShutting down...")
finally:
    consumer.close()