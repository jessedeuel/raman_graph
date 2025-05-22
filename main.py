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

from PyQt5.QtWidgets import QWidget, QPushButton, QCheckBox, QComboBox, QLineEdit, QSizePolicy, QLabel
from PyQt5.QtCore import pyqtSlot, QTimer, qDebug

background_color = "white"

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)

        self.setWindowTitle("GRN - Great RamaN")


        # Private variables
        self.counter = 0
        self.values = []
        self.integration_time = 5000 # in ms
        self.background = []

        # Layouts
        main_layout = QtWidgets.QGridLayout(self._main)
        # graph_layout = QtWidgets.QVBoxLayout(self._main)
        # comport_layout = QtWidgets.QVBoxLayout(self._main)

        # Size Policies
        spLeft = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        spLeft.setHorizontalStretch(5)
        spRight = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        spRight.setHorizontalStretch(1)
        
        dynamic_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        dynamic_canvas.setSizePolicy(spLeft)
        main_layout.addWidget(dynamic_canvas, 1, 0, 5, 1)
        main_layout.addWidget(NavigationToolbar(dynamic_canvas, self), 0, 0)

        dynamic_canvas.figure.set_facecolor(background_color)

        self.comport_dropdown = QComboBox(self)
        self.comport_dropdown.addItems([port.device for port in serial.tools.list_ports.comports()])

        self.connect_button = QPushButton('Connect', self)
        self.connect_button.clicked.connect(self.on_connect_click)
        #self.connect_button.setSizePolicy(spRight)

        self.integration_time_input = QLineEdit(self)
        #self.integration_time_input.textChanged.connect(self.set_integration_time)

        self.reading_button = QPushButton('Take Reading', self)
        self.reading_button.clicked.connect(self.request_reading)

        self.background_button = QPushButton('Set As Background', self)
        self.background_button.clicked.connect(self.set_background)

        self.show_background_subtraction_checkbox = QCheckBox('Show Background Subtraction', self)
        # self.show_background_subtraction_checkbox.clicked.connect(lambda x: self._update_canvas())

        self.export_button = QPushButton('Export CSV', self)
        self.export_button.clicked.connect(self.on_export_click)

        self.set_average_button = QPushButton('Set Average Count', self)
        self.average_count_input = QLineEdit(self)

        self.laser_checkbox = QCheckBox('Laser On', self)
        self.laser_checkbox.stateChanged.connect(self.on_laser_checkbox_changed)

        self.file_name_label = QLabel("File name")
        self.file_name_textbox = QLineEdit()
        
        main_layout.addWidget(self.comport_dropdown, 0, 1, 1, 2)
        main_layout.addWidget(self.connect_button, 2, 1, 1, 2)
        main_layout.addWidget(self.integration_time_input, 3, 2, 1, 1)
        main_layout.addWidget(self.reading_button, 3, 1, 1, 1)
        main_layout.addWidget(self.background_button, 4, 1)
        main_layout.addWidget(self.show_background_subtraction_checkbox, 4, 2)
        main_layout.addWidget(self.laser_checkbox, 5, 1, 1, 2)
        main_layout.addWidget(self.average_count_input, 6, 1, 1, 2)
        main_layout.addWidget(self.file_name_label, 7, 1, 1, 1)
        main_layout.addWidget(self.file_name_textbox, 7, 2, 1, 1)
        main_layout.addWidget(self.export_button, 8, 1, 1, 2)

        self._dynamic_ax = dynamic_canvas.figure.subplots()
        self._dynamic_ax.set_facecolor(background_color)
        self._dynamic_ax.grid(True)

        # Set up a Line2D
        self.xdata = np.linspace(0, 2048, num=2048)
        self._update_ydata()
        self._line, = self._dynamic_ax.plot(self.xdata, self.ydata)
        self._line.set_color('r')
        self._dynamic_ax.set_xlim(0, 2048)
        self._dynamic_ax.set_ylim(0, 1023)

        # Timers
        self.data_timer = QTimer(self)
        self.data_timer.timeout.connect(self._update_ydata)
        #self.data_timer.setInterval(500)
        self.data_timer.start(500)

        self.drawing_timer = QTimer(self) #QTimer(self) 
        self.drawing_timer.timeout.connect(self._update_canvas) #add_callback
        #self.drawing_timer.setInterval(500)
        self.drawing_timer.start(500)
        self._update_canvas()

    #@pyqtSlot()
    def _update_ydata(self):
        # qDebug("blah", end='')
        
        
        if hasattr(self, 's'):
            try:
                if self.s.in_waiting:
                    qDebug("in waiting")
                    # tmp_time = time.time()
                    # timed_out = False

                    # while self.s.in_waiting and not timed_out:
                    #     qDebug("Reading")
                    #     tmp = str(self.s.read(1))

                    #     if tmp == "" and (time.time() - tmp_time >= 10):
                    #         timed_out = True
                    #         raise Exception
                    #     else:
                    #         out += tmp

                    
                    self._update_canvas()
                    # self._update_canvas()
                    # fig.canvas.draw()
                    # fig.canvas.flush_events()
                else:
                    self.s.reset_input_buffer()
                    self.s.reset_output_buffer()
                    #qDebug("blah" + str(self.counter) + " " + str(self.s.in_waiting))
                    #self.counter += 1
            except Exception as e:
                qDebug("Failed to receive data.")
                qDebug(e)
                self.s.close()
                del self.s
                self.connect_button.setStyleSheet("background-color : red")

        else:
            self.ydata = np.linspace(0, 2048, num=2048)

    #@pyqtSlot()
    def _update_canvas(self):
        # qDebug('foo', end='')
        # qDebug('foo')
        if self.show_background_subtraction_checkbox.isChecked() and len(self.background) == self.ydata.size:
            self._line.set_data(self.xdata, np.array(self.background) - self.ydata)
        else:
            self._line.set_data(self.xdata, self.ydata)
        self._line.figure.canvas.draw_idle()

    @pyqtSlot()
    def on_laser_checkbox_changed(self):
        if self.laser_checkbox.isChecked():
            self.s.write('L'.encode('utf-8'))
        else:
            self.s.write('l'.encode('utf-8'))


    @pyqtSlot()
    def on_connect_click(self):
        qDebug(f"Attempting to connect to {self.comport_dropdown.currentText()}")
        try:
            self.s = serial.Serial(self.comport_dropdown.currentText(), 115200, timeout=0)
            qDebug("Connected!")
            self.s.reset_input_buffer()
            qDebug(f'{self.s.is_open}')
            self.connect_button.setStyleSheet("background-color : green")
        except:
            qDebug(f"Failed to connect to {self.comport_dropdown.currentText()}!")
            self.connect_button.setStyleSheet("background-color : red")

    @pyqtSlot()
    def on_export_click(self):
        if len(self.values) > 0:
            with open(f"./logs/{"RamanLog" if (self.file_name_textbox.text() == '') else self.file_name_textbox.text()}-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}.txt", "w") as file:
                for i, val in enumerate(self.values):
                    file.write(f"{val}\n")


    @pyqtSlot()
    def request_reading(self):
        if hasattr(self, 's'):
            try:
                self.integration_time = int(self.integration_time_input.text())
            except:
                qDebug("Invalid integration time")
                return
            
            try:
                avg_count = int(self.average_count_input.text())
            except:
                avg_count = 1

            self.ydata = np.zeros([1, 2048])
            
            for i in range(0, avg_count):
                #self.s.flush()
                sent = self.s.write(str(self.integration_time).encode('utf-8'))

                #time.sleep(3.0)\

                if sent > 0:
                    qDebug(f"Requested reading with integration time {self.integration_time}ms")
                else:
                    qDebug("Failed to request raman data.")

                while not self.s.in_waiting:
                    pass

                out = self.s.readline().decode()
                qDebug("done reading")
                qDebug(out)
                self.values = [int(i) for i in out.split(', ')[0:-1]]
                qDebug(f"Recieved {len(self.values)} readings.")

                if len(self.values) == 2048:
                    self.ydata += np.array(self.values)
                else:
                    qDebug("Did not receive expected number of readings.")

            self.ydata /= avg_count

        else:
            qDebug("Not connected to any port.")

    @pyqtSlot()
    def set_background(self):
        self.background = self.values
        self.show_background_subtraction_checkbox.setChecked(True)
        # self._update_canvas()

    @pyqtSlot()
    def closeEvent(self, event):
        qDebug("Exiting")
        if hasattr(self, 's'):
            self.s.close()
        
        exit(0)



if __name__ == "__main__":

    # plt.axis([0, 2048, 0, 1023])
    
    qapp = QtWidgets.QApplication.instance()
    if not qapp:
        qapp = QtWidgets.QApplication(sys.argv)

    app = ApplicationWindow()

    qapp.setStyleSheet(f'QWidget {{ background-color: {background_color} }}')

    app.show()
    app.activateWindow()
    app.raise_()
    qapp.exec()
