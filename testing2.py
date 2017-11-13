import User_inputs
import EPICS
import time
import Zaber
import SmarAct
import main
import NMR
import Temp_monitor
import subprocess

NMR.NMR.open()
Zaber.ZB.open()
SmarAct.SA.connect((User_inputs.SA_IP, User_inputs.SA_PORT))

main.Move_Two()

#subprocess.run(Temp_monitor.Start_Temp_monitor())

for key in User_inputs.PS_NMR:
    main.Choose_Probe(key)
    NMR.NMR_Remote(key, 1)
    EPICS.Power_ON(key, 1)
    NMR.NMR_Tune(key)
    time.sleep(2)

    print(key, User_inputs.PS_NMR[key][0])
print("done")

NMR.NMR.close()
Zaber.ZB.close()
SmarAct.SA.close()
