import serial
import serial.tools.list_ports
import numpy as np
from numpy import random
import sys
import time
from datetime import datetime

from matplotlib import backend_bases
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.figure import Figure

from PyQt5.QtWidgets import QWidget, QPushButton, QAction, QLineEdit, QSizePolicy
from PyQt5.QtCore import pyqtSlot

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)

        # Private variables
        self.values = []
        self.integration_time = 50 # in ms
        self.background = []

        # Layouts
        main_layout = QtWidgets.QGridLayout(self._main)
        graph_layout = QtWidgets.QVBoxLayout(self._main)
        comport_layout = QtWidgets.QVBoxLayout(self._main)

        # Size Policies
        spLeft = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        spLeft.setHorizontalStretch(4)
        spRight = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        spRight.setHorizontalStretch(1)
        
        dynamic_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        dynamic_canvas.setSizePolicy(spLeft)
        main_layout.addWidget(dynamic_canvas, 1, 0, 4, 1)
        main_layout.addWidget(NavigationToolbar(dynamic_canvas, self), 0, 0)

        self.comport_textbox = QLineEdit(self)
        self.comport_textbox.resize(280, 40)
        self.comport_textbox.setSizePolicy(spRight)

        self.connect_button = QPushButton('Connect', self)
        self.connect_button.clicked.connect(self.on_connect_click)
        #self.connect_button.setSizePolicy(spRight)

        self.reading_button = QPushButton('Take Reading', self)
        self.reading_button.clicked.connect(self.request_reading)

        self.export_button = QPushButton('Export CSV', self)
        self.export_button.clicked.connect(self.on_export_click)
        
        main_layout.addWidget(self.comport_textbox, 0, 1)
        main_layout.addWidget(self.connect_button, 2, 1)
        main_layout.addWidget(self.reading_button, 3, 1)
        main_layout.addWidget(self.export_button, 4, 1)



        self._dynamic_ax = dynamic_canvas.figure.subplots()

        # Set up a Line2D
        self.xdata = np.linspace(0, 2048, num=2048)
        self._update_ydata()
        self._line, = self._dynamic_ax.plot(self.xdata, self.ydata)

        self.data_timer = dynamic_canvas.new_timer(1)
        self.data_timer.add_callback(self._update_ydata)
        self.data_timer.start()

        self.drawing_timer = dynamic_canvas.new_timer(20)
        self.drawing_timer.add_callback(self._update_canvas)
        self.drawing_timer.start()



    def _update_ydata(self):
        if hasattr(self, 's'):
            if self.s.in_waiting:
                out = self.s.readline().decode()
                arr = out.split(', ')
                arr = arr[0:-1]
                print(f"Recieved")
                self.values = np.array([int(i) for i in arr])

                self.ydata = self.values
                # fig.canvas.draw()
                # fig.canvas.flush_events()
        else:
            self.ydata = np.linspace(0, 2048, num=2048)

    def _update_canvas(self):
        self._line.set_data(self.xdata, self.ydata)
        self._line.figure.canvas.draw_idle()

    @pyqtSlot()
    def on_connect_click(self):
        try:
            self.s = serial.Serial(self.comport_textbox.text(), 115200, timeout=0)
            print(f"Connecting to {self.comport_textbox.text()}")
            self.connect_button.setStyleSheet("background-color : green")
        except:
            print(f"Failed to connect to {self.comport_textbox.text()}!")
            self.connect_button.setStyleSheet("background-color : red")

    @pyqtSlot()
    def on_export_click(self):
        if self.values.any():
            with open(f"RamanLog-{datetime.now().strftime("%Y-%m-%d-%H%M%S")}.txt", "w") as file:
                for i, val in enumerate(self.values):
                    file.write(f"{i+1} {val}\n")


    @pyqtSlot()
    def request_reading(self):
        tmp = self.integration_time.to_bytes()
        self.s.write(tmp)


def on_close(event):
    print("Exiting")
    exit(0)



if __name__ == "__main__":

    # plt.axis([0, 2048, 0, 1023])
    
    qapp = QtWidgets.QApplication.instance()
    if not qapp:
        qapp = QtWidgets.QApplication(sys.argv)

    app = ApplicationWindow()
    app.show()
    app.activateWindow()
    app.raise_()
    qapp.exec()

    """

    i = 0

    
    while True:
        fig.canvas.mpl_connect('close_event', on_close)
        
        # y = np.random.random()
        # #p = plt.plot(np.linspace(1, 2048, num=2048), )
        # plt.plot()
        # plt.pause(0.05)
        # i = i+1
        


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
        """
