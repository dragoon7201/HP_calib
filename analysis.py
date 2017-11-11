import os
path = r'C:\Users\lus\Desktop\Data1'
B_path = r"C:\Users\lus\PycharmProjects\epics_testing\NMR_readings2.txt"
X_ave = []
Y_ave = []
Z_ave = []
TP_ave = []
TB_ave = []
B = []
Array = ['X']
for dirname in os.listdir(path):
    dirname = "\\" + dirname
    for L in Array:
        if L in dirname:
            counter = 0
            for filename in os.listdir(path + dirname):
                filename = path + dirname + "\\" + filename
                if counter < 78:
                    with open(filename, 'r') as file:
                        lines = [x.strip("\n") for x in file.readlines()]
                        sum_x = 0
                        sum_y = 0
                        sum_z = 0
                        sum_tp = 0
                        sum_tb = 0
                        for line in range(1, 101):
                            sum_x += float(lines[line].split(',')[0])
                            sum_y += float(lines[line].split(',')[1])
                            sum_z += float(lines[line].split(',')[2])
                            sum_tp += float(lines[line].split(',')[4])
                            sum_tb += float(lines[line].split(',')[3])
                        X_ave.append(sum_x/100)
                        Y_ave.append(sum_y/100)
                        Z_ave.append(sum_z/100)
                        TP_ave.append(sum_tp/100)
                        TB_ave.append(sum_tb/100)
                counter += 1


with open(path + "\\X.txt", 'w') as file:
    for x in X_ave:
        file.write(str(x) + "\n")
with open(path + "\\Y.txt", "w") as file:
    for y in Y_ave:
        file.write(str(y) + "\n")
with open(path + "\\Z.txt", 'w') as file:
    for z in Z_ave:
        file.write(str(z) + "\n")
