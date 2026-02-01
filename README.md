# ABM Foraging Simulation: Survival & Logistics

This simulation models ancestral foraging behaviors where survival depends on balancing energy risk and reward.

## Core Simulation Logic
* **Physical Resources**: Food (Plants, Small Game, Large Game) are physical objects on the grid. Once an agent "harvests" one, it is removed from the map.
* **Injury & Recovery**: High-risk hunts (Large Game) can result in injury. Injured agents enter a "Rest" state, staying in place and consuming 50% less energy to recover.
* **Survival Decisions**: Agents evaluate their energy. If energy is low (<800), they pivot to "Survival Mode," searching only for low-risk plants.

## How to Run
1. Install dependencies: `pip install mesa pandas`.
2. Launch the UI: `python run.py`.
3. View the simulation at `http://127.0.0.1:8521`.

## Analyzing the "Why" (Logs)
Open `simulation_log.csv` to see:
* **Reasoning**: Why an agent chose a specific resource (e.g., "Starving. Looking for safe plants").
* **DeathCause**: Why an agent died (e.g., "Killed by large_game" or "Starvation").

Food patch → square

Water patch → triangle

Different colors (e.g., brown for food, blue for water)