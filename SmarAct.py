# This module contains functions related to communicating with the SmarAct Device
import socket, User_inputs, time
IP_PORT = (User_inputs.SA_IP, User_inputs.SA_PORT)
SA = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SA.settimeout(0.5)

# Maps common commands into what SmarAct Device understands
CMDS = {
        "reset": "R",
        "sync": "SCM0", # 0 is for synchronous commands, which replies after receiving commands
        "enable_sensor": "SSE1", # 1 is for Enabled
        "set_type": "SST" + User_inputs.SA_CH + ",8", # 8 is for the type of sensor that our device has
        "home": "FRM" + User_inputs.SA_CH + ",3,0,0",   # 3 corresponds to rotating CCW first to find home, 0 and 0 means it applys 0 hold force, and holds for 0 seconds
        "move": "MAA" + User_inputs.SA_CH + ","
        }
#SmarAct communication function, encodes and sends commands to the device
def SA_Com(command, amount = "", option = ""):
    cmd = ":"
    if amount != "":
        amount = MAA_Calc(amount)
    cmd += CMDS[command] + amount + "\n"
    SA.send(cmd.encode())
    time.sleep(0.5)
    reply = SA.recv(2048)
    if option == "read":
        print(reply.decode())
    time.sleep(1)
# Takes the movement commands and depending on whether the movement will end up as a positive or negative angle with respect to SmarAct's own 0 Angle
# MAA can only take positive angle arguments, so to move to a negative angle, you have to pass -1 to rotation arguement, and add 360 degrees to the negative angle
# The last argument of 0 is how many seconds to hold. Which is not needed
def MAA_Calc(amount):
    amount *= 1000000
    amount = round(amount)
    if amount > 0:
        return str(amount) + ",0,0" # here the 0 means
    else:
        return str(amount + 360000000) + ",-1,0"
