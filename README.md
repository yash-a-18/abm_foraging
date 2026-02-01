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

**Why Reasoning Differs on Hover**
You may see an agent standing on a plant while its reasoning says "Hunting small_game" due to the following execution order in agents.py:

1. **Target Selection:** At the start of a step, the agent chooses a target based on its current energy (e.g., if energy is high, it randomly picks between "plants," "small_game," or "large_game").
2. **Movement:** The agent moves to a new random neighboring cell before checking for food.
3. **Interaction:** Once moved, the agent only attempts to harvest if the resource in its current cell matches its pre-selected target.

If an agent chooses to hunt "small_game" but moves into a cell containing "plants," it will not harvest those plants. It simply stands there with the reasoning "Hunting small_game," waiting for the next step to move again.

---
## Step-by-Step Logic of the Code
**1. Single Agent Simulation**
   
For a single agent, a single "step" follows this linear path:

   * **Initialization:** The agent starts with 3000 energy and is placed randomly on the grid.

   * **Health Check:** If the agent is injured, it skips movement and foraging to rest, consuming 50% less energy until healed.

   * **Decision Making:**

     * **Survival Mode:** If energy is < 800, the agent's reasoning becomes "Starving. Looking for safe plants only".

     * **Opportunistic Mode:** If energy is high, it randomly picks any resource type to hunt.

   * **Finding & Harvesting:**

     * The agent moves one step.

     * It looks at its current cell. If a ResourcePatch matching its target is there, it attempts a harvest.

     * **Harvest Risks:** Hunting carries a defined risk of injury or death. If successful, energy is added based on a normal distribution; if unsuccessful, the agent might die or become injured.

   * **Metabolism:** At the end of every step, the daily_requirement (50 energy) is subtracted. If energy hits 0, the agent dies of "Starvation".

**2. Multiple Agents Simulation**

When multiple agents are involved, the ForageModel manages the environment and synchronization:

   * **Environment Setup:** The model fills the 10x10 grid with initial resource patches based on spawn probabilities.

   * **Concurrent Steps:** The model uses RandomActivation, meaning in every step, it picks agents one by one in a random order to perform their individual "step" logic described above.

   * **Competition (Resource Disappearance):** Because resources disappear after consumption, multiple agents often compete for the same food. If Agent A consumes a "small_game" patch, it is removed from the grid immediately, so Agent B arriving in the same cell later in the same step will find nothing.

   * **Resource Replenishment:** At the start of every global step, the model attempts to spawn new resources in empty cells, simulating nature's regrowth.

   * **Data Logging:** The model records every agent's status, energy, and reasoning into a CSV file and a UI history list at the end of each step, allowing you to track the population's survival over time.