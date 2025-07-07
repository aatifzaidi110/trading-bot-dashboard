# run_all.py

import subprocess
import time
import os

# === Step 1: Run generate_bot.py to create structure if needed ===
print("🛠 Generating base folders and files...")
subprocess.run(["python", "generate_bot.py"])

# === Step 2: Run scanner to create scan_results.json ===
print("🔍 Scanning top tickers...")
scan_script = os.path.join("core", "scripts", "scan_top_tickers.py")
if os.path.exists(scan_script):
    subprocess.run(["python", scan_script, "--tickers", "15"])
else:
    print("⚠️  Skipping scanner - script not found.")

# Optional: Sleep to allow scan to finish writing files
time.sleep(2)

# === Step 3: Launch Streamlit dashboard ===
print("📊 Launching Streamlit dashboard...")
dashboard_path = os.path.join("core", "streamlit_app", "dashboard.py")
subprocess.run(["streamlit", "run", dashboard_path])
