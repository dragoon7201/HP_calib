# This is the main function for the calibration program, it provides the framework for other individual modules
import time, User_inputs, sys, os, datetime
from NMR import NMR, NMR_read, NMR_Tune, NMR_Remote, NMR_local
from Zaber import ZB_Com, ZB, ZB_waitall
from SmarAct import SA_Com, SA
import EPICS #Cyclical referencing, hence 'from xxx import yyy' does not work
from Compensator import Trig
## Home all devices, This function assumes that the program closes properly
## If Due to whatever reason, the program did not end properly
## One should be extra careful and home the device manually
def Home_All(option=""): #set option to anything if SA not required/attached
    ZB_Com("dev_X", "home")
    ZB_Com("dev_Y", "home")
    ZB_Com("dev_NMR", "home")
    ZB_Com("dev_HP", "home")
    ZB_waitall()
    ZB_Com("dev_HP", "move abs", -20, option="wait")
    ZB_Com("dev_Z", "home", option="wait")
    ZB_Com("dev_Z", "move abs", User_inputs.Z_CTR, option="wait")
    ZB_Com("dev_HP", "move abs", 0, option="wait")
    if option == "":
        print("Configuring SmarAct device, this will take ~15 seconds..")
        SA_Com("reset")
        time.sleep(2)   #Some initializing commands take some time to finish,
                        #So waiting some time is needed.
        SA_Com("sync")
        time.sleep(2)
        SA_Com("enable_sensor")
        time.sleep(2)
        SA_Com("set_type")
        time.sleep(2)
        SA_Com("home")
        time.sleep(1)
## Returns all devices to a Safe position at the end of program.
# Or after error, such that it can be homed properly next time.
def Safe_Pos():
    ZB_Com("dev_X", "home")
    ZB_Com("dev_Y", "home")
    ZB_waitall()
    ZB_Com("dev_Z", "move abs", User_inputs.Z_CTR)
    ZB_Com("dev_NMR", "move abs", 0)
    ZB_Com("dev_HP", "move abs", 0, option="wait")# uses move abs 0 instead of home as move abs will always retrace its path back
    SA_Com("move", 10) #10° so SmarAct rests a little CCW to the reference mark 0°
    ZB.close()
    NMR.close()
    SA.shutdown(1)
    SA.close()

def Move_Out():
    ZB_Com("dev_X", "move abs", 0)
    ZB_Com("dev_Y", "move abs", 0)
    ZB_waitall()
    ZB_Com("dev_Z", "move abs", User_inputs.Z_CTR)
    ZB_Com("dev_HP", "move abs", 0, option="wait")

## Readies Zaber devices for the selected hall probe sensor.
def To_Ready(Probe):
    #Sets the FLAT and STRT variables, which are the reference angles that future offsets are based upon
    #For example, +20° ZB rotation would be a +20° move from the FLAT angle of whichever probe
    if Probe == "X":
        User_inputs.HP_FLAT = User_inputs.ZB_ZERO[0]
        User_inputs.HP_STRT = User_inputs.SA_ZERO[0]
        ZB_Com("dev_HP", "move abs", User_inputs.HP_FLAT, option="wait")
        ZB_Com("dev_X", "move abs", User_inputs.X_CTR)
        ZB_Com("dev_Y", "move abs", User_inputs.Y_CTR)
        ZB_Com("dev_Z", "move abs", User_inputs.Z_CTR)
        SA_Com("move", User_inputs.HP_STRT)
        ZB_waitall()
    elif Probe == "Y":
        User_inputs.HP_FLAT = User_inputs.ZB_ZERO[1]
        User_inputs.HP_STRT = User_inputs.SA_ZERO[1]
        ZB_Com("dev_Z", "move abs", User_inputs.Z_CTR - 3, option="wait") #giving it more room on the left to rotate
        ZB_Com("dev_HP", "move abs", User_inputs.HP_FLAT, option="wait")
        ZB_Com("dev_X", "move abs", User_inputs.X_CTR)
        ZB_Com("dev_Y", "move abs", User_inputs.Y_CTR)
        ZB_waitall()
        ZB_Com("dev_Z", "move abs", User_inputs.Z_CTR)
        SA_Com("move", User_inputs.HP_STRT)
        ZB_waitall()
    elif Probe == "Z":
        User_inputs.HP_FLAT = User_inputs.ZB_ZERO[2]
        User_inputs.HP_STRT = User_inputs.SA_ZERO[2]
        ZB_Com("dev_HP", "move abs", User_inputs.HP_FLAT, option="wait")
        ZB_Com("dev_X", "move abs", User_inputs.X_CTR)
        ZB_Com("dev_Y", "move abs", User_inputs.Y_CTR)
        ZB_Com("dev_Z", "move abs", User_inputs.Z_CTR)
        SA_Com("move", User_inputs.HP_STRT)
        ZB_waitall()
    else:
        print("Please double check HP probe entry in user_inputs.txt!")
        print("only 'X' , 'Y' or 'Z' is accepted")
        input()
        sys.exit()
    time.sleep(2)
## Checks User choice of polarities
def Polarity_Order(input):
    if input == "-":
        return [0]
    elif input == '+':
        return [1]
    elif input == '#':
        return [1, 0]
    else:
        print("Please double check PS Polarity entry in user_inputs.txt!")
        print("only '-' , '+' or '#' is acceptable")
        print("moving to safe position and exiting")
        Safe_Pos()
        input()
        sys.exit()
## Picks the appropriate NMR probe to use for a given dac PS output
def Choose_Probe(dac):
    #User.input.NMR_PX is the absolute angle position of the corresponding probes.
    #So if the probes have be re-arranged, one would need to enter new angles
    NMR_probe = User_inputs.PS_NMR[dac][1]
    if NMR_probe == 'E':
        ZB_Com("dev_NMR", "move abs", User_inputs.NMR_P2, option="wait")
    elif NMR_probe == 'F':
        ZB_Com("dev_NMR", "move abs", User_inputs.NMR_P4, option="wait")
    elif NMR_probe == 'G':
        ZB_Com("dev_NMR", "move abs", User_inputs.NMR_P5, option="wait")
    else:
        print("Did we get new NMR probes? I may need to be re-programed")
    time.sleep(1)
## Move the hall sensor into the measurement position,
# The idea is to get the hall sensor and NMR probe to measure at the same spatial position
# Thus eliminating any discrepancy in field uniformity across the dipole
def Move_One(probe, SA_angle=0.0, ZB_angle=0.0):
    compensation = Trig(probe, SA_angle, ZB_angle) # Returns the amount to compensate after being rotated
    comp_x = User_inputs.X_CTR - compensation[0]
    comp_y = User_inputs.Y_CTR - compensation[1]
    comp_z = User_inputs.Z_CTR - compensation[2]
    ZB_Com("dev_X", "move abs", comp_x)
    ZB_Com("dev_Y", "move abs", comp_y)
    ZB_Com("dev_Z", "move abs", comp_z)
    ZB_waitall()
    Yaw = User_inputs.HP_STRT + SA_angle
    SA_Com("move", Yaw)
    Roll = User_inputs.HP_FLAT + ZB_angle
    ZB_Com("dev_HP", "move abs", Roll, option="wait")
    time.sleep(2) #Delay for vibration dampening
# Moves the NMR probe into measurement position
def Move_Two():
    SA_Com("move", User_inputs.HP_STRT)
    ZB_Com("dev_HP", "move abs", User_inputs.HP_FLAT, option="wait")
    ZB_Com("dev_X", "move abs", User_inputs.X_CTR)
    ZB_Com("dev_Y", "move abs", User_inputs.Y_CTR)
    ZB_Com("dev_Z", "move abs", User_inputs.Z_CTR)
    ZB_waitall()
    time.sleep(2) #Delay for vibration dampening
# Checks temperature, and powers on or off the power supply, and tunes the NMR teslameter afterwards
def Update_System(dac, polarity):
    #Only last part of code is needed since Water cooler fix.
    #Different power settings have different thresholds for "hot", this is done to maximize the runtime
    #for example, running at 45000 DAC, we allow temps to go up till 29°C
    #as that would allow enough time to finish at least one set of measurements
    #while running at 200000 DAC, we should cool down sooner, at 27°
    if EPICS.Check_Temp('water') >= User_inputs.PS_HOT(dac):
        print("Water temperature too hot, cooling down...")
        EPICS.Power_OFF()
        while EPICS.Check_Temp('water') >= User_inputs.PS_COOL: # Waits until the water temperature is below predefined values in User_inputs.py module
            time.sleep(300) # check again every 5 mins
            print(time.strftime("%H:%M:%S")) # shows it is not frozen
    if User_inputs.IS_ON == False or User_inputs.REQUEST: # Only when the power supply is off, or a new setting is requested, will it call Power_ON function
        Choose_Probe(dac)
        NMR_Remote(dac, polarity)
        EPICS.Power_ON(dac, polarity)   # Power_ON() will update to the new dac value if PS is already running. It will reset first if a change in polarity is ordered
        NMR_Tune(dac) #Tunes the NMR Teslameter for given power supply DAC
