import time, User_inputs, sys, os, datetime
from NMR import NMR, NMR_read, NMR_Tune, NMR_Remote, NMR_local
from Zaber import ZB_Com, ZB, ZB_waitall
from SmarAct import SA_Com, SA
import EPICS #Cyclical referencing, hence 'from xxx import yyy' does not work
from Compensator import Trig




tally = 0
if tally%2 == 0:
    SA_loop = User_inputs.SA_ANGLES
else:
    SA_loop = reversed(User_inputs.SA_ANGLES)
for SA_angle in SA_loop:
    tally += 1
    if tally%2 != 0:
        ZB_loop = User_inputs.ZB_ANGLES
    else:
        ZB_loop = reversed(User_inputs.ZB_ANGLES)
    for ZB_angle in ZB_loop:
        #Move_One('N', SA_angle, ZB_angle)
        print("Angle SA: %s Angle ZB: %s" % (SA_angle, ZB_angle))
        #Move_Two()

