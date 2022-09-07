import pyaudio
import threading
import atexit
import numpy as np
import matplotlib.pyplot as plt
from PyQt5 import QtGui, QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

class MicrophoneRecorder(object):
    def __init__(self, rate=4000, chunksize=1024):
        self.rate = rate
        self.chunksize = chunksize
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=self.rate,
                                  input=True,
                                  frames_per_buffer=self.chunksize,
                                  stream_callback=self.new_frame)
        self.lock = threading.Lock()
        self.stop = False
        self.frames = []
        atexit.register(self.close)

    def new_frame(self, data, frame_count, time_info, status):
        data = np.fromstring(data, 'int16')
        with self.lock:
            self.frames.append(data)
            if self.stop:
                return None, pyaudio.paComplete
        return None, pyaudio.paContinue
    
    def get_frames(self):
        with self.lock:
            frames = self.frames
            self.frames = []
            return frames
    
    def start(self):
        self.stream.start_stream()

    def close(self):
        with self.lock:
            self.stop = True
        self.stream.close()
        self.p.terminate()

plt.switch_backend('Qt5Agg')

class MplFigure(object):
    def __init__(self, parent):
        self.figure = plt.figure(facecolor='white')
        self.canvas = FigureCanvas(self.figure)
        # self.toolbar = NavigationToolbar(self.canvas, parent)

class LiveFFTWidget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        
        # customize the UI
        self.initUI()
        
        # init class data
        self.initData()       
        
        # connect slots
        self.connectSlots()
        
        # init MPL widget
        self.initMplWidget()
        
    def initUI(self):

        start_stop = QtWidgets.QHBoxLayout()
        button = QtWidgets.QPushButton("Start", self)
        button.setCheckable(True)
        button.clicked.connect(self.changeColor)

        button.setStyleSheet("background-color : green")
        start_stop.addWidget(button)
        # hbox_gain.addWidget(autoGainCheckBox)
        
        # reference to checkbox
        self.button = button

        vbox = QtWidgets.QVBoxLayout()

        vbox.addLayout(start_stop)

        # mpl figure
        self.main_figure = MplFigure(self)
        vbox.addWidget(self.main_figure.canvas)

        self.setLayout(vbox) 

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('Voice Activity Detection')    
        self.show()
        timer = QtCore.QTimer()
        timer.timeout.connect(self.handleNewData)
        timer.start(100)
        self.timer = timer

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

    def initData(self):
        mic = MicrophoneRecorder()
        mic.start()  

        # keeps reference to mic        
        self.mic = mic
        
        # computes the parameters that will be used during plotting
        self.freq_vect = np.fft.rfftfreq(mic.chunksize, 
                                         1./mic.rate)
        self.time_vect = np.arange(mic.chunksize, dtype=np.float32) / mic.rate * 1000
                
    def connectSlots(self):
        pass
    
    def initMplWidget(self):
        """creates initial matplotlib plots in the main window and keeps 
        references for further use"""
        # top plot
        self.ax_top = self.main_figure.figure.add_subplot(211)
        self.ax_top.set_ylim(-32768, 32768)
        self.ax_top.set_xlim(0, self.time_vect.max())
        self.ax_top.set_xlabel(u'time (ms)', fontsize=6) 
        self.ax_top.set_ylabel(u'intensity ', fontsize=6) 
        self.line_top, = self.ax_top.plot(self.time_vect, 
                                         np.ones_like(self.time_vect))                               

    def handleNewData(self):
        """ handles the asynchroneously collected sound chunks """        
        # gets the latest frames        
        frames = self.mic.get_frames()
        
        if len(frames) > 0:
            # keeps only the last frame
            current_frame = frames[-1]
            # plots the time signal
            self.line_top.set_data(self.time_vect, current_frame)       
            
            # refreshes the plots
            self.main_figure.canvas.draw()

import sys

app = QtWidgets.QApplication(sys.argv) 
window = LiveFFTWidget() 

#app.show()

sys.exit(app.exec_()) 