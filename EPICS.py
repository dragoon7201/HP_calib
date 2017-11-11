from epics import PV
import time, User_inputs, os
import paramiko, sys
import datetime
## EPICS module contains functions that has to do with getting or putting EPICS PV values

#########################      Some Constants      ####################################
#Connects to the Linux computer via Paramiko SSH
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.load_system_host_keys()
host = "opi1504-103.clsi.ca"
usrname = "magmap"
password = "w1gg13"
SCRIPTS = { #Names of the scripts located on Linux Machine 1504-103 /home/magmap/HP_calib_scripts
            # NOTE caget and caput commands in the scripts are full paths. Due to paramiko not sharing the same $PATH
            # we cannot call caget and caput directly.
    "change polarity": "./Change_Polarity",
    "power on": "./Power_On",
    "set dac": "./Set_Dac ",
    "reset": "./Reset",
    "HP config": "./HP_ADC_config",
    "HP scan": "./HP_SP_Scan",
    "Record": "./Read_HP_PV"
}
## Defines the EPICs PV names
TM_h2o = PV("TM1504-1-06")
TM_room = PV("TM1504-1-01")
PS_onoff = PV("PS1504-01:onoff")
PS_polarity = PV("PS1504-01:polarity")
PS_dac = PV("PS1504-01:dac")
PS_adc = PV("PS1504-01:adc")
PS_reset = PV("PS1504-01:reset")
HP_xdata = PV("HP1504-01:xData")
HP_ydata = PV("HP1504-01:yData")
HP_zdata = PV("HP1504-01:sData")
HP_box_tm = PV("HP1504-01:TM:box")
HP_probe_tm = PV("HP1504-01:TM:probe")


########################################################################################

# Checks water temperature, temperture monitor is probe #6, attached on the water pipes
def Check_Temp():
    T = TM_room.get(as_numpy=True)
    return T
# Using Paramiko addon, we can logon to the linux machien as wiggle user, and put commands related to EPICS PV's
# Since being on the Windows computer only allows us to READ PV values, and not PUT them. So we have to PUT values through this means
# All actual commands are done by scripts written on the Linux machine it self. Scripts are located in /home/magmap/HP_calib_scripts
def EPIC_send(cmd, amount=''):
    pre_cmd = "cd ~/HP_calib_scripts; "
    if cmd == "set dac":
        send = pre_cmd + SCRIPTS[cmd] + str(amount)
    else:
        send = pre_cmd + SCRIPTS[cmd]
    #channel is used instead of just ssh.exec_command as channel can receive exit code
    channel = ssh.get_transport().open_session()
    channel.exec_command(send)
    exitcode = channel.recv_exit_status()
    if exitcode == 1:
        print("script error occurred (probably a timeout error)")
        if User_inputs.IS_ON:
            print("powering off PS")
            Power_OFF()
        print("Blocking script from continuing, enter anything to exit")
        input()
        sys.exit()
# Function relating to setting power supply dac, changing polarity and powering on of the Power Supply
# All actual commands are done by scripts written on the Linux machine it self. Scripts are located in /home/magmap/HP_calib_scripts
def Power_ON(dac, polarity):
    print("Powering up to %d dac and %s polarity" % (dac, '+' if polarity > 0 else '-'))
    am_i_on = PS_adc.get()
    current_pol = PS_polarity.get(as_numpy=True)
    print("current adc %d and polarity %d" % (am_i_on, current_pol))
    ssh.connect(hostname=host, username=usrname, password=password)
    if current_pol != polarity:
        EPIC_send("reset")

        EPIC_send("change polarity")

    EPIC_send("set dac", amount=dac)
    EPIC_send("power on") # Script will ignore this command if it is already powered on
    ssh.close()
    User_inputs.IS_ON = True
    print("Power Supply powered ON, waiting %d mins %d secs for field stabilization..." % divmod(User_inputs.PS_Wait_Time, 60))
    time.sleep(User_inputs.PS_Wait_Time)
## Sends the command to run HP_Config script on Linux machine. Which has precoded settings
def Config_HP():
    print("Configuring HP SP settings, 100 data points, 10 averages per data point and 0.1 sec interval")
    # Note if SP configurations need to be altered
    # Please go to script file HP_Config in /home/magmap/HP_calib_scripts/
    # As that is the script with all the actual parameters, this function here merely runs that script
    ssh.connect(hostname=host, username=usrname, password=password)
    EPIC_send("HP config")
    ssh.close()
## IMPORTANT, reading data from HP can no longer be accomplished using epic.PV.get().
## The network permission has changed since the old IOC was replaced. Therefore, use Rec_HP_Alt() instead.
## Sends command to start SP scan. And then Reads the PV's that contain results and writes those to file
## Function also sorts collected data into different folders based on run mode and senis probe inputs.
def Rec_HP_OBSOLETE(run_mode, probe, option=''):
    print("Recording Hall Probe measurement values...")
    now = datetime.datetime.now()
    filename = now.strftime("%Y-%m-%d_%Hh%Mm%Ss_SPscan") # Format of files created
    data_dir = User_inputs.HP_DATA # parent folder for hp sp scan
    if run_mode == "main":  # sub folders
        data_dir += "/Main" + "/" + probe
    elif run_mode == "secondary":
        data_dir += "/Secondary" + "/" + probe
    elif run_mode == "zeroing":
        data_dir += "/Zeroing" + "/" + probe
    if not os.path.exists(data_dir): # Makes a new directory if one does not exist already
        os.makedirs(data_dir)
    time.sleep(0.1)
    ssh.connect(hostname=host, username=usrname, password=password)
    EPIC_send("HP scan")
    time.sleep(0.5)
    x_reading = HP_xdata.get(as_numpy=True)
    y_reading = HP_ydata.get(as_numpy=True)
    z_reading = HP_zdata.get(as_numpy=True)
    box_temp = HP_box_tm.get(as_numpy=True)
    prob_temp = HP_probe_tm.get(as_numpy=True)
    with open(data_dir + "/" + filename + ".txt", 'w') as file:
        file.write("X, Y, Z, Box_t, probe_t\n")
        for i in range(0,len(x_reading)):
            file.write(str(x_reading[i]) + ', ')
            file.write(str(y_reading[i]) + ', ')
            file.write(str(z_reading[i]) + ', ')
            file.write(str(box_temp[i]) + ', ')
            file.write(str(prob_temp[i]) + '\n')
    if option == 'return_ave': # returns the averages for real-time plotting purposes
        x_avg = sum(x_reading) / float(len(x_reading))
        y_avg = sum(y_reading) / float(len(y_reading))
        z_avg = sum(z_reading) / float(len(z_reading))
        return [x_avg, y_avg, z_avg]

# The alternative HP record function is used if, for some reason, the HP PVs cannot be read. This has occurred once, when the rack computers were swapped for newer ones.
def Rec_HP(run_mode, probe, option=""):
    # The difference between Rec_HP() and the OBSOLETE alternative, is that this one does not read the PV's directly. PV access to the IOC has been restricted to the 10.51 VLAN since new PLC
    # Using ssh should be a little slower, but should be no big deal.
    # The data format and file name are organized the same way in both functions.
    print("Recording Hall Probe measurement values...")
    now = datetime.datetime.now()
    filename = now.strftime("%Y-%m-%d_%Hh%Mm%Ss_SPscan")  # Format of files created
    data_dir = User_inputs.HP_DATA  # parent folder for hp sp scan
    if run_mode == "main":  # sub folders
        data_dir += "/Main" + "/" + probe
    elif run_mode == "secondary":
        data_dir += "/Secondary" + "/" + probe
    elif run_mode == "zeroing":
        data_dir += "/Zeroing" + "/" + probe
    if not os.path.exists(data_dir):  # Makes a new directory if one does not exist already
        os.makedirs(data_dir)
    time.sleep(0.1)
    ssh.connect(hostname=host, username=usrname, password=password)
    EPIC_send("HP scan")    #Starts a scan
    time.sleep(1)
    stdin, stdout, stderror = ssh.exec_command('cd ~/HP_calib_scripts; ./Return_HP_reading') #grabs result from scan, stored in stdout variable
    raw_data = stdout.readlines()  # returns a list that includes all results bunched together that needs partitioning
    ssh.close()

    parsed_data = raw_data[0].split(',')  # separates the X, Y, Z, Box_Temp and PRB_Temp into their own list
    X_data = parsed_data[0].split(' ')  # separates each data point and creates an array
    Y_data = parsed_data[1].split(' ')
    Z_data = parsed_data[2].split(' ')
    Box_T = parsed_data[3].split(' ')
    Prb_T = parsed_data[4].split(' ')
    with open(data_dir + "/" + filename + ".txt", 'w') as file: #writes data to a txt file
        file.write("X, Y, Z, Box_T, Probe_T\n")
        for i in range(1, len(X_data)): # we skip point 0 as that is an integer telling us how many data points there are
            file.write(str(X_data[i]) + ', ')
            file.write(str(Y_data[i]) + ', ')
            file.write(str(Z_data[i]) + ', ')
            file.write(str(Box_T[i]) + ', ')
            file.write(str(Prb_T[i]) + '\n')

    if option == "return_ave":
        X_data = [float(i) for i in X_data]  # converts str entry into floats, result array format [# of data points, data1, data2, data3, .... data100]
        Y_data = [float(i) for i in Y_data]
        Z_data = [float(i) for i in Z_data]
        Box_T = [float(i) for i in Box_T]
        Prb_T = [float(i) for i in Prb_T]

        Ave_X = sum(X_data[1:]) / X_data[0] # first cell holds the number of data points
        Ave_Y = sum(Y_data[1:]) / Y_data[0]
        Ave_Z = sum(Z_data[1:]) / Z_data[0]
        Ave_Box = sum(Box_T[1:]) / Box_T[0]
        Ave_Prb = sum(Prb_T[1:]) / Prb_T[0]

        return Ave_X, Ave_Y, Ave_Z, Ave_Box, Ave_Prb


## Power down the Power supply
def Power_OFF():
    print("Power down Power supply")
    ssh.connect(hostname=host, username=usrname, password=password)
    EPIC_send("reset")
    ssh.close()
    User_inputs.IS_ON = False
