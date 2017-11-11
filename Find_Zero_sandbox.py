import time, User_inputs
import sys, os
import numpy as np
import random


def rand(x=1):
    ret = []
    for i in range(0,x):
        ret.append(random.uniform(1.0,2.0))
    return ret

def Zeroing():

    PS = 200000

    Probes = ['X','Y','Z']


    devices = ["SA", "ZB"]


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



    polarity = [1, 0]


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

    # for pol in polarity:
    #     for HP in Probes:
    #         print("Begin zeroing")
    #         for D in devices:
    #             for A in Angle_range:
    #                 #exec() is used instead of a direct call, because it allows for flexibility in choice of ZB = angle or SA = angle.
    #                 #exec("main.Move_One(HP, %s = %f)" % (D + "_angle", A)) # Sets an Angle for either SA or ZB, the other is defaulted to 0°
    #                 print("angle: %f for device %s" % (A, D))
    #                 if plot:
    #                     [x, y, z] = rand(3)
    #                     RT_plotter.x_dat.append(x)
    #                     RT_plotter.y_dat.append(y)
    #                     RT_plotter.z_dat.append(z)
    #                     RT_plotter.x_axis.append(A)
    #                     RT_plotter.new_data = True  # When new data is true, the plotter updates itself
    #                 time.sleep(1)
    #             if plot: # This part is to reset the plot after finishing the scans for one device.
    #                 RT_plotter.fig_name = D + '_' + HP + '_pos' if pol > 0 else "_neg" + '.png' #Sets the filename for saving
    #                 RT_plotter.SAVE = True  # Turns the saving path to true, the actual saving is done in RT_plotter.py module
    #                 time.sleep(2)
    #                 RT_plotter.x_dat = []  # Clears data
    #                 RT_plotter.y_dat = []
    #                 RT_plotter.z_dat = []
    #                 RT_plotter.x_axis = []
    #         print('done ', HP)
    RT_plotter.RUN = False
    plotter.join()
    time.sleep(2)
    print('Program finished')

if __name__ == "__main__":
    Zeroing()
