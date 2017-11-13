import time, User_inputs
from SmarAct import SA
from Zaber import ZB
from NMR import NMR, NMR_read, NMR_Remote, NMR_local
import EPICS
import main
import sys, os
import numpy as np


try:
    SA.connect((User_inputs.SA_IP, User_inputs.SA_PORT))
    ZB.open()
    NMR.open()
except:
    print("Failed to connected to SmarAct, Zaber or NMR devices! Please check connections and try again!")
    sys.exit()


# Checks temperature, and powers on or off the power supply, and tunes the NMR teslameter afterwards


def Zeroing():
    reply = input("Does devices need homing? (y/n)\n").lower()
    if reply == 'y':
        main.Home_All()

    reply = input("Enter Power Supply Dac to be used for zeroing, 230000 (~1.0 T) recommended for 55mm dipole gap\n")
    PS = int(reply)

    while True:
        reply = input("Select the hall probes to zero, any combination of X, Y, and Z separated by commas\n").upper()
        Probes = reply.replace(' ', '').split(',')
        if set(Probes).issubset(['X', 'Y', 'Z']):
            break
        else:
            print("Input not understood, please try again")

    while True:
        reply = input("would you like to zero SA angle or ZB angle? (enter 'S' or 'Z' or 'B' for both)\n").lower()
        if reply == 's':
            devices = ["SA"]
            break
        elif reply == 'z':
            devices = ["ZB"]
            break
        elif reply == 'b':
            devices = ["SA", "ZB"]
            break
        else:
            print('Cannot understand instruction! Please enter S, Z, or B')

    while True:
        reply = input(
            "Please enter the minimum angle, maximum angle and step size for zeroing in degrees. Separate with commas, accepts decimals (min_angle, max_angle, step_size)\n")
        inputs = reply.split(',')
        inputs = [float(x) for x in inputs]
        try:
            Angle_range = np.around(np.arange(inputs[0], inputs[1] + 0.01, inputs[2]), 2).tolist()  # This line first computes an numpy array with input min, max and step, then rounds it to 2 decimals, finally converts it to a python list
            break
        except:
            print('Inputs not understood, please make sure the entry order is: min_angle, max_angle, step_size')
            continue  # remains in loop until user gets inputs right

    while True:
        reply = input("Choose polarity (+ or - or # for both)\n")
        if reply == '+':
            polarity = [1]
            break
        elif reply == '-':
            polarity = [0]
            break
        elif reply == '#':
            polarity = [1, 0]
            break
        else:
            print('Cannot understand input! Please enter -, +, or #')

    reply = input('Would you like to plot data in real-time? (y/n)\n').lower()
    if reply == 'y':
        import RT_plotter
        from threading import Thread
        plot = True
        plotter = Thread(target=RT_plotter.plot)
        plotter.start()
        time.sleep(1)
    else:
        plot = False

    os.system('cls')
    print("Please confirm the run settings:\n")
    print("Current Run Tag: ", User_inputs.CUR_TAG)
    print("Hall probes to Zero: ", Probes)
    print("Devices to zero: ", devices)
    print("Power supply polarity: ", polarity)
    print("Angle range of zeroing: starting %.2f°, ending %.2f°, in steps of %.2f°" %(inputs[0], inputs[1], inputs[2]))
    print("Real-time plotting: ", "YES" if plot else "NO")
    print("Enter anything to begin")
    input()
    os.system('cls')

    print('configuring ADC settings...')
    EPICS.Config_HP()

    for pol in polarity:
        for HP in Probes:
            main.To_Ready(HP)
            main.Update_System(PS, pol) # powers up power supply and locks in NMR
            NMR_read(run_mode="zeroing", probe=HP)  # NMR readings are recorded once for each hall probe and polarity.
            print("Begin zeroing")
            for D in devices:
                for A in Angle_range:
                    #exec() is used instead of a direct call, because it allows for flexibility in choice of ZB = angle or SA = angle.
                    exec("main.Move_One(HP, %s = %f)" % (D + "_angle", A)) # Sets an Angle for either SA or ZB, the other is defaulted to 0°
                    print("angle: %f for device %s" % (A, D))
                    if plot:
                        x, y, z = EPICS.Rec_HP(run_mode='zeroing', probe=HP, option='return_ave')[:3] #Gets the first 3 return (X, Y, Z averages)
                        RT_plotter.x_dat.append(x)
                        RT_plotter.y_dat.append(y)
                        RT_plotter.z_dat.append(z)
                        RT_plotter.x_axis.append(A)
                        RT_plotter.new_data = True #When new data is true, the plotter updates itself
                    else:
                        EPICS.Rec_HP(run_mode='zeroing', probe=HP)
                if plot: # This part is to reset the plot after finishing the scans for one device.
                    RT_plotter.fig_name = D + '_' + HP + ('_pos' if pol > 0 else "_neg") + '.png' #Sets the filename for saving
                    RT_plotter.SAVE = True  #Turns the saving path to true, the actual saving is done in RT_plotter.py module, save directory is HP_Data
                    time.sleep(2)
                    RT_plotter.x_dat = [] #Clears previous data
                    RT_plotter.y_dat = []
                    RT_plotter.z_dat = []
                    RT_plotter.x_axis = []
            print('done ', HP)
            NMR_local()
            main.Move_Out()
        EPICS.Power_OFF()
    RT_plotter.RUN = False
    main.Safe_Pos()
    print('Program finished')
    #After closing the program, an error would occur because one of the modules that RT_plotter uses needs to be in the main thread. But this error should be fine, since it is at the end of the program and all needed data is collected.

if __name__ == "__main__":
    Zeroing()
