# model.py
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from agents import ForagerAgent, ResourcePatch
import random
import itertools

import config

class ForageModel(Model):
    """
    Mesa Model for foraging/hunting simulation.
    """
    def __init__(self,
                 width=config.GRID_WIDTH,
                 height=config.GRID_HEIGHT,
                 initial_population=config.INITIAL_POPULATION,
                 resource_defs=config.RESOURCE_DEFS,
                 spawn_probs=config.RESOURCE_SPAWN_PROBS,
                 activities=config.ACTIVITIES,
                 starting_energy=config.STARTING_ENERGY,
                 daily_requirement=config.DAILY_REQUIREMENT,
                 max_weak_days=config.MAX_WEAK_DAYS,
                 activity_costs=config.ACTIVITY_COSTS):
        super().__init__()
        self.width = width
        self.height = height
        self.grid = MultiGrid(width, height, torus=True)
        self.schedule = RandomActivation(self)
        self.next_resource_id = itertools.count(1000000)
        self.next_agent_id = itertools.count(1)
        self.initial_population = initial_population

        # Model-level editable params
        self.resource_defs = resource_defs
        self.spawn_probs = spawn_probs
        self.activities = activities
        self.starting_energy = starting_energy
        self.daily_requirement = daily_requirement
        self.max_weak_days = max_weak_days
        self.activity_costs = activity_costs

        # Tracking
        self.initial_agents_count = initial_population
        self.dead_count = 0
        self.injured_count = 0

        # Create agents
        for i in range(self.initial_population):
            aid = next(self.next_agent_id)
            # simple skills: foraging skill randomly 0..4, hunting skill randomly 0..8
            for_skill = self.random.randint(0, 4)
            hunt_skill = self.random.randint(0, 8)
            agent = ForagerAgent(aid, self, name=f"Agent_{aid}", foraging_skill=for_skill, hunting_skill=hunt_skill)
            agent.energy = self.starting_energy
            self.schedule.add(agent)
            # place agent randomly
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))

        # Data collector
        self.datacollector = DataCollector(
            model_reporters={
                "Alive": lambda m: sum(a.is_alive() for a in m.schedule.agents),
                "Dead": lambda m: sum(a.status=="dead" for a in m.schedule.agents),
                "Injured": lambda m: sum(a.status=="injured" for a in m.schedule.agents),
                "MeanEnergy": lambda m: (sum(a.energy for a in m.schedule.agents if a.is_alive()) / 
                                        max(1, sum(a.is_alive() for a in m.schedule.agents)))
            },
            agent_reporters={
                "Energy": lambda a: getattr(a, "energy", None),
                "Status": lambda a: getattr(a, "status", None),
                "ForagingSkill": lambda a: getattr(a, "foraging_skill", None),
                "HuntingSkill": lambda a: getattr(a, "hunting_skill", None),
            }
        )

        # spawn initial resources
        self.spawn_resources_initial()

    def spawn_resources_initial(self):
        # fill grid randomly with some initial resource patches according to spawn probs
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                self.try_spawn_patch((x, y))

    def try_spawn_patch(self, pos):
        # Only spawn if cell doesn't yet contain a resource patch.
        cell_contents = self.grid.get_cell_list_contents([pos])
        existing = any(isinstance(obj, ResourcePatch) for obj in cell_contents)
        if existing:
            return
        for rtype, prob in self.spawn_probs.items():
            if self.random.random() < prob:
                rid = next(self.next_resource_id)
                patch = ResourcePatch(rid, self, rtype)
                self.grid.place_agent(patch, pos)
                # Also add to schedule so that patches exist in get_cell_list_contents and actor lifecycle (though passive)
                self.schedule.add(patch)
                return

    def step(self):
        # Each step:
        # 1) Spawn new resources (simple: try to spawn in empty cells)
        # 2) Step through scheduled agents (random activation)
        # 3) Collect data
        # 4) Clean up fully depleted resource patches
        # 1) spawn
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                self.try_spawn_patch((x, y))

        # 2) step scheduler
        self.schedule.step()

        # 3) collect data
        self.datacollector.collect(self)

        # 4) cleanup dead markers and depleted patches
        self.cleanup_dead_agents_and_depleted_resources()

    def cleanup_dead_agents_and_depleted_resources(self):
        # remove dead agents from grid and schedule (but keep them in schedule.agents so DataCollector works; Mesa's scheduler doesn't typically remove)
        # For simplicity, we'll not remove dead from schedule.agents, but we'll try removing from grid cells so they don't clutter visuals.
        for agent in list(self.schedule.agents):
            if getattr(agent, "status", None) == "dead":
                # attempt to remove from grid
                try:
                    if agent.pos is not None:
                        self.grid.remove_agent(agent)
                except Exception:
                    pass

        # remove depleted resource patches
        for obj in list(self.schedule.agents):
            if isinstance(obj, ResourcePatch):
                if obj.amount <= 0:
                    try:
                        if obj.pos is not None:
                            self.grid.remove_agent(obj)
                    except Exception:
                        pass
                    try:
                        # remove from schedule to keep iteration tidy
                        self.schedule.remove(obj)
                    except Exception:
                        pass
