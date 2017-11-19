import time, User_inputs
import main, EPICS
from Zaber import ZB, ZB_Com, ZB_waitall
from SmarAct import SA, SA_Com
from Compensator import Trig
from NMR import NMR, NMR_read, NMR_Remote, NMR_Tune, NMR_local
# This module runs the secondary measurements that rotate Zaber 360° with each Senis probes at 0°, 90°, 180° and 270°(-90°) SmarAct angles
#Probably obsolete

DAC = 110000 # results in a field of ~0.5 T at 55 mm gap
SA.connect((User_inputs.SA_IP, User_inputs.SA_PORT))
ZB.open()
NMR.open()

ZB_ang = [5*x + 90 for x in range(0, 72)]
SA_ang = [180]
def out():
    ZB_Com("dev_X", "move abs", 0)
    ZB_Com("dev_Y", "move abs", 0)
    ZB_waitall()
    ZB_Com("dev_Z", "move abs", User_inputs.Z_CTR, option="wait")
    ZB_Com("dev_HP", "move abs", User_inputs.HP_FLAT, option="wait")
    SA_Com("move", User_inputs.HP_STRT)
    time.sleep(2)

def move(probe, SA_ang, ZB_ang):
    comp = Trig(probe, SA_ang, ZB_ang)  # Returns the amount to compensate after being rotated
    comp_x = User_inputs.X_CTR - comp[0]
    comp_y = User_inputs.Y_CTR - comp[1]
    comp_z = User_inputs.Z_CTR - comp[2]
    ZB_Com("dev_X", "move abs", comp_x)
    ZB_Com("dev_Y", "move abs", comp_y)
    ZB_Com("dev_Z", "move abs", comp_z)
    ZB_waitall()

    flatness = User_inputs.HP_FLAT + ZB_ang
    ZB_Com("dev_HP", "move abs", flatness, option="wait")
    straightness = User_inputs.HP_STRT + SA_ang
    SA_Com("move", straightness)

    time.sleep(2)  # Delay for vibration dampening
def center():
    ZB_Com("dev_X", "move abs", User_inputs.X_CTR)
    ZB_Com("dev_Y", "move abs", User_inputs.Y_CTR)
    ZB_Com("dev_Z", "move abs", User_inputs.Z_CTR)
    ZB_waitall()
    time.sleep(4)
def run():
    ans = input("do you want to home? (y/n)")
    if ans.lower() == "y":
        main.Home_All()
    pb = input("which senis probe would you like to select? (X, Y or Z)").upper()
    if pb != "X" and pb != "Y" and pb != "Z":
        print("please enter X, Y or Z only!")
        exit()
    print("Moving to ready position")
    main.To_Ready(pb)
    print("configuring HP ADC")
    EPICS.Config_HP()
    print("Selecting Probe")
    main.Choose_NMR_Probe(DAC)
    time.sleep(1)

    for S in SA_ang:
        main.Update_System(DAC, 1)
        center()
        print("ready to read NMR, 5 seconds!")
        time.sleep(5)
        NMR_read(filename="Secondary.txt")
        print("done reading")
        for Z in ZB_ang:
            print("moving to %d SA and %d ZB" % (S, Z))
            move("Y", S, Z)
            EPICS.Rec_HP_Alt()
        out()
    EPICS.Power_OFF()
    ZB.close()
    NMR.close()
    SA.close()
    print("All done!")

if __name__ == "__main__":
    run()

