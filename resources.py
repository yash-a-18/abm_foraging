import random
import math
from config import RESOURCE_DEFS

def sample_resource_return(resource_type):
    """
    Sample kcal return from a resource.
    """
    rd = RESOURCE_DEFS[resource_type]
    mean = rd["mean"]
    var = rd["variance"]
    val = random.gauss(mean, math.sqrt(var))
    return max(0.0, val)
