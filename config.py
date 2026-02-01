# config.py
"""
Editable configuration for the ABM foraging/hunting model.
All defaults chosen for a sensible starter model — edit freely.
"""

# Grid / simulation
GRID_WIDTH = 100
GRID_HEIGHT = 100
INITIAL_POPULATION = 150 # Can be a dunbar number
STEPS_PER_RUN = 200 # 10000 * 365 # Or certain generations (50 generations i.e., 1000-2000 years)
INITIAL_STRATEGY = ["gather", "hunt_small", "hunt_large"] 

# Energy / survival
STARTING_ENERGY = 2000         # initial kcal per agent 
ENERGY_BANK = 5000            # after this threshold, maybe they can reproduce
DAILY_REQUIREMENT = 100       # kcal required per day to avoid becoming weak
MAX_WEAK_DAYS = 10              # number of consecutive days below threshold before death
# Die with starvation or natural death(old age)!

# Shared energy bank b/w 2 agents
# attempt gather get 100 with +/-10 variance (90,110)
# attempt hunt get 90 with +/-50 variance (40,140)

# After every 9 months, we can have a check for reproduction

"""Can be removed for the simulation"""
# Activity energy costs (kcal) -- energy spent while attempting an activity (in addition to daily consumption)
ACTIVITY_COSTS = {
    "plants": 150,
    "small_game": 300,
    "large_game": 600,
}

# Keep the resources constant
# Resource spawn probabilities (per empty cell per step)
RESOURCE_SPAWN_PROBS = {
    "plants": 0.0,
    "small_game": 0.0,
    "large_game": 0.0,
}

# Normal Distribution Parameters for Resource Returns
# Resource type defaults (mean, variance, skill requirement, package size, risk injury, risk death, injury_days)
RESOURCE_DEFS = {
    "plants": {
        "mean": 400,
        "variance": 50,
        "skill_required": 0,
        "package": 400,
        "risk_injury": 0.0,
        "risk_death": 0.0,
        "injury_days": 0,
    },
    "small_game": {
        "mean": 1200,
        "variance": 200,
        "skill_required": 3,
        "package": 1200,
        "risk_injury": 0.05,
        "risk_death": 0.01,
        "injury_days": 2,
    },
    "large_game": {
        "mean": 6000,
        "variance": 1000,
        "skill_required": 7,
        "package": 6000,
        "risk_injury": 0.12,
        "risk_death": 0.04,
        "injury_days": 7,
    },
}

# Activity choices (for UI or agent decision)
ACTIVITIES = ["plants", "small_game", "large_game"]

# Movement
MAX_MOVE_DISTANCE = 1  # how far an agent can step per day (Chebyshev / grid adjacency)

# Visualization / portrayal sizes
AGENT_SIZE = 0.8
RESOURCE_SIZE = 0.9
