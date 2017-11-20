from epics import PV
import matplotlib.pyplot as plt
import time

def Start_monitor():
    TM_02 = PV("TM1504-1-02")
    TM_06 = PV("TM1504-1-06")
    PS_adc = PV("PS1504-01:adc")
    out_temp = []
    in_temp = []
    adc_array = []
    x_axis = []
    fig = plt.figure()
    temp_plt = fig.add_subplot(211)
    adc_plt = fig.add_subplot(212)
    Ln1, = temp_plt.plot(out_temp)  #not sure why ln1 must be an element of a list
    Ln2, = temp_plt.plot(in_temp)
    Ln3, = adc_plt.plot(adc_array)
    plt.ion()
    temp_plt.set_title("Water Temperature")
    adc_plt.set_title("PS ADC")
    temp_plt.legend(["Out going H20 T", "Incoming H2O T"], loc="upper left")
    plt.xlabel('time (s)')
    temp_plt.set_ylabel('Temp (°C)')
    adc_plt.set_ylabel('ADC')
    temp_plt.grid(linewidth=1, linestyle='-')
    adc_plt.grid(linewidth=1, linestyle='-')
    i = 0
    start = time.time()
    while True:
        out = TM_02.get(as_numpy=True)
        income = TM_06.get(as_numpy=True)
        adc = PS_adc.get(as_numpy=True)
        out_temp.append(out)
        in_temp.append(income)
        adc_array.append(adc)

        x_axis.append(i)
        Ln1.set_ydata(out_temp)
        Ln2.set_ydata(in_temp)
        Ln3.set_ydata(adc_array)
        Ln1.set_xdata(x_axis)
        Ln2.set_xdata(x_axis)
        Ln3.set_xdata(x_axis)

        temp_miny = min(in_temp) - 2
        temp_maxy = max(out_temp) + 2
        temp_plt.set_xlim(0, i + 1)
        temp_plt.set_ylim(temp_miny, temp_maxy)

        adc_miny = min(adc_array) - 2
        adc_maxy = max(adc_array) + 2
        adc_plt.set_xlim(0, i + 1)
        adc_plt.set_ylim(adc_miny, adc_maxy)

        plt.pause(3.5) #Allows time for graph to update
        i += 5
        time.sleep(5 - ((time.time() - start) % 5))

if __name__ == '__main__':
    Start_monitor()



