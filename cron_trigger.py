from flask import Flask, request
import subprocess
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
SECRET_KEY = os.getenv("CRON_SECRET_KEY")  

@app.route("/trigger-email", methods=["GET"])
def trigger_email():
    key = request.args.get("key")
    if key != SECRET_KEY:
        return "❌ Unauthorized", 403

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"🚀 Trigger received at {timestamp}")

    # Run emailer script in background (non-blocking)
    subprocess.Popen(["poetry", "run", "python", "emailer.py"])
    return f"✅ Email triggered at {timestamp}", 200

@app.route("/")
def healthcheck():
    return "🟢 Cron trigger app is running"

if __name__ == "__main__":
    app.run(debug=True)
