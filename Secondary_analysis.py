import os
import math

#path = r'C:\Users\lus\Desktop\Secondary2'

for dir in os.listdir(path): # goes into X, Y ,Z
    dir = path + "\\" + dir
    if os.path.isdir(dir):
        for subdir in os.listdir(dir): # does into -90, 0, 90, 180 folders
            subdir = dir + "\\" + subdir
            if os.path.isdir(subdir):
                X = []
                Y = []
                Z = []

                for file in os.listdir(subdir): # goes into each file
                    file = subdir + "\\" + file
                    x_sum = 0
                    y_sum = 0
                    z_sum = 0
                    with open(file, 'r') as f:
                        lines = [x.strip("\n") for x in f.readlines()]
                        for i in range(1, len(lines)):
                            x_sum += float(lines[i].split(',')[0])
                            y_sum += float(lines[i].split(',')[1])
                            z_sum += float(lines[i].split(',')[2])
                    X.append(x_sum/100)
                    Y.append(y_sum/100)
                    Z.append(z_sum/100)

            result_name = subdir + "_result.txt"
            with open(result_name, 'w+') as r:
                r.write("X, Y, Z\n")
                for i in range(0, len(X)):
                    r.write(str(X[i]) + ", " + str(Y[i]) + ", " + str(Z[i]) + "\n")
