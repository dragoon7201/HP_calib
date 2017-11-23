import os
import numpy as np
CUR_DIR = os.path.dirname(__file__)
#The CUR_TAG variable is a permanent counter ranging from 0 - 46655 (base 36)
#The counter is used to group files that were produced in a single run, and so the counter is incremented each time a main scan or zeroing scan is started.
CUR_TAG = "006" #Make sure the only double quotation marks on this line are the ones around the 3 character TAG values
user_file = CUR_DIR + "\\Run_settings.txt"
hardware_file = CUR_DIR + "\\Hardware_settings.txt"
#Reading the user_inputs, both hardware and run
with open(user_file, 'r') as source:
    run_line = [x.strip('\n') for x in source.readlines()]
with open(hardware_file, 'r') as source:
    hardware_line = [x.strip('\n') for x in source.readlines()]
#Assigning them to constants used by other modules
ZB_PORT = hardware_line[1]
NMR_PORT = hardware_line[3]
SA_IP = hardware_line[5]
SA_PORT = int(hardware_line[7])
SA_CH = hardware_line[9]
X_CTR = float(hardware_line[11])
Y_CTR = float(hardware_line[13])
Z_CTR = float(hardware_line[15])
NMR_P2 = float(hardware_line[17])
NMR_P4 = float(hardware_line[19])
NMR_P5 = float(hardware_line[21])
ZB_ZERO = [float(x) for x in hardware_line[23].split(',')]
SA_ZERO = [float(x) for x in hardware_line[25].split(',')]
PAIR_FILE = CUR_DIR + '\\' + hardware_line[27]
HEAT = int(hardware_line[29])

PS_SEQ = [int(x) for x in run_line[1].split(',')]
PS_POLAR = run_line[3]
HP_PROB = run_line[5].upper().replace(' ', '').split(',')
DATA_DIR = run_line[7]
if not os.path.exists(DATA_DIR): # Makes the data directory if it is not already there
    os.makedirs(DATA_DIR)

SA_ANGLES = [float(x) for x in run_line[9].split(',')]
SA_ANGLES = np.around(np.arange(SA_ANGLES[0], SA_ANGLES[1] + 0.01, SA_ANGLES[2]), 2).tolist() # adding 0.01 to max angle so that it may include itself in the range
ZB_ANGLES = [float(x) for x in run_line[11].split(',')]
ZB_ANGLES = np.around(np.arange(ZB_ANGLES[0], ZB_ANGLES[1] + 0.01, ZB_ANGLES[2]), 2).tolist()
PS_Wait_Time = int(run_line[13])
###############################################################
#Reading power supply to NMR pairing file
with open(PAIR_FILE, 'r') as source:
    pairing = [x.strip('\n').split('\t\t')[:3] for x in source.readlines()[1:]] #we are just interested in the first 3 columns after row 1
PS_NMR = {int(x): (int(y), z) for x, y, z in pairing} #creates a dictionary that is used for choosing NMR probe and tuning
##############################################################

PS_COOL = 26 #Not used, but kepted just incase

#Global variables used by other modules for keeping track of things
HP_STRT = 0
HP_FLAT = 0
REQUEST = False
IS_ON = False
NMR_TUNE_Limit = 7

#This is a function that finds the variable Curr_TAG in User_inputs.py and adds one to the value for keeping permanent count
#This way scan files from one single batch can be grouped together independent of date time
def TAG_Update():
    content = []
    inx = 0
    Found_TAG = False
    tally = 0
    power = 2
    with open(__file__, 'r') as f:
        for line in f:
            content.append(line)
            if line.find("CUR_TAG = ") == 0:
                inx = len(content) - 1 # it will be the most recently appended index
                Found_TAG = True
    if not Found_TAG:
        print("Cannot find the CUR_TAG Variable...continuing without TAG update")
        return
    old_tag = content[inx].partition('\"')[-1].rpartition('\"')[0]
    for x in old_tag:
        if ord(x) < 58:
            tally += (ord(x) - 48)*(36**power)
        else:
            tally += (ord(x) - 55)*(36**power)
        power -= 1
    tally += 1
    new_tag = ""
    P1,tally = divmod(tally, 36**2)
    P2,tally = divmod(tally, 36)
    P3,tally = divmod(tally, 1)

    for x in [P1, P2, P3]:
        if x > 9:
            new_tag += chr(x + 55)
        else:
            new_tag += chr(x + 48)
    content[inx] = content[inx].replace(old_tag, new_tag)
    with open(__file__, 'w') as f:
        for line in content:
            f.write(line)

def PS_HOT(dac):
    # a number to approximate the "quickness" of overheating, higher value is sooner
    return 30 - (dac * HEAT/10000000)
#Appends to TAG file, and creates TAG directory
def CREATE_TAG(details):
    with open(DATA_DIR + '\\RUN_LOG.txt', 'a+') as log:
        description = input('Please enter a brief description for this run\n')
        if os.stat(DATA_DIR + '\\RUN_LOG.txt').st_size > 0:
            newlines = '\n\n'
        else:
            newlines = ''
        log.write('%sTAG%s description: %s\n' % (newlines, CUR_TAG, description))
        log.write(details)
    if not os.path.exists(DATA_DIR + '\\' + CUR_TAG):
        os.makedirs(DATA_DIR + '\\' + CUR_TAG)
    return DATA_DIR + '\\' + CUR_TAG + '\\'

def CLOSE_TAG(details):
    with open(DATA_DIR + '\\RUN_LOG.txt', 'a+') as log:
        log.write('Run complete! %s\n' % details)

    import Email
    files = [DATA_DIR + '\\RUN_LOG.txt',
             DATA_DIR + '\\' + CUR_TAG + '\\' + CUR_TAG + '_Summary.txt']
    Email.send_mail('sunny.lu@lightsource.ca', 'sunny.lu.sl@gmail.com', 'attch1', 'hello!', files)
    TAG_Update()
