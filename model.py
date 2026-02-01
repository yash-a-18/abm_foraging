# model.py
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from agents import ForagerAgent, ResourcePatch
import random
import itertools
import config
import pandas as pd
from log import get_log_path

class ForageModel(Model):
    """
    Mesa Model for foraging/hunting simulation simulating older times.
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
        self.event_history = []
        self.width = width
        self.height = height
        self.grid = MultiGrid(width, height, torus=True)
        self.schedule = RandomActivation(self)
        self.next_resource_id = itertools.count(1000000)
        self.next_agent_id = itertools.count(1)
        
        # Model Parameters
        self.resource_defs = resource_defs
        self.spawn_probs = spawn_probs
        self.activities = activities
        self.starting_energy = starting_energy
        self.daily_requirement = daily_requirement
        self.max_weak_days = max_weak_days
        self.run_id = random.randint(100000, 999999)

        # Create agents with the simplified __init__
        for i in range(initial_population):
            aid = next(self.next_agent_id)
            agent = ForagerAgent(aid, self, name=f"Agent_{aid}")
            self.schedule.add(agent)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))

        self.datacollector = DataCollector(
            model_reporters={
                "Alive": lambda m: sum(1 for a in m.schedule.agents if isinstance(a, ForagerAgent) and a.status != "dead"),
                "Dead": lambda m: sum(1 for a in m.schedule.agents if isinstance(a, ForagerAgent) and a.status == "dead"),
                "Injured": lambda m: sum(1 for a in m.schedule.agents if isinstance(a, ForagerAgent) and a.status == "injured"),
            }
        )

        self.spawn_resources_initial()

    def spawn_resources_initial(self):
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                self.try_spawn_patch((x, y))

    def try_spawn_patch(self, pos):
        cell_contents = self.grid.get_cell_list_contents([pos])
        if any(isinstance(obj, ResourcePatch) for obj in cell_contents):
            return
        for rtype, prob in self.spawn_probs.items():
            if self.random.random() < prob:
                rid = next(self.next_resource_id)
                patch = ResourcePatch(rid, self, rtype)
                self.grid.place_agent(patch, pos)
                self.schedule.add(patch)
                break

    def record_event(self, step, agent, event_text):
        log_path = get_log_path()

        stats = agent.consumption_stats
        stats_str = f"P:{stats['plants']} | S:{stats['small_game']} | L:{stats['large_game']}"
        row = {
            "RunID": self.run_id,
            "Step": step,
            "AgentID": agent.unique_id,
            "Status": agent.status,
            "Energy": round(agent.energy, 2),
            "Position": str(agent.pos),
            "Event": event_text,
            "Reasoning": getattr(agent, "reasoning", ""),
            "DeathCause": getattr(agent, "cause_of_death", ""),
            "Stats": stats_str
        }
        pd.DataFrame([row]).to_csv(log_path, mode="a", header=False, index=False)

        # Add to UI history
        reason = getattr(agent, "reasoning", "")
        log_msg = (f"Step {step}: Agent {agent.unique_id} - {event_text} | "
                   f"Stats: [{stats_str}] | "
                   f"Reasoning: {reason}")
        self.event_history.append(log_msg)

    def step(self):
        # 1. Spawn new resources
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                self.try_spawn_patch((x, y))

        # 2. Let agents act
        self.schedule.step()

        # Log active agents only
        for agent in self.schedule.agents:
            if isinstance(agent, ForagerAgent) and agent.status != "dead":
                # Record to CSV for full data analysis
                self.record_event(self.schedule.steps, agent, "Step Update")
                
                # Format a summary string for the UI Status Log
                stats = agent.consumption_stats
                agent_summary = (
                    f"Agent {agent.unique_id}: Energy {int(agent.energy)} | "
                    f"Status: {agent.status} | "
                    f"Harvested: [P:{stats['plants']}, S:{stats['small_game']}, L:{stats['large_game']}]"
                )
                self.event_history.append(agent_summary)

        summary_msg = f"--- Step {self.schedule.steps} Summary ---"
        self.event_history.append(summary_msg)

        # 3. Collect model- and agent-level summary stats
        self.datacollector.collect(self)
        
        if sum(1 for a in self.schedule.agents if isinstance(a, ForagerAgent) and a.status != "dead") == 0:
            self.running = False