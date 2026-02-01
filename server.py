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
        # Retrieve the last 5 events from the model's history
        events = model.event_history[-5:] if hasattr(model, 'event_history') else []
        log_html = "<div style='border:1px solid #ccc; padding:10px; background:#f9f9f9;'>"
        log_html += "<h4>Live Status Log</h4><ul style='list-style-type:none; padding:0;'>"
        for e in reversed(events):
            log_html += f"<li style='margin-bottom:5px; border-bottom:1px solid #eee;'>{e}</li>"
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

# UI Layout
status_log = StatusLogElement()
grid = CanvasGrid(portrayal_method, config.GRID_WIDTH, config.GRID_HEIGHT, 500, 500)
chart = ChartModule([
    {"Label": "Alive", "Color": "Green"},
    {"Label": "Injured", "Color": "Orange"},
    {"Label": "Dead", "Color": "Red"}
])

server = ModularServer(
    ForageModel, 
    [grid, status_log, chart], # Added status_log here
    "Foraging Survival Sim", 
    {}
)