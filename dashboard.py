import streamlit as st
from kafka import KafkaConsumer
import json
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

st.set_page_config(page_title="Pro Trader Dashboard", layout="wide")
st.title("🏛️ High-Frequency Portfolio Monitor")

PORTFOLIO = {
    "NVDA": {"shares": 10, "buy_price": 178.62, "alert_at": 175.00},
    "AAPL": {"shares": 5, "buy_price": 248.97, "alert_at": 247.38},
    "TSLA": {"shares": 2, "buy_price": 380.24, "alert_at": 370.00}
}


if 'data' not in st.session_state:
    st.session_state.data = []
if 'prices' not in st.session_state:
    st.session_state.prices = {s: v['buy_price'] for s, v in PORTFOLIO.items()}

def create_consumer():
    return KafkaConsumer(
        'market-ticks',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='latest',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )


head1, head2 = st.columns(2)
total_val_slot = head1.empty()
total_pl_slot = head2.empty()

st.markdown("---")

col1, col2, col3 = st.columns(3)
ui_slots = {}
for sym, col in zip(PORTFOLIO.keys(), [col1, col2, col3]):
    with col:
        st.subheader(f"{sym} Analysis")
        ui_slots[sym] = {
            "metric": st.empty(),
            "chart": st.empty()
        }

st.markdown("---")
st.subheader("📋 Recent Transaction Log (Live Kafka Feed)")
table_placeholder = st.empty()

consumer = create_consumer()

for message in consumer:
    tick = message.value
    
    try:
        symbol = tick.get('symbol')
        price = tick.get('price')
        
        if symbol and price:
            time_str = datetime.now().strftime('%H:%M:%S')
            st.session_state.prices[symbol] = price

           
            current_total = sum(st.session_state.prices[s] * PORTFOLIO[s]['shares'] for s in PORTFOLIO)
            initial_cost = sum(PORTFOLIO[s]['buy_price'] * PORTFOLIO[s]['shares'] for s in PORTFOLIO)
            net_pl = current_total - initial_cost
            
          
            total_val_slot.metric("Net Portfolio Value", f"${current_total:,.2f}")
        
            total_pl_slot.metric(
                "Total Unrealized P/L", 
                f"${net_pl:,.2f}", 
                delta=f"{net_pl:+.2f}", 
                delta_color="normal"
            )

            stock_pl = (price - PORTFOLIO[symbol]['buy_price']) * PORTFOLIO[symbol]['shares']
            
        
            ui_slots[symbol]["metric"].metric(
                label=f"Current {symbol}", 
                value=f"${price:.2f}", 
                delta=f"{stock_pl:+.2f}", 
                delta_color="normal"
            )


            st.session_state.data.insert(0, {"Time": time_str, "Symbol": symbol, "Price": price})
            st.session_state.data = st.session_state.data[:60] 
            
            df = pd.DataFrame(st.session_state.data)
            
            for sym in PORTFOLIO.keys():
                symbol_df = df[df['Symbol'] == sym].sort_values("Time")
                if not symbol_df.empty:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=symbol_df['Time'], y=symbol_df['Price'], name='Price', line=dict(color='#1f77b4', width=3)))
                    fig.add_hline(y=PORTFOLIO[sym]['alert_at'], line_dash="dash", line_color="red", annotation_text="ALERT", annotation_position="top left")
                    fig.update_layout(height=300, margin=dict(l=0, r=0, t=20, b=0), showlegend=False)
                    ui_slots[sym]["chart"].plotly_chart(fig, use_container_width=True)
            
            table_placeholder.table(df.head(10))

    except Exception as e:
        continue