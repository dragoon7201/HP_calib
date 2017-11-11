import os
import math
import matplotlib.pyplot as plt
path = input('Please enter the folder of the zeroing scans\n')
X = []
Y = []
Z = []
for file in os.listdir(path):
    if file.endswith(".txt"):
        file = path + "\\" + file
        x_sum = 0
        y_sum = 0
        z_sum = 0
        with open(file, 'r') as x:
            lines = [w.strip('\n') for w in x.readlines()]
            count = len(lines) - 1
            for i in range(1, len(lines)):
                x_sum += float(lines[i].split(',')[0])
                y_sum += float(lines[i].split(',')[1])
                z_sum += float(lines[i].split(',')[2])
        X.append(x_sum/count)
        Y.append(y_sum/count)
        Z.append(z_sum/count)




plt.figure("Quick Plots")
plt.subplot(311)
plt.plot(X)
plt.grid(b=True, which='major', color='r', linestyle='--')

plt.title("X")
plt.subplot(312)
plt.plot(Y)
plt.grid(b=True, which='major', color='r', linestyle='--')

plt.title("Y")
plt.subplot(313)
plt.plot(Z)
plt.title("Z")
plt.grid(b=True, which='major', color='r', linestyle='--')

plt.tight_layout()
plt.show()