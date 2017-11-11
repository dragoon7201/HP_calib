import RT_plotter
from threading import Thread
import numpy as np
import random
import time
#import EPICS

while True:
    reply = input("Select the hall probes to zero, any combination of X, Y, and Z separated by commas\n").upper()
    Probes = reply.replace(' ', '').split(',')
    if set(Probes).issubset(['X', 'Y', 'Z']):
        break
    else:
        print("Input not understood, please please try again")



# x, y, z = EPICS.Rec_HP(run_mode='zeroing', probe='X', option='return_ave')[:3]