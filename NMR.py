# This module contains functions that communicate with the NMR Teslameter
import serial, User_inputs, time, os
Default = User_inputs.CUR_TAG + "_NMR_readings.txt"
NMR = serial.Serial()
NMR.baudrate = 2400
NMR.port = User_inputs.NMR_PORT
NMR.parity = serial.PARITY_NONE
NMR.stopbits = serial.STOPBITS_ONE
NMR.bytesize = serial.EIGHTBITS
NMR.timeout = 0.5

# Sends Enquiry command, and recieves the NMR readings, then records the value to a file called NMR_readings.txt
# in the Directory defined by user
def NMR_read(data_dir, probe, filename = Default, option = ''):
    if option == '':
        print("Recording NMR measurement values...")
    NMR.write(b'\5')
    time.sleep(0.5)
    raw_ascii = NMR.readline()
    if len(raw_ascii) == 0:
        print("Please check cable connection and turn on/off Tesla meter!")
    decoded_value = raw_ascii.decode().strip('\r\n')
    if decoded_value[0] == "L":
        decoded_value = decoded_value[1:len(decoded_value) - 1] # Removes the front 'L' character and '\n\r' at the end
    else:
        decoded_value = "No Lock"

    file_dir = data_dir + probe
    if not os.path.exists(file_dir):  # Makes a new directory if one does not exist already
        os.makedirs(file_dir)
    time.sleep(0.1)

    with open(data_dir + filename, "a+") as NMR_file:
        NMR_file.write(decoded_value + "\n")
    time.sleep(1)

    if option == 'return':
        return str(decoded_value) # We want to return string, so that when writing to file, we won't have to worry about whether the data is float or "No Lock".
# Sets up the NMR for remote mode, selects probe number, polarity, depending on Power Supply Dac and polarity.
# Option codes are found in the PT2025 manual under R232 communications chapter
def NMR_Remote(PS_dac, polarity):
    NMR.write("R".encode()) #Remote mode
    time.sleep(0.5)
    NMR.write("D1".encode()) #Tesla mode
    time.sleep(0.5)
    NMR.write("A1".encode()) #Automatic mode
    time.sleep(0.5)
    probe = 'P' + User_inputs.PS_NMR[PS_dac][1] #Turns on the appropriate channels. E for probe 2, F probe 4, G probe 5
    NMR.write(probe.encode())
    time.sleep(0.5)
    set_polar = "F"         # Sets NMR polarity
    if probe == 'PE':
        polarity += 1       #Because Probe 2 was installed backwards, so NMR polarity must be set opposite to PS polarity
    if polarity%2 == 0:
        set_polar += "0"    # 0 for negative
    else:
        set_polar += "1"    # 1 for positive
    NMR.write(set_polar.encode())
    time.sleep(1)
# Tunes the NMR around predetermined dac settings which is mapped for various power Supply outputs
# If the pre-set dac is too high or too low, the function will call itself again with +/- offset values
def NMR_Tune(PS_dac, offset = 0, tries = 0):
    if tries >= User_inputs.NMR_TUNE_Limit:
        print("PS DAC of %d cannot be successfully locked in after %d tries! Please check the paring file %s to see if the numbers are still right, or check the Teslameter connecting cables." % (PS_dac, tries, User_inputs.PAIR_FILE))
        return False
    if PS_dac in User_inputs.PS_NMR.keys():
        target = User_inputs.PS_NMR[PS_dac][0] + offset
        print("Setting NMR DAC to %d for PS DAC of %d" % (target, PS_dac))
        cmd = "C" + str(target) + '\r\n'
        NMR.write(cmd.encode())
        time.sleep(10) #Wait 10 secs for a lock-on
        NMR.write("S1".encode()) #Reads status 1 back (includes information on field lock)
        reply = NMR.readline().decode()
        #These are the replies that mean field lock signal
        #I am not sure what the conversions are, but code works. Maybe hexidecimal representation of binary bits? Table available https://en.wikipedia.org/wiki/Hexadecimal
        if reply[1] == '2' or reply[1] == '3' or reply[1] == '6' or reply[1] == '7':
            print("Field Locked")
            NMR.write("S2".encode()) #Reads status 2 back (includes information on field too low or too high)
            reply = NMR.readline().decode()
            #These are the replies that mean the 'TOO LO' led is lit
            if reply[2] == '9' or reply[2] == 'D' or reply[2] == '1' or reply[2] == '5':
                print("Dac set point too low")
                NMR_Tune(PS_dac, offset + 25, tries + 1)
            #These are the replies that mean the 'TOO HI' led is lit
            elif reply[2] == 'S' or reply[2] == 'E' or reply[2] == '2' or reply[2] == '6':
                print("Dac set point too high")
                NMR_Tune(PS_dac, offset - 25, tries + 1)
        else:
            print("No field lock! This may mean the cable connections are loose or that the preset NMR DAC values are wrong! Please verify!")
            return False
    else:
        print("Given dac setting not predefined in dictionary!")
        print("No NMR to PS DAC pairings found for PS DAC of %d! please check the pairings file %s and try again!" % (PS_dac, User_inputs.PAIR_FILE))
        return False
    return True
#Returns NMR to manual mode
def NMR_local():
    print("Returning NMR setting to local")
    NMR.write("L".encode())
    time.sleep(0.5)

#Returns the DAC value of the NMR
def Read_DAC():
    NMR.write("S4".encode())
    time.sleep(1)
    dac = NMR.readline().decode().strip('\r\n')[1:]
    #Returned values are in base 16
    return int(dac, 16)
