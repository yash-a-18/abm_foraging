# server.py
from mesa.visualization.modules import CanvasGrid, ChartModule, TextElement
from mesa.visualization.ModularVisualization import ModularServer
from model import ForageModel
import config
from agents import ForagerAgent, ResourcePatch

# 1. ADD A CUSTOM TEXT ELEMENT FOR THE SIDE LOG
class StatusLogElement(TextElement):
    def __init__(self):
        pass
    def render(self, model):
        events = getattr(model, 'event_history', [])
        
        # Use a scrollable div so the list of agents doesn't push the charts away
        log_html = """
        <div style='border:1px solid #ccc; padding:10px; background:#f9f9f9; 
                    height:350px; overflow-y:auto; font-family:monospace;'>
            <ul style='list-style-type:none; padding:0; margin:0;'>
        """
        # Show newest summaries at the top
        for e in reversed(events):
            # Make Step headers bold for visual clarity
            if "--- Step" in e:
                log_html += f"<li style='margin-top:10px; border-bottom:2px solid #333; font-weight:bold;'>{e}</li>"
            else:
                log_html += f"<li style='margin-bottom:2px; border-bottom:1px solid #eee; font-size:11px;'>{e}</li>"
        
        log_html += "</ul></div>"
        return log_html

def portrayal_method(obj):
    if obj is None: return
    
    # PORTRAYAL FOR AGENTS
    if isinstance(obj, ForagerAgent):
        portrayal = {
            "Layer": 1,
            "AgentID": obj.unique_id,
            "Status": obj.status,
            "Reasoning": obj.reasoning,
            "Current Energy": f"{int(obj.energy)}",
            "text_color": "white",
        }
        
        # Mapping status to specific image files
        # Ensure these files exist in your /resources/ folder
        if obj.status == "dead":
            portrayal["Shape"] = "resources/dead_icon.png" 
        elif obj.status == "injured":
            portrayal["Shape"] = "resources/injured_icon.png"
        else:
            portrayal["Shape"] = "resources/man_icon.png"
            
        portrayal["scale"] = 0.9
        return portrayal

    # PORTRAYAL FOR RESOURCES
    if isinstance(obj, ResourcePatch):
        portrayal = {"Layer": 0, "scale": 0.8}
        
        if obj.resource_type == "plants":
            portrayal["Shape"] = "resources/plant.png"
        elif obj.resource_type == "small_game":
            portrayal["Shape"] = "resources/rabbit.png"
        elif obj.resource_type == "large_game":
            portrayal["Shape"] = "resources/bear.png"
            
        return portrayal
    
# server.py (Add this new element)

class StatsTableElement(TextElement):
    def render(self, model):
        table_html = """
        <table style='width:100%; border-collapse: collapse; font-family:sans-serif; font-size:12px;'>
            <tr style='background:#ddd;'>
                <th>Agent</th><th>Energy</th><th>Status</th><th>P</th><th>S</th><th>L</th>
            </tr>
        """
        for agent in model.schedule.agents:
            if isinstance(agent, ForagerAgent):
                # Color code status
                color = "black" if agent.status == "dead" else "green" if agent.status == "healthy" else "orange"
                
                table_html += f"""
                <tr>
                    <td>{agent.unique_id}</td>
                    <td>{int(agent.energy)}</td>
                    <td style='color:{color};'>{agent.status}</td>
                    <td>{agent.consumption_stats['plants']}</td>
                    <td>{agent.consumption_stats['small_game']}</td>
                    <td>{agent.consumption_stats['large_game']}</td>
                </tr>
                """
        table_html += "</table>"
        return table_html

# UI Layout
status_log = StatusLogElement()
stats_table = StatsTableElement()
grid = CanvasGrid(portrayal_method, config.GRID_WIDTH, config.GRID_HEIGHT, 500, 500)
chart = ChartModule([
    {"Label": "Alive", "Color": "Green"},
    {"Label": "Injured", "Color": "Orange"},
    {"Label": "Dead", "Color": "Red"},
    {"Label": "Mean Energy", "Color": "Blue"}
])

server = ModularServer(
    ForageModel, 
    [grid, status_log, stats_table, chart], # Added status_log and stats_table here
    "Foraging Survival Sim", 
    {}
)