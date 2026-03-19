# Real-Time Stock Market Data Pipeline

A high-frequency financial data engineering project. This system streams live trade data from WebSockets into a KRaft-based Apache Kafka cluster, providing real-time portfolio valuation and automated email alerts.

## 🛠️ Tech Stack

- Language: Python 3.11+
- Message Broker: Apache Kafka 4.2.0 (KRaft Mode - No Zookeeper)
- Data Source: Finnhub.io Real-time WebSockets
- Alerting: SMTP (Gmail/TLS) with ssl context

## 🏗️ Architecture

### Producer (`producer.py`)
- Connects to Finnhub WebSockets
- Filters for specific tickers: `NVDA`, `AAPL`, `TSLA`
- Publishes JSON trade packets with high-precision timestamps to Kafka topic `market-ticks`

### Kafka Broker
- Acts as distributed message buffer
- Uses modern KRaft consensus protocol

### Consumer (`alert_consumer.py`)
- Tracks a live "Fake Portfolio"
- Calculates real-time Total Value and Profit/Loss (P/L)
- Triggers an enhanced email alert (snapshot stats included) when price hits user-defined threshold

## 🚀 Setup & Installation

### 1. Download Apache Kafka
- Source: Apache Kafka Official Downloads
- Version: Kafka 4.2.0, Scala 2.13 (e.g., `kafka_2.13-4.2.0.tgz`)
- Extract to a simple path like `C:\kafka_2.13-4.2.0\`

### 2. Initialize Kafka (KRaft Mode)

Open PowerShell in `Kafka\bin\windows` and run:

1. Generate a Cluster ID:

```powershell
$KAFKA_CLUSTER_ID = .\kafka-storage.bat random-uuid
echo $KAFKA_CLUSTER_ID
```

2. Format storage:

```powershell
.\kafka-storage.bat format --standalone -t $KAFKA_CLUSTER_ID -c C:\kafka_2.13-4.2.0\config\server.properties
```

3. Start broker:

```powershell
.\kafka-server-start.bat C:\kafka_2.13-4.2.0\config\server.properties
```

4. Create topic (new terminal):

```powershell
.\kafka-topics.bat --create --topic market-ticks --bootstrap-server localhost:9092
```

### 3. Python Environment Setup

```bash
git clone https://github.com/Srini1024/kafka-stock-prices-alert-system.git
cd kafka-stock-prices-alert-system
pip install -r requirements.txt
```

Create `.env` in repo root:

```ini
FINNHUB_API_KEY=your_api_key_here
SENDER_EMAIL=your_gmail@gmail.com
EMAIL_PASSWORD=your_16_char_app_password
RECEIVER_EMAIL=your_gmail@gmail.com
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

## 📊 Running the System

1. Start Kafka Broker (from step 2.3)
2. Launch Producer: `python producer.py`
3. Launch Consumer: `python alert_consumer.py`

## 👨‍💻 Project Highlights

- KRaft Mode: modern Kafka architecture, no Zookeeper required
- Latency Tracking: includes high-precision timestamps
- Enhanced Alerts: rich email notifications with portfolio snapshots
- Security: `.gitignore` includes sensitive credential files
