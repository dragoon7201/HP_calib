import RT_plotter
from threading import Thread
import numpy as np
import random
import time
from main import Move_One

from epics import PV

tm = PV("TM1504-1-02")
print(tm.get())