# This module contains a function that calculates the amount of corrections needed in X Y and Z in order keep the senis probe at the same position after rotating

import math
import numpy
####################################################################################################################
#The idea being this:
#The assumed point of measurement for the teslameter's NMR probe, is the reference point in which we try to move the senis probe there when preforming the SP scan.
#Thus we must correct for the distance between the assumed point of measurement on the NMR probe, to that of the senis probe.
#This way any spatial fluctuations in field uniformity is reduced. While we do gain some temporal fluctuations, it is not significant.
#As the time it takes to move the devices between NMR measuring position and Senis measuring position is quite irrelevant.

####################################################################################################################

# Some measured physical constants. Some are measured to approximation, while others are known from device manuals.
NMR_to_COR = [-15, -28.5, 2.5] # Distance between the Center of Rotation to the "assumed point of measurement" on the teslameter's NMR probe (arbitrary point)
#Below are distances measured between each senis probe to the Center of Rotation (COR) at their respective starting positions ie. (0° SA, 0° ZB)
X_to_COR = [[3.0], # For example, at the starting position of the X senis probe,
            [1.2], # it is 3mm inward in X direction, 1.2 mm downward in Y direction and 2mm rightward in the Z direction
            [-2.0]]# Compared to the center of rotation
Y_to_COR = [[3.0],
            [0.0],
            [1.2]]
Z_to_COR = [[2.0],
            [1.2],
            [-3.0]]
N_to_COR = [[0],## This is neutral position, basically the center of the hall sensor chip. It only has a y distance from the center of rotation
            [1.2],
            [0]]
# Depending on which device is moved, and the angle to be moved
# Returns a tuple containing the correction amounts in each axis
def Trig(probe, SA_angle = 0.0, ZB_angle = 0.0):

    #python math trig functions only work with radians angles
    RAD_SA = math.radians(SA_angle)
    RAD_ZB = math.radians(ZB_angle)

    #The following are rotation matrix. Source can be found on wikipedia. Note that the sine angles are negatives, as all rotations are CW from the perspective of our defined axis
    Rz = [
        [math.cos(RAD_SA), math.sin(RAD_SA), 0],
        [-math.sin(RAD_SA), math.cos(RAD_SA), 0],
        [0, 0, 1]
    ]
    Ry = [
        [math.cos(RAD_SA), 0, -math.sin(RAD_SA)],
        [0, 1, 0],
        [math.sin(RAD_SA), 0, math.cos(RAD_SA)]
    ]
    Rx = [
        [1, 0, 0],
        [0, math.cos(RAD_ZB), math.sin(RAD_ZB)],
        [0, -math.sin(RAD_ZB), math.cos(RAD_ZB)]
    ]

    if probe == "Y":
        rot_matrx = numpy.matmul(Rx, Rz)
        offset = numpy.matrix(numpy.matmul(rot_matrx, Y_to_COR)).A1 # Returns an array which contains offsets for (x , y, z) axis
    elif probe == "X": # X and Z are calculated the same way, as one is the other rotated 90 degrees
        rot_matrx = numpy.matmul(Rx, Ry)
        offset = numpy.matrix(numpy.matmul(rot_matrx, X_to_COR)).A1
    elif probe == "Z":
        rot_matrx = numpy.matmul(Rx, Ry)
        offset = numpy.matrix(numpy.matmul(rot_matrx, Z_to_COR)).A1
    else:
        rot_matrx = numpy.matmul(Rx, Ry)
        offset = numpy.matrix(numpy.matmul(rot_matrx, N_to_COR)).A1
    #return offset
    return (NMR_to_COR[0] + offset[0], NMR_to_COR[1] + offset[1], NMR_to_COR[2] + offset[2]) # returns the total amount needed for correction

