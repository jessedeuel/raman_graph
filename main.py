import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
from matplotlib import backend_bases
import numpy as np
from numpy import random
import os

def on_close(event):
    print("Exiting")
    exit(0)



if __name__ == "__main__":
    s = serial.Serial("/dev/ttyACM0", 115200, timeout=0)
    
    for port in serial.tools.list_ports.comports():
        try:
            s = serial.Serial(port, 115200, timeout=0)
            print(f"Connecting to {s}")
        except:
            pass

    # plt.axis([0, 2048, 0, 1023])

    plt.ion()

    x = np.linspace(0, 2048, num=2048)
    y = np.sin(x)

    # p = fig.add_subplot(111)
    fig, ax = plt.subplots()
    lines, = ax.plot(x, y, 'r-')

    ax.set_ylim(0, 1023)
    ax.set_xlim(0, 2048)

    i = 0

    while True:
        fig.canvas.mpl_connect('close_event', on_close)
        """
        y = np.random.random()
        #p = plt.plot(np.linspace(1, 2048, num=2048), )
        plt.plot()
        plt.pause(0.05)
        i = i+1
        """

        #fig.start_event_loop()

        if s.in_waiting:
            out = s.readline().decode()
            arr = out.split(', ')
            arr = arr[0:-1]
            print(f"Recieved {i}")
            i = i + 1
            arr = np.array([int(i) for i in arr])

            lines.set_ydata(arr)
            fig.canvas.draw()
            fig.canvas.flush_events()

        plt.pause(0.05)
            
