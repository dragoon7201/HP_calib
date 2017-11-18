import User_inputs
import datetime
import time

polarity = [1, 2, 3]
Probes = ['X', 'Y', 'Z']
PS = 123
now = datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y")

run_details = ('Run Type: Zeroing\n'
               'Start Time: %s\n'
               'Power Supply DAC: %d\n'
               'Power Supply Polarity: %s\n'
               'Hall Probes: %s\n'
               'Zaber Angles: %s\n'
               'SmarAct Angles: %s\n' % (
                   now, PS, polarity,
                   ', '.join(Probes),
                   User_inputs.ZB_ANGLES, User_inputs.SA_ANGLES))
# Creates a folder for this run, and returns the address to that folder
data_dir = User_inputs.CREATE_TAG(run_details)