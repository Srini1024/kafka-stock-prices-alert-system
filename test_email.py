import smtplib
import ssl
import os 
from dotenv import load_dotenv

load_dotenv()

SENDER = os.getenv("SENDER_EMAIL")
PASSWORD = os.getenv("EMAIL_PASSWORD")
RECEIVER = os.getenv("RECEIVER_EMAIL")

message = f"""Subject: Kafka Test 
From: {SENDER}
To: {RECEIVER}

If you see this, your Gmail and Python are finally friends!"""

print("🚀 Attempting to send test email...")

try:

    context = ssl.create_default_context()
    
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls(context=context) 
        server.login(SENDER, PASSWORD)
        server.sendmail(SENDER, RECEIVER, message)
        
    print("✅ SUCCESS! Check your inbox.")
except Exception as e:
    print(f"❌ STILL FAILING: {e}")