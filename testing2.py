import RT_plotter
from threading import Thread
import numpy as np
import random
import time
#import EPICS

pol = 1
fig_name = 'string' + '_pos' if pol > 0 else "_neg" + '.png'  # Sets the filename for saving
print(fig_name)


# x, y, z = EPICS.Rec_HP(run_mode='zeroing', probe='X', option='return_ave')[:3]