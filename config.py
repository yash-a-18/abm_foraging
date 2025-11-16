# config.py
"""
Editable configuration for the ABM foraging/hunting model.
All defaults chosen for a sensible starter model — edit freely.
"""

# Grid / simulation
GRID_WIDTH = 10
GRID_HEIGHT = 10
INITIAL_POPULATION = 100
STEPS_PER_RUN = 200

# Energy / survival
STARTING_ENERGY = 2000         # initial kcal per agent
DAILY_REQUIREMENT = 2000       # kcal required per day to avoid becoming weak
MAX_WEAK_DAYS = 2              # number of consecutive days below threshold before death

# Activity energy costs (kcal) -- energy spent while attempting an activity (in addition to daily consumption)
ACTIVITY_COSTS = {
    "plants": 150,
    "small_game": 300,
    "large_game": 600,
}

# Resource spawn probabilities (per empty cell per step)
RESOURCE_SPAWN_PROBS = {
    "plants": 0.20,
    "small_game": 0.06,
    "large_game": 0.015,
}

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
