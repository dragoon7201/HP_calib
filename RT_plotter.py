import matplotlib.pyplot as plt
import User_inputs
new_data = False
SAVE = False
RUN = True
fig_path = ''
fig_name = ''
x_dat = []
y_dat = []
z_dat = []
x_axis = []


def axis_limit(array, arg):
    if arg == 'min':
        if len(array) == 1:
            return array[0] - 0.1
        else:
            return min(array)
    if arg == 'max':
        if len(array) == 1:
            return array[0] + 0.1
        else:
            return max(array)


def plot():
    global new_data, SAVE
    fig = plt.figure()
    x_plot = fig.add_subplot(311)  # 3 subplots, first column, first row
    plt.grid(b=True, which='major', color='r', linestyle='--')

    y_plot = fig.add_subplot(312)  # "     ,     "       , second row
    plt.grid(b=True, which='major', color='r', linestyle='--')

    z_plot = fig.add_subplot(313)  # "     ,     "       , third row
    plt.grid(b=True, which='major', color='r', linestyle='--')


    x_plot.set_title('X probe')
    y_plot.set_title('Y probe')
    z_plot.set_title('Z probe')

    y_plot.set_ylabel('average volts ( V )')
    z_plot.set_xlabel('rotation angle ( ° )')

    Ln_x, = x_plot.plot(x_dat)
    Ln_y, = y_plot.plot(y_dat)
    Ln_z, = z_plot.plot(z_dat)
    plt.ion()
    plt.tight_layout()

    while RUN:
        if new_data:
            Ln_x.set_ydata(x_dat)
            Ln_y.set_ydata(y_dat)
            Ln_z.set_ydata(z_dat)

            Ln_x.set_xdata(x_axis)
            Ln_y.set_xdata(x_axis)
            Ln_z.set_xdata(x_axis)

            mn = axis_limit(x_axis, 'min')
            mx = axis_limit(x_axis, 'max')

            x_plot.set_xlim(mn, mx)
            y_plot.set_xlim(mn, mx)
            z_plot.set_xlim(mn, mx)

            x_plot.set_ylim(axis_limit(x_dat, 'min'), axis_limit(x_dat, 'max'))
            y_plot.set_ylim(axis_limit(y_dat, 'min'), axis_limit(y_dat, 'max'))
            z_plot.set_ylim(axis_limit(z_dat, 'min'), axis_limit(z_dat, 'max'))
            new_data = False
        elif SAVE:
            print('saving triggered')
            plt.savefig(fig_path + '/' + fig_name, bbox_inches='tight')
            SAVE = False
        else:
            plt.pause(1)

    print('plotting service terminated')