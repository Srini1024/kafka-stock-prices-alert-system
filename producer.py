import websocket
import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from kafka import KafkaProducer


load_dotenv()
API_KEY = os.getenv("FINNHUB_API_KEY")
BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")

if not API_KEY or not BOOTSTRAP_SERVERS:
    print("❌ ERROR: Missing environment variables! Check your .env file.")
    sys.exit(1)\
    
producer = KafkaProducer(
    bootstrap_servers=[BOOTSTRAP_SERVERS],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def on_message(ws, message):
    msg = json.loads(message)
    
    if msg.get('type') == 'trade':
        for trade in msg['data']:
            readable_time = datetime.fromtimestamp(trade['t'] / 1000.0).strftime('%H:%M:%S.%f')[:-3]
            packet = {
                "symbol": trade['s'],
                "price": trade['p'],
                "time": trade['t'],
                "volume": trade['v']
            }
            producer.send("market-ticks", value=packet)
            print(f"[{readable_time}] Sent to Kafka: {packet['symbol']} @ ${packet['price']}")
            
def on_error(ws, error):

    print(f"❌ Connection Error: {error}")

def on_close(ws, close_status_code, close_msg):

    print("Connection Closed. Producer stopping...")
    producer.close()

def on_open(ws):
    print("✅ Securely connected to Finnhub! Subscribing to symbols...")
    
    symbols = ["AAPL", "TSLA", "NVDA"]
    
    for s in symbols:
        ws.send(json.dumps({"type": "subscribe", "symbol": s}))

if __name__ == "__main__":

    websocket_url = f"wss://ws.finnhub.io?token={API_KEY}"
    
    ws = websocket.WebSocketApp(
        websocket_url,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    ws.on_open = on_open
    
    print(f"Producer is starting up... (Watching for trades)")
    ws.run_forever()