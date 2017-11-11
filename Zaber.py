## This module contains functions related to moving the Zaber devices
import serial, User_inputs,time
step_mm = 1.00 / 0.00009921875 #mm to device step units
step_dg = 1.00 / 0.000234375 #degrees to device step units

ZB = serial.Serial()
ZB.port = User_inputs.ZB_PORT
ZB.baudrate = 115200
ZB.timeout = 0.5


Devices = { #Maps devices to numbers that Zaber understands, note if wire connections are changed, the numbers would probably change as well
    "dev_X": 1,
    "dev_Y": 3,
    "dev_Z": 2,
    "dev_NMR": 5,
    "dev_HP": 4
}
# General command sending function that talks to Zaber devices
def ZB_Com(device, command, amount = "", option = ""):
    #option defaults to '', which does nothing, 'read' option prints device response to command
    #option 'wait' waits until device is done movement before continuing
    #option 'both' will do both
    if amount != "":
        if Devices[device] > 3:  # device 4, and 5 are rotary hence must use step_dg conversion
            amount = float(amount)*step_dg
        else:
            amount = float(amount)*step_mm
        amount = " " + str(round(amount)) # amount is now in whole numbered device step units

    cmd = "/" + str(Devices[device]) + " 0 " + command + amount + "\n"
    ZB.reset_input_buffer()     #Input and output buffers should be reset before writing to serial
    ZB.reset_output_buffer()    #That way commands don't get mixed up, otherwise devices seems to get confused
    ZB.write(cmd.encode())  #encoding uses "utf-8" by default
    if option != "":
        reply = ZB.readline().decode()
        if option == 'read' or option == 'both':
            print(reply)
            return reply
        if option == 'wait' or option == 'both':
            while "IDLE" not in reply:
                ZB.reset_input_buffer()
                ZB.reset_output_buffer()
                ZB.write(("/" + str(Devices[device]) + "\n").encode())
                reply = ZB.readline().decode()

# Specific function that checks all Zaber devices status until they are all IDLE
def ZB_waitall():

    device1 = "/1\n"
    device2 = "/2\n"
    device3 = "/3\n"
    device4 = "/4\n"
    device5 = "/5\n"

    ZB_devices = [device1, device2, device3, device4, device5]
    reply2 = ""
    for x in ZB_devices:
        ZB.reset_input_buffer()
        ZB.reset_output_buffer()
        ZB.write(x.encode())
        reply2 += ZB.readline().decode()
    while "BUSY" in reply2:
        reply2 = ""
        for x in ZB_devices:
            ZB.reset_input_buffer()
            ZB.reset_output_buffer()
            ZB.write(x.encode())
            reply2 += ZB.readline().decode()