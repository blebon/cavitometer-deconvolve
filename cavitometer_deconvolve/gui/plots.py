# -*- coding: utf-8 -*-
""" GUI module.

This module contains the codes for a simple GUI.

"""

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
)

from numpy import abs

import matplotlib

matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.pyplot import subplots


class ResultsCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        figure, self.axes = subplots(nrows=1, ncols=2, figsize=(width, height), dpi=dpi)
        super(ResultsCanvas, self).__init__(figure)


class ResultsWindow(QDialog):
    def __init__(self, parent=None, *args, **kwargs):
        super(ResultsWindow, self).__init__(parent, *args, **kwargs)

        resultsCanvas = ResultsCanvas(self, width=5, height=4, dpi=100)

        paxes, faxes = resultsCanvas.axes.flat
        paxes.plot(parent.time, parent.signal)
        paxes.set_xlabel("Time (s)")
        paxes.set_ylabel("Pressure (kPa)")
        paxes.set_title("Pressure")
        faxes.plot(parent.freq / 1e3, abs(parent.fourier))
        faxes.set_xlabel("Frequency (kHz)")
        faxes.set_ylabel("Fourier")
        faxes.set_title("FFT")
        resultsCanvas.draw()

        toolbar = NavigationToolbar2QT(resultsCanvas, self)

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(resultsCanvas)

        self.setLayout(layout)
        self.setWindowTitle("Deconvolution results")

        self.show()
