# log.py
import pandas as pd
from pathlib import Path

# --- DEFINE LOG FILE PATH ---
LOG_PATH = Path(r".\simulation_log.csv")

# Ensure parent folder exists
LOG_PATH.parent.mkdir(exist_ok=True)

# --- INITIAL CSV STRUCTURE ---
# Aligning these exactly with the keys used in model.py record_event
sample_data = {
    "RunID": [],
    "Step": [],
    "AgentID": [],
    "Status": [],
    "Energy": [],
    "Position": [],
    "Event": [],
    "Reasoning": [],     # Matches model.py
    "DeathCause": [],
    "Stats": []
}

df = pd.DataFrame(sample_data)

# Create the CSV file ONLY if it does NOT already exist
if not LOG_PATH.exists():
    df.to_csv(LOG_PATH, index=False)

def get_log_path():
    return LOG_PATH