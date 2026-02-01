from mesa import Agent
import random
import math

class ResourcePatch(Agent):
    """Physical food sources that exist on the grid."""
    def __init__(self, unique_id, model, resource_type):
        super().__init__(unique_id, model)
        self.resource_type = resource_type
        # Resources stay until consumed
        self.amount = 1 

    def step(self):
        # Static resources don't 'act', but we keep the method for Mesa compatibility
        pass

class ForagerAgent(Agent):
    def __init__(self, unique_id, model, name="Agent"):
        super().__init__(unique_id, model)
        self.name = name
        self.energy = 3000
        self.status = "healthy"
        self.injury_days_remaining = 0
        self.cause_of_death = None
        self.reasoning = "Searching for resources."
        # Cumulative consumption tracker
        self.consumption_stats = {
            "plants": 0,
            "small_game": 0,
            "large_game": 0
        }

    def step(self):
        if self.status == "dead":
            return

        # 1. Handle Injury/Recovery
        if self.status == "injured":
            self.injury_days_remaining -= 1
            # Resting: stay in place, 50% energy consumption
            self.energy -= (self.model.daily_requirement * 0.5)
            self.reasoning = f"Recovering from injury. {self.injury_days_remaining} days left."
            
            if self.injury_days_remaining <= 0:
                self.status = "healthy" if self.energy > 500 else "weak"
                self.reasoning = "Healed! Resuming search."
            return

        # 2. Decision Making (Simple logic for 'Older Times')
        # If energy is low, pick the safest option (Plants)
        if self.energy < 800:
            target = "plants"
            self.reasoning = "Starving. Looking for safe plants only."
        else:
            target = random.choice(["plants", "small_game", "large_game"])
            self.reasoning = f"Hunting {target} for high energy yield."

        # 3. Movement & Finding Food
        self.move_to_find()
        
        # 4. Interaction
        self.interact_with_cell(target)

        # 5. Metabolism
        self.energy -= self.model.daily_requirement
        if self.energy <= 0:
            self.die("Starvation")

    def move_to_find(self):
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def interact_with_cell(self, target_type):
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        patch = next((obj for obj in cell_contents if isinstance(obj, ResourcePatch)), None)

        if patch and patch.resource_type == target_type:
            self.attempt_harvest(patch)

    def attempt_harvest(self, patch):
        config = self.model.resource_defs[patch.resource_type]
        roll = random.random()

        if roll < config["risk_death"]:
            self.die(f"Killed by {patch.resource_type}")
        elif roll < config["risk_injury"]:
            self.status = "injured"
            self.injury_days_remaining = config["injury_days"]
            self.reasoning = f"Injured by {patch.resource_type}!"
        else:
            # Success!
            gain = max(0, random.normalvariate(config["mean"], config["variance"]))
            self.energy += gain
            # Increment the count for the specific resource type
            self.consumption_stats[patch.resource_type] += 1
            # Resource disappears after consumption
            self.model.grid.remove_agent(patch)
            self.model.schedule.remove(patch)

    def die(self, reason):
        self.status = "dead"
        self.cause_of_death = reason
        self.reasoning = f"Dead: {reason}"