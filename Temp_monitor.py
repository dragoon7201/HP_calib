from epics import PV
import matplotlib.pyplot as plt
import time

def Start_Temp_monitor():
    TM_02 = PV("TM1504-1-02")
    TM_06 = PV("TM1504-1-06")
    dat1 = []
    dat2 = []
    x_axis = []
    fig = plt.figure()
    ax = fig.add_subplot(111)

    Ln1, = ax.plot(dat1)
    Ln2, = ax.plot(dat2)
    plt.ion()
    plt.title("Water Temperature monitoring")
    plt.legend(["Out going H20 T", "Incoming H2O T"], loc="upper left")
    plt.xlabel('time (s)')
    plt.ylabel('Temp (°C)')
    ax.grid(linewidth=1, linestyle='-')
    i = 0
    start = time.time()
    while True:
        out = TM_02.get(as_numpy=True)
        income = TM_06.get(as_numpy=True)
        dat1.append(out)
        dat2.append(income)
        x_axis.append(i)
        Ln1.set_ydata(dat1)
        Ln2.set_ydata(dat2)
        Ln1.set_xdata(x_axis)
        Ln2.set_xdata(x_axis)

        miny = min(dat2) - 2
        maxy = max(dat1) + 2
        ax.set_xlim(0, i + 1)
        ax.set_ylim(miny, maxy)
        plt.pause(0.5) #Allows time for graph to update
        i += 1
        time.sleep(1 - ((time.time() - start) % 1))

if __name__ == '__main__':
    Start_Temp_monitor()



