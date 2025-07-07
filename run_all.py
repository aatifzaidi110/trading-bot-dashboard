# run_all.py

import subprocess
import time
import os

# === Step 1: Activate virtual environment ===
venv_activate = os.path.join("venv", "Scripts", "activate")
print("✅ Activating virtual environment...")
# This step is needed only if run from outside, otherwise skip if already in (venv)

# === Step 2: Run the trading bot ===
print("🤖 Running trading bot...")
subprocess.run(["python", "generate_bot.py"])

# Optional: Sleep to give files time to write
time.sleep(2)

# === Step 3: Launch Streamlit dashboard ===
print("📊 Launching dashboard...")
subprocess.run(["streamlit", "run", "core/streamlit_app/dashboard.py"])
