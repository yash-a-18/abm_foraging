# log.py
import pandas as pd
from pathlib import Path

# --- DEFINE LOG FILE PATH ---
LOG_PATH = Path(r".\simulation_log.csv")

# Ensure parent folder exists
LOG_PATH.parent.mkdir(exist_ok=True)

# --- INITIAL CSV STRUCTURE ---
# Added "Event" so event-based logging works
sample_data = {
    "RunID": [],
    "Step": [],
    "AgentID": [],
    "Sex": [],
    "Status": [],
    "Energy": [],
    "Activity": [],
    "Position": [],
    "Event": []        # <-- NEW COLUMN
}

df = pd.DataFrame(sample_data)

# Create the CSV file ONLY if it does NOT already exist
if not LOG_PATH.exists():
    df.to_csv(LOG_PATH, index=False)

# Expose LOG_PATH to import from other files
def get_log_path():
    return LOG_PATH