# The main Function that starts by asking user whether devices need to be homed. Then it goes through with calibration, and finally returns to safe position before ending
def main():
    #Connects and opens ports to the main devices
    print("Connecting all ports and setting HP ADC SP scan settings...")
    print("\n")
    try:
        NMR.open()
        ZB.open()
        SA.connect((User_inputs.SA_IP, User_inputs.SA_PORT))
    except:
        print("failed to connected to SmarAct, Zaber or NMR devices! Please check connections and try again!")

    #Shows some User inputs for User to confirm
    print("Please confirm the following user_input parameters:")
    print("Current Run Tag: ", User_inputs.CUR_TAG)
    print('\n')
    print("Center X: ", User_inputs.X_CTR)
    print("Center Y: ", User_inputs.Y_CTR)
    print("Center Z: ", User_inputs.Z_CTR)
    print('\n')
    print("Power supply DAC sequence: ", User_inputs.PS_SEQ)
    print("Polarity: ", User_inputs.PS_POLAR)
    print("Hall Probe to Calibrate: ", User_inputs.HP_PROB)
    print('\n')
    print("SmarAct Rotation Sequence: ", User_inputs.SA_ANGLES)
    print("Zaber Rotation Angles: ", User_inputs.ZB_ANGLES)
    print("Enter anything to continue...")
    input()
    os.system('cls')
    now = datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y")
    run_details = ('Run Type: Main\n'
                   'Start Time: %s\n'
                   'Power Supply DAC: %s\n'
                   'Power Supply Polarity: %s\n'
                   'Hall Probes: %s\n'
                   'Zaber Angles: %s\n'
                   'SmarAct Angles: %s\n' % (
                       now, User_inputs.PS_SEQ, User_inputs.PS_POLAR, ', '.join(User_inputs.HP_PROB),
                       User_inputs.ZB_ANGLES, User_inputs.SA_ANGLES))
    data_dir = User_inputs.CREATE_TAG(run_details) #Creates a folder for this run, and returns the address to that folder

    #Configures the Hall Probe ADC to 100 data points each an average of 10 readings.
    EPICS.Config_HP()
    #Creates polarity array
    polarity = Polarity_Order(User_inputs.PS_POLAR)
    print("Would you like to HOME Zaber and SmarAct devices? (y/n)")
    print("Devices need to be HOMED at least ONCE after powered ON")
    if input().lower() == "y":
        print("Homing all devices please wait...")
        time.sleep(1)
        Home_All()
    print("All Devices ready, make sure Power Supply Breaker is flipped ON")
    print("Enter anything to begin calibrations...")
    input()
    os.system('cls')

    #Writes the initial line to data file
    data_file = data_dir + User_inputs.CUR_TAG + 'Summary.txt'
    with open(data_file, 'a+') as file:
        file.write(( #Line is too long for python and must be broken
                   "PS_DAC\t\t\t\tPolarity\t\t\t\tPROBE\t\t\t\tZB_angle[°]\t\t\t\tSA_angle[°]\t\t\t\t"
                   "NMR_field[T]\t\t\t\tX_probe[V]\t\t\t\tY_Probe[V]\t\t\t\tZ_Probe[V]\t\t\t\t"
                   "Prb_Temp[°C]\t\t\t\tBox_Temp[°C]\t\t\t\tAir_Temp[°C]\n"))

    for pol in polarity:
        for HP in User_inputs.HP_PROB:
            print("Moving to start position for %s probe" % HP)
            To_Ready(HP)
            for dac in User_inputs.PS_SEQ:
                print("Selecting NMR Probe and Configuring Teslameter for Remote Mode...")
                ## REQUEST flag is set true so that Check_Status() will run Power_ON() again even if the power supply is already running
                # This is helpful when we have multiple power supply DAC settings
                User_inputs.REQUEST = True
                print("Configuring Power Supply dac and polarity...")
                ## REQUEST true means that a new polarity or dac setting is requested
                Update_System(dac, pol)  #Updates PS and NMR to the new dac. Changes NMR probe if necessary
                User_inputs.REQUEST = False  ## REQUEST variable may be outdated, since we no longer need to check temperatures after chiller fix
                #Goes through the given rotation angles
                for SA_angle in User_inputs.SA_ANGLES:
                    for ZB_angle in User_inputs.ZB_ANGLES:
                        Move_One(HP, SA_angle, ZB_angle)    #Moves to HP measuring position
                        [x, y, z, b, p] = EPICS.Rec_HP(data_dir, probe=HP, option='return_ave')  #Records HP ADC values for x y z probe, box and probe temperature
                        Move_Two()  #Moves to measure teslameter
                        nmr = NMR_read(data_dir, probe=HP, option='return')  #Records Teslameter values
                        Air_Temp = EPICS.Check_Temp()
                        with open(data_file, 'a+') as file:
                            file.write("%d\t\t\t\t%s\t\t\t\t%s\t\t\t\t%f.2\t\t\t\t%f.2\t\t\t\t%s"
                                       "\t\t\t\t%f\t\t\t\t%f\t\t\t\t%f\t\t\t\t%f\t\t\t\t%f\t\t\t\t%f\n"
                                       % (dac, pol*2 - 1, HP, ZB_angle, SA_angle, nmr, x, y, z, p, b, Air_Temp))
                #Checks temperature and determines whether to power down and wait, or continues
                Update_System(dac, pol)
        Move_Out()  # This will ensure the devices knows how to enter into another HP start position, eg. X -> Y
    NMR_local()
    EPICS.Power_OFF()
    Safe_Pos()

    print("Scan program finished!")
    now = datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y")
    User_inputs.CLOSE_TAG(now)
    sys.exit()

if __name__ == "__main__":
    main()
