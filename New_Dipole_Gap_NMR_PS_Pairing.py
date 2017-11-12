# This module runs the power supply at various dac settings, and moves the NMR probe into reading position.
# The user then must choose a nmr probe and manually lock in the field. When satisfied, enter "pair"
# this will record the NMR dac value that will result in a locked field. The program then moves on to the next PS setting.

import User_inputs
from NMR import Read_DAC, NMR, NMR_read
from Zaber import ZB, ZB_Com, ZB_waitall
from main import Home_All, Move_Out
import EPICS
PS_seq = [10000*x for x in range(3,36)]
Parings = {}

NMR.open()
ZB.open()

print("PS settings: ", PS_seq)
print("Do you want to home Zaber devices? (y/n)")
reply = input().lower()
if reply == 'y':
    Home_All("no_SA")

print("Moving to NMR measuring position.")
ZB_Com("dev_X", "move abs", User_inputs.X_CTR)
ZB_Com("dev_Y", "move abs", User_inputs.Y_CTR)
ZB_Com("dev_Z", "move abs", User_inputs.Z_CTR)
ZB_waitall()

for PS in PS_seq:
    locked_probe = ''
    print("Enter number to select the NMR probe for PS setting of: ", PS)
    while True:
        PB = input('\n')
        if PB == '2':
            ZB_Com("dev_NMR", "move abs", User_inputs.NMR_P2, option="wait")
            locked_probe = 'E'
            break
        elif PB == '4':
            ZB_Com("dev_NMR", "move abs", User_inputs.NMR_P4, option="wait")
            locked_probe = 'F'
            break
        elif PB == '5':
            ZB_Com("dev_NMR", "move abs", User_inputs.NMR_P5, option="wait")
            locked_probe = 'G'
            break
        else:
            print("input not recognized, please enter 2, 4, or 5")
    EPICS.Power_ON(PS, 1)
    print("Power supply is now ready, please lock in the field manually, and enter 'lock' to record NMR dac.")
    print("If no lock is possible, enter 'skip' to move to the next power supply dac")
    print("If a different NMR probe is needed, enter the probe number instead")
    while True:
        response = input('\n').lower()
        if response == '2':
            ZB_Com("dev_NMR", "move abs", User_inputs.NMR_P2, option="wait")
            locked_probe = 'E'
        elif response == '4':
            ZB_Com("dev_NMR", "move abs", User_inputs.NMR_P4, option="wait")
            locked_probe = 'F'
        elif response == '5':
            ZB_Com("dev_NMR", "move abs", User_inputs.NMR_P5, option="wait")
            locked_probe = 'G'
        elif response == "lock":
            dac = Read_DAC()
            time.sleep(0.5)
            field = NMR_read('x','x',option='return')
            Parings.update({PS: (dac, locked_probe, field)})
            print('PS dac of %d is successfully paired with NMR dac of %d, field is %s T' % (PS, dac, field))
            break
        elif response == 'skip':
            break
        else:
            print("input not recognized, please enter 'lock' if field is locked in, or 2, 4, 5 to change NMR probe, and 'skip' if no lock is possible")
    print('moving on to the next PS dac')

print("would you like to save results into text file? If so, enter a descriptor such as 'Gap_55mm', otherwise enter 'n' to end program without saving")
reply = input()
if len(reply) > 1:
    print('saving to ', User_inputs.CUR_DIR)
    with open(User_inputs.CUR_DIR + '/' + reply + '.txt', 'a+') as file:
        file.write('PS_DAC\t\tNMR_DAC\t\tNMR_Prb\t\tField[T]\n')
        for key in Parings:
            file.write('%d\t\t%d\t\t%s\t\t%.4f\n' % (key, Parings[key][0], Parings[key][1], Parings[key][2]))v # Note that the writen file is unordered. This is not an error, but just how dictionaries are in Python
print('program finishing...')                                                                                  
EPICS.Power_OFF()
Move_Out()
NMR.close()
ZB.close()
