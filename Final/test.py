from PyQt5 import QtGui, QtCore, QtWidgets
import matplotlib.pyplot as plt
import numpy as np
from ScrollingAxis import ScrollingTimestampPlot
from MicrophoneRecorder import MicrophoneRecorder
from MPLFigure import MplFigure
from Record import Recorder
from iteration_utilities import deepflatten
# from ScrollingAxis import ScrollingTimestampPlot


plt.switch_backend('Qt5Agg')

class VADUI(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        # customize the UI
        self.initUI()

        # init class data
        self.initData()       

        self.Record()
        # connect slots
        self.connectSlots()

        # init MPL widget
        self.initMplWidget()

        self.current_all_frames = []

    def initUI(self):

        start_stop = QtWidgets.QHBoxLayout()
        button = QtWidgets.QPushButton("Start", self)
        button.setCheckable(True)

        button.setStyleSheet("background-color : green")
        start_stop.addWidget(button)

        # reference to checkbox
        self.button = button
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(start_stop)

        # MPL figure
        self.top_figure = MplFigure(self)
        vbox.addWidget(self.top_figure.canvas)

        self.setLayout(vbox) 

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('Voice Activity Detection')    
        self.show()
        timer = QtCore.QTimer()
        timer.timeout.connect(self.handleNewData)
        timer.start(100)
        self.timer = timer

        self.scrolling_time_stamp = ScrollingTimestampPlot()
        vbox.addLayout(self.scrolling_time_stamp.get_scrolling_timestamp_plot_layout())

    # Button color start stop
    def changeColor(self):

        # if button is checked
        if self.button.isChecked():
            self.button.setStyleSheet("background-color : red")
            self.button.setText("Stop")

        # if it is unchecked
        else:
            self.button.setStyleSheet("background-color : green")
            self.button.setText("Start")
            self.scrolling_time_stamp.clear_scrolling_timestamp_plot()

    def initData(self):
        mic = MicrophoneRecorder()

        # keeps reference to mic
        self.mic = mic

        # computes the parameters that will be used during plotting
        self.freq_vect = np.fft.rfftfreq(mic.chunksize, 
                                        1./mic.rate)
        self.time_vect = np.arange(mic.chunksize, dtype=np.float32) / mic.rate * 1000

    def connectSlots(self):
        self.button.clicked.connect(self.changeColor)
        self.button.clicked.connect(self.Record)

    def initMplWidget(self):
        """creates initial matplotlib plots in the main window and keeps 
        references for further use"""
        # top plot
        self.ax_top = self.top_figure.figure.add_subplot(211)
        self.ax_top.set_ylim(-32768, 32768)
        self.ax_top.set_xlim(0, self.time_vect.max())
        self.ax_top.set_xlabel(u'time (ms)', fontsize=6) 
        self.ax_top.set_ylabel(u'intensity ', fontsize=6) 
        self.line_top, = self.ax_top.plot(self.time_vect, np.ones_like(self.time_vect))

    def handleNewData(self):
        """ handles the asynchroneously collected sound chunks """        
        # gets the latest frames
        current_frame = [0]
        last_frames = self.mic.last_frames()
        # all_frames = self.mic.all_frames()
        self.ax_top.set_xlim(0, self.time_vect.max())
        try:
            current_frame = last_frames[-1]
        except:
            current_frame = [0]*1024
        self.scrolling_time_stamp.read_position(position=current_frame[0])
        # self.current_all_frames.append(current_frame)
        self.current_all_frames =list(deepflatten(self.current_all_frames, depth=1))
        # self.time_vect_all = np.arange(len(self.current_all_frames), dtype=np.float32) / self.mic.rate * 1000

        # print(len(all_frames))
        if len(last_frames) > 0:
            # keeps only the last frame
            # print(len(self.current_all_frames),len(current_frame),len(self.time_vect_all))
            # plots the time signal
            if self.button.isChecked():
                # print(len(current_frame))
                self.line_top.set_data(self.time_vect, current_frame)   
            # refreshes the plots
            self.top_figure.canvas.draw()

    def Record(self):
        # if button is checked
        if self.button.isChecked():
            self.mic.start_recording()

        # if it is unchecked
        else:
            self.mic.stop_recording()

import sys

app = QtWidgets.QApplication(sys.argv) 
window = VADUI()

# app.show()

sys.exit(app.exec_()) 