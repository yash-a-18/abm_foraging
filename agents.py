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
    def __init__(self, unique_id, model, resource_type):
        super().__init__(unique_id, model)
        self.resource_type = resource_type
        self.definition = RESOURCE_DEFS[resource_type]
        self.amount = 1  # simple: 1 package per patch

    def step(self):
        return  # passive for now


class ForagerAgent(Agent):
    """
    Main forager/hunter agent with event-based logging.
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

        # --- Logging baseline state ---
        self.last_logged_state = {
            "status": self.status,
            "energy": self.energy,
            "position": None
        }

        # Sex & constraints
        self.sex = random.choice(["female", "male"])
        self.risk_tolerance = 0.2 if self.sex == "female" else 0.8
        self.reproductive_status = "none"

    # --- Detect meaningful changes ---
    def has_changed(self):
        return (
            self.status != self.last_logged_state["status"]
            or abs(self.energy - self.last_logged_state["energy"]) >= 50
            or self.pos != self.last_logged_state["position"]
        )

    def update_logged_state(self):
        self.last_logged_state = {
            "status": self.status,
            "energy": self.energy,
            "position": self.pos
        }

    def log_event_if_changed(self):
        """Write an event row ONLY if something important changed."""
        if self.has_changed():
            # Define readable text
            if self.status == "dead":
                event = "Agent died"
            elif self.status == "injured":
                event = "Agent injured"
            elif self.status == "weak" and self.last_logged_state["status"] != "weak":
                event = "Energy dropped below maintenance"
            elif abs(self.energy - self.last_logged_state["energy"]) >= 50:
                event = f"Energy changed by {round(self.energy - self.last_logged_state['energy'], 1)}"
            elif self.pos != self.last_logged_state["position"]:
                event = "Moved to new cell"
            else:
                event = "State changed"

            self.model.record_event(
                step=self.model.schedule.time,
                agent=self,
                event_text=event
            )

            self.update_logged_state()

    # ---------------------------------------------------------------
    # -------------------------- NORMAL BEHAVIOR --------------------
    # ---------------------------------------------------------------

    def is_alive(self):
        return self.status != "dead"

    def step(self):
        if not self.is_alive():
            return

        if self.status == "injured":
            self.handle_injury_day()
            self.consume_daily()
            self.days_alive += 1
            self.log_event_if_changed()
            return

        # Activity choice
        activity = self.choose_activity()

        # Perform activity
        self.attempt_activity(activity)

        # Lose calories
        self.consume_daily()

        # Update life status
        self.update_survival_status()

        self.days_alive += 1

        # --- EVENT-BASED LOGGING HERE ---
        self.log_event_if_changed()

    def handle_injury_day(self):
        if self.injury_days_remaining > 0:
            self.injury_days_remaining -= 1
        if self.injury_days_remaining <= 0:
            self.status = "healthy" if self.energy >= self.model.daily_requirement else "weak"

    def choose_activity(self):
        if self.sex == "female":
            return "plants" if random.random() < 1 - self.risk_tolerance else random.choice(self.model.activities)
        return random.choice(self.model.activities)

    def attempt_activity(self, activity):
        activity_cost = ACTIVITY_COSTS.get(activity, 0)
        self.energy -= activity_cost

        self.random_move()

        # Look for matching resource patch
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        resource_patch = next(
            (obj for obj in cell_contents
             if isinstance(obj, ResourcePatch)
             and obj.resource_type == activity
             and obj.amount > 0),
            None
        )

        if resource_patch is None:
            return

        # Skill check
        req = resource_patch.definition["skill_required"]
        skill = self.foraging_skill if activity == "plants" else self.hunting_skill
        if skill < req:
            return

        # Gain calories
        gained = sample_resource_return(activity)
        weak_multiplier = 0.5 if self.status == "weak" else 1.0
        gained *= weak_multiplier
        self.energy += gained

        resource_patch.amount = max(0, resource_patch.amount - 1)

        # Risk outcomes
        rdef = resource_patch.definition
        roll = self.random.random()

        if roll < rdef["risk_death"]:
            self.die()
        elif roll < rdef["risk_death"] + rdef["risk_injury"]:
            self.become_injured(rdef.get("injury_days", 1))

    def consume_daily(self):
        penalty = 50 if self.sex == "female" and self.reproductive_status == "pregnant" else 0
        self.energy -= (self.model.daily_requirement + penalty)

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
        except:
            pass

    def become_injured(self, days):
        self.status = "injured"
        self.injury_days_remaining = max(1, days)

    def random_move(self):
        neigh = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False, radius=1
        )
        if neigh:
            self.model.grid.move_agent(self, random.choice(neigh))
