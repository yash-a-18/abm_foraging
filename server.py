from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from model import ForageModel
from config import AGENT_SIZE, RESOURCE_SIZE, GRID_WIDTH, GRID_HEIGHT
from agents import ForagerAgent, ResourcePatch

def portrayal_method(obj):
    if obj is None:
        return
    portrayal = {}

    if isinstance(obj, ForagerAgent):
        portrayal["Shape"] = "circle"
        portrayal["r"] = AGENT_SIZE
        portrayal["Layer"] = 1
        portrayal["Filled"] = "true"
        if obj.status == "dead":
            portrayal["Color"] = "black"
            portrayal["text"] = ""
        elif obj.status == "injured":
            portrayal["Color"] = "orange"
            portrayal["text"] = "I"
        elif obj.status == "weak":
            portrayal["Color"] = "yellow"
            portrayal["text"] = "W"
        else:
            portrayal["Color"] = "green"
            portrayal["text"] = ""
        portrayal["text_color"] = "black"
        return portrayal

    if isinstance(obj, ResourcePatch):
        portrayal["Shape"] = "rect"
        portrayal["w"] = RESOURCE_SIZE
        portrayal["h"] = RESOURCE_SIZE
        portrayal["Layer"] = 0
        rtype = getattr(obj, "resource_type", None)
        if rtype == "plants":
            portrayal["Color"] = "lightgreen"
            portrayal["text"] = "P"
        elif rtype == "small_game":
            portrayal["Color"] = "saddlebrown"
            portrayal["text"] = "S"
        elif rtype == "large_game":
            portrayal["Color"] = "darkred"
            portrayal["text"] = "L"
        else:
            portrayal["Color"] = "gray"
            portrayal["text"] = ""
        portrayal["text_color"] = "black"
        return portrayal

    return None

# Grid visualization
grid = CanvasGrid(portrayal_method, GRID_WIDTH, GRID_HEIGHT, 500, 500)

# Chart visualization
chart = ChartModule([
    {"Label": "Alive", "Color": "Green"},
    {"Label": "Dead", "Color": "Black"},
    {"Label": "Injured", "Color": "Orange"},
    {"Label": "MeanEnergy", "Color": "Blue"},
])

server = ModularServer(
    ForageModel,
    [grid, chart],
    "Foraging-Hunting Model",
    {}  # default params
)
