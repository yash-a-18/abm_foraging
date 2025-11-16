from mesa import Agent
from config import (
    STARTING_ENERGY,
    DAILY_REQUIREMENT,
    MAX_WEAK_DAYS,
    ACTIVITY_COSTS,
    RESOURCE_DEFS,
)
from resources import sample_resource_return
import random

class ResourcePatch(Agent):
    """
    ResourcePatch is an agent-like object on the grid representing
    a single resource 'patch'.
    """
    def __init__(self, unique_id, model, resource_type):
        super().__init__(unique_id, model)
        self.resource_type = resource_type
        self.definition = RESOURCE_DEFS[resource_type]
        self.amount = 1  # simple: 1 package per patch

    def step(self):
        return  # passive for now


class ForagerAgent(Agent):
    """
    Main human agent.
    """
    def __init__(self, unique_id, model, name, foraging_skill=1, hunting_skill=1):
        super().__init__(unique_id, model)
        self.name = name
        self.energy = STARTING_ENERGY
        self.foraging_skill = int(foraging_skill)
        self.hunting_skill = int(hunting_skill)
        self.weak_days = 0
        self.status = "healthy"
        self.injury_days_remaining = 0
        self.days_alive = 0

    def is_alive(self):
        return self.status != "dead"

    def step(self):
        if not self.is_alive():
            return

        if self.status == "injured":
            self.handle_injury_day()
            self.consume_daily()
            self.days_alive += 1
            return

        activity = random.choice(self.model.activities)
        self.attempt_activity(activity)
        self.consume_daily()
        self.update_survival_status()
        self.days_alive += 1

    def handle_injury_day(self):
        if self.injury_days_remaining > 0:
            self.injury_days_remaining -= 1
        if self.injury_days_remaining <= 0:
            self.status = "healthy" if self.energy >= self.model.daily_requirement else "weak"

    def attempt_activity(self, activity):
        activity_cost = ACTIVITY_COSTS.get(activity, 0)
        self.energy -= activity_cost
        self.random_move()

        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        resource_patch = None
        for obj in cell_contents:
            if isinstance(obj, ResourcePatch) and obj.resource_type == activity and obj.amount > 0:
                resource_patch = obj
                break

        if resource_patch is None:
            return

        req = resource_patch.definition["skill_required"]
        skill = self.foraging_skill if activity == "plants" else self.hunting_skill
        if skill < req:
            return

        gained = sample_resource_return(activity)
        weak_multiplier = 0.5 if self.status == "weak" else 1.0
        gained *= weak_multiplier
        self.energy += gained
        resource_patch.amount = max(0, resource_patch.amount - 1)

        rdef = resource_patch.definition
        rnd = self.random.random()
        if rnd < rdef["risk_death"]:
            self.die()
        elif rnd < (rdef["risk_death"] + rdef["risk_injury"]):
            self.become_injured(rdef.get("injury_days", 1))

    def consume_daily(self):
        self.energy -= self.model.daily_requirement

    def update_survival_status(self):
        if self.energy < self.model.daily_requirement:
            self.weak_days += 1
            if self.weak_days > self.model.max_weak_days:
                self.die()
            else:
                self.status = "weak"
        else:
            self.weak_days = 0
            if self.status != "injured":
                self.status = "healthy"

    def die(self):
        self.status = "dead"
        try:
            self.model.grid.remove_agent(self)
        except Exception:
            pass

    def become_injured(self, days):
        self.status = "injured"
        self.injury_days_remaining = max(1, days)

    def random_move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False, radius=1
        )
        if len(possible_steps) > 0:
            new_pos = self.random.choice(possible_steps)
            self.model.grid.move_agent(self, new_pos)
