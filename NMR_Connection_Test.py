import serial, time
from User_inputs import NMR_PORT
#### SECTION connects NMR Devices and sets some of the connection parameters ####
NMR = serial.Serial()
NMR.baudrate = 2400
NMR.port = NMR_PORT
NMR.parity = serial.PARITY_NONE
NMR.stopbits = serial.STOPBITS_ONE
NMR.bytesize = serial.EIGHTBITS
NMR.timeout = 0.5
NMR.open()
################################################################################
while True:
    NMR.write(b'\5') #byte 5 is the ENQ ascii character
    time.sleep(0.5)
    raw_ascii = NMR.readline()
    if len(raw_ascii) == 0: # device reply is 0 length string, that means connection is bad
        print("Please check cable connection and turn on/off Tesla meter!")
    decoded_value = raw_ascii.decode().strip('\r\n')
    print(decoded_value)
    time.sleep(0.5)