# -*- coding: utf-8 -*-
""" GUI module.

This module contains the codes for a simple GUI.

"""

from sys import argv, exit

from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStyleFactory,
    QRadioButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from numpy import max, mean, square, sqrt, abs

from cavitometer_deconvolve.hardware import sensitivities
from cavitometer_deconvolve.utils.read import read_signal
from cavitometer_deconvolve.math import deconvolve

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


class CavitometerDeconvolveGUI(QMainWindow):
    def __init__(self, parent=None):
        """Initialize the widgets."""
        super(CavitometerDeconvolveGUI, self).__init__(parent)

        # Set the palette
        self.originalPalette = QApplication.palette()

        # Top horizontal box layout: choose window theme and disable sections
        styleComboBox = QComboBox()
        styleComboBox.addItems(QStyleFactory.keys())

        styleLabel = QLabel("&Style:")
        styleLabel.setBuddy(styleComboBox)

        self.useStylePaletteCheckBox = QCheckBox("&Use style's standard palette")
        self.useStylePaletteCheckBox.setChecked(True)

        disableWidgetsCheckBox = QCheckBox("&Disable widgets")

        # Create sections
        self.createFileIOGroupBox()  # Choose data and probe files
        self.createTableWidget()  # View data and probe dataframes in tabs
        self.createResultsWidget()  # View results

        styleComboBox.activated[str].connect(self.changeStyle)
        self.useStylePaletteCheckBox.toggled.connect(self.changePalette)
        disableWidgetsCheckBox.toggled.connect(self.fileIOGroupBox.setDisabled)
        disableWidgetsCheckBox.toggled.connect(self.tableGroupBox.setDisabled)
        disableWidgetsCheckBox.toggled.connect(self.resultsGroupBox.setDisabled)

        # The top horizontal box layout
        topLayout = QHBoxLayout()
        topLayout.addWidget(styleLabel)
        topLayout.addWidget(styleComboBox)
        topLayout.addStretch(1)
        topLayout.addWidget(self.useStylePaletteCheckBox)
        topLayout.addWidget(disableWidgetsCheckBox)

        # Main widgets
        mainLayout = QGridLayout()
        mainLayout.addLayout(topLayout, 0, 0, 1, 2)
        mainLayout.addWidget(self.fileIOGroupBox, 1, 0, 1, 2)
        mainLayout.addWidget(self.tableGroupBox, 2, 0)
        mainLayout.addWidget(self.resultsGroupBox, 2, 1)
        mainLayout.setRowStretch(2, 1)

        widget = QWidget()
        widget.setLayout(mainLayout)
        self.setCentralWidget(widget)

        self.setWindowTitle("Cavitometer-Deconvolve")

    def changeStyle(self, styleName):
        """Change the window appearance."""
        QApplication.setStyle(QStyleFactory.create(styleName))
        self.changePalette()

    def changePalette(self):
        if self.useStylePaletteCheckBox.isChecked():
            QApplication.setPalette(QApplication.style().standardPalette())
        else:
            QApplication.setPalette(self.originalPalette)

    def createFileIOGroupBox(self):
        """Choose voltage and probe files, channels and hit deconvolve."""
        self.fileIOGroupBox = QGroupBox("Select voltage and probe files")
        self.fileIOGroupBox.setCheckable(True)
        self.fileIOGroupBox.setChecked(True)

        # Select the data file and show in line edit
        self.dataFileLineEdit = QLineEdit("")
        self.dataFileLineEdit.setEnabled(False)

        selectDataFilePushButton = QPushButton("Select &voltage file")
        selectDataFilePushButton.setDefault(True)
        selectDataFilePushButton.clicked.connect(self.openDataFile)

        # Select probe sensitivities
        self.probeLineEdit = QLineEdit("")
        self.probeLineEdit.setEnabled(False)

        selectProbePushButton = QPushButton("Select &probe sensitivities file")
        selectProbePushButton.setDefault(True)
        selectProbePushButton.clicked.connect(self.openProbeFile)

        # Select channel in voltage file
        self.channelGroupBox = QGroupBox("Channel selection")
        channelLayout = QHBoxLayout()
        self.channelListWidget = QListWidget()
        channelLayout.addWidget(self.channelListWidget)
        self.channelGroupBox.setLayout(channelLayout)
        self.channelGroupBox.setEnabled(False)
        self.selectedChannel = 1  # Default is 1
        self.channelListWidget.itemClicked.connect(self.setChannel)

        # Select probe position
        self.probeRadioGroupBox = QGroupBox("Probe position")
        probeRadioLayout = QHBoxLayout()
        self.probe_position = 0
        self.b0 = QRadioButton("&Vertical")
        self.b0.setChecked(True)
        self.b0.toggled.connect(lambda: self.selectProbePosition(self.b0))
        probeRadioLayout.addWidget(self.b0)

        self.b1 = QRadioButton("45 &degrees")
        self.b1.setChecked(False)
        self.b1.toggled.connect(lambda: self.selectProbePosition(self.b1))
        probeRadioLayout.addWidget(self.b1)

        self.probeRadioGroupBox.setLayout(probeRadioLayout)
        self.probeRadioGroupBox.setEnabled(False)

        # Variables to enable or disable relevant sections
        self.valid_data_file = False  # Enable or disable channel selection
        self.valid_probe_file = False  # Enable or disable probe position selection
        self.can_deconvolve = False  # Enable or disable deconvolve push button

        # Button to run deconvolution
        self.deconvolvePushButton = QPushButton("&Deconvolve")
        self.deconvolvePushButton.setDefault(True)
        self.deconvolvePushButton.setEnabled(self.can_deconvolve)
        self.deconvolvePushButton.clicked.connect(self.deconvolve)

        layout = QGridLayout()
        layout.addWidget(self.dataFileLineEdit, 1, 1)
        layout.addWidget(selectDataFilePushButton, 1, 2, 1, 2)
        layout.addWidget(self.probeLineEdit, 2, 1)
        layout.addWidget(selectProbePushButton, 2, 2, 1, 2)
        layout.addWidget(self.channelGroupBox, 3, 1)
        layout.addWidget(self.probeRadioGroupBox, 3, 2)
        layout.addWidget(self.deconvolvePushButton, 3, 3)
        self.fileIOGroupBox.setLayout(layout)

    def invalidDataFile(self):
        """If data file is invalid, disable relevant sections."""
        self.valid_data_file = False
        self.dataTableWidget.setRowCount(0)
        self.dataTableWidget.setColumnCount(0)
        self.dataFileLineEdit.setText("")
        self.channelListWidget.clear()
        self.enableOrDisableDeconvolveButton()

    def openDataFile(self):
        """Open filename using QT dialog."""
        # Reset fields first
        self.invalidDataFile()

        dataFileSelector = QFileDialog()
        filenames = dataFileSelector.getOpenFileName(
            self,
            "Open data file",
            "",
            "Data files (*.csv *.xls *.xlsx)",
        )

        """If dialog closed without selecting a file"""
        if not filenames[0]:
            return None

        # Show path in the line edit box
        self.voltageFilename = filenames[0]
        self.dataFileLineEdit.setText(self.voltageFilename)

        # Read the data
        try:
            columns, self.units, self.raw_data = read_signal(self.voltageFilename)
        except Exception as e:
            invalidDataFile = QMessageBox()
            invalidDataFile.setText(f"Error: {e}")
            invalidDataFile.exec()
            return None

        self.channelListWidget.addItems(columns[1:])

        # Display in the bottom left table widget
        self.dataTableWidget.setColumnCount(self.raw_data.shape[1])
        self.dataTableWidget.setRowCount(self.raw_data.shape[0] + 2)

        for column, columnvalue in enumerate(columns):
            # Display header in first row
            self.dataTableWidget.setItem(0, column, QTableWidgetItem(columnvalue))
            self.dataTableWidget.setItem(
                1, column, QTableWidgetItem(self.units[column])
            )
            # Display the rest of the data in all the rows below
            for row, value in enumerate(self.raw_data[:, column]):
                self.item = QTableWidgetItem(str(value))
                # row + 1 because header is at row 0
                self.dataTableWidget.setItem(row + 2, column, self.item)
                self.item.setFlags(Qt.ItemIsEnabled)

        self.valid_data_file = True
        self.enableOrDisableDeconvolveButton()

    def setChannel(self):
        """Update selected channel flag when list clicked."""
        self.selectedChannel = self.channelListWidget.currentRow() + 1

    def invalidProbeFile(self):
        """If probe file is invalid, disable relevant sections."""
        self.valid_probe_file = False
        self.probeTableWidget.setRowCount(0)
        self.probeTableWidget.setColumnCount(0)
        self.probeLineEdit.setText("")
        self.enableOrDisableDeconvolveButton()

    def openProbeFile(self):
        self.invalidProbeFile()

        # Open filename using QT dialog
        dataFileSelector = QFileDialog()
        filenames = dataFileSelector.getOpenFileName(
            self,
            "Open data file",
            "",
            "Data files (*.csv *.xls *.xlsx)",
        )

        # If dialog is cancelled.
        if not filenames[0]:
            return None

        # Show path in the line edit box
        try:
            self.probe = sensitivities.Probe(filenames[0])
        except Exception as e:
            invalidProbeFile = QMessageBox()
            invalidProbeFile.setText(f"Error: {e}")
            invalidProbeFile.exec()
            return None
        self.probeLineEdit.setText(filenames[0])

        # Display in the bottom left table widget
        self.probeTableWidget.setColumnCount(2)
        self.probeTableWidget.setRowCount(self.probe.frequencies.shape[0] + 1)

        # Display frequencies
        self.probeTableWidget.setItem(0, 0, QTableWidgetItem("Frequency (kHz)"))
        # Display the rest of the data in all the rows below
        for row, value in enumerate(self.probe.frequencies):
            self.item = QTableWidgetItem(str(value))
            # row + 1 because header is at row 0
            self.probeTableWidget.setItem(row + 1, 0, self.item)
            self.item.setFlags(Qt.ItemIsEnabled)

        # Display sensitivities
        self.updateSensitivitiesColumn()
        self.valid_probe_file = True
        self.enableOrDisableDeconvolveButton()

    def enableOrDisableDeconvolveButton(self):
        """Enable or disable group boxes."""
        self.can_deconvolve = self.valid_data_file and self.valid_probe_file
        self.channelGroupBox.setEnabled(self.valid_data_file)
        self.probeRadioGroupBox.setEnabled(self.valid_probe_file)
        self.deconvolvePushButton.setEnabled(self.can_deconvolve)

    def selectProbePosition(self, b):
        if b.text() == "&Vertical":
            if b.isChecked():
                self.probe_position = 0

        if b.text() == "45 &degrees":
            if b.isChecked():
                self.probe_position = 1

        # Update sensitivities
        self.updateSensitivitiesColumn()

    def updateSensitivitiesColumn(self):
        """Repopulate sensitivities column when radio button is toggled."""
        self.probeTableWidget.setItem(0, 1, QTableWidgetItem("Sensitivities (dB)"))
        # Display the rest of the data in all the rows below
        for row, value in enumerate(self.probe.get_sensitivities(self.probe_position)):
            self.item = QTableWidgetItem(str(value))
            # row + 1 because header is at row 0
            self.probeTableWidget.setItem(row + 1, 1, self.item)
            self.item.setFlags(Qt.ItemIsEnabled)

    def createTableWidget(self):
        """Tabs for data and probe."""
        self.tableGroupBox = QGroupBox("Files reader")
        self.tableGroupBox.setCheckable(True)
        self.tableGroupBox.setChecked(True)

        fileTabWidget = QTabWidget()

        dataTab = QWidget()
        self.dataTableWidget = QTableWidget()
        dataHBox = QHBoxLayout()
        dataHBox.addWidget(self.dataTableWidget)
        dataTab.setLayout(dataHBox)

        probeTab = QWidget()
        self.probeTableWidget = QTableWidget()
        probeHBox = QHBoxLayout()
        probeHBox.addWidget(self.probeTableWidget)
        probeTab.setLayout(probeHBox)

        fileTabWidget.addTab(dataTab, "Voltage file")
        fileTabWidget.addTab(probeTab, "Probe file")

        layout = QVBoxLayout()
        layout.addWidget(fileTabWidget)

        self.tableGroupBox.setLayout(layout)

    def createResultsWidget(self):
        self.resultsGroupBox = QGroupBox("Results")
        self.resultsGroupBox.setCheckable(True)
        self.resultsGroupBox.setChecked(True)

        resultsTabWidget = QTabWidget()

        resultsTab = QWidget()
        self.resultsTableWidget = QTableWidget()
        resultsTableHBox = QHBoxLayout()
        resultsTableHBox.addWidget(self.resultsTableWidget)
        resultsTab.setLayout(resultsTableHBox)

        statisticsTab = QWidget()
        self.statisticsGroupBox = QGroupBox("")
        self.initializeStatisticsGroupBox()
        statisticsTableHBox = QHBoxLayout()
        statisticsTableHBox.addWidget(self.statisticsGroupBox)
        statisticsTab.setLayout(statisticsTableHBox)

        resultsTabWidget.addTab(resultsTab, "Pressure table")
        resultsTabWidget.addTab(statisticsTab, "Pressure statistics")

        layout = QVBoxLayout()
        layout.addWidget(resultsTabWidget)

        self.resultsGroupBox.setLayout(layout)

    def initializeStatisticsGroupBox(self):
        maxPressureLabel = QLabel("Maximum Pressure (kPa):")
        self.maxPressureLineEdit = QLineEdit("")
        rmsPressureLabel = QLabel("RMS Pressure (kPa):")
        self.rmsPressureLineEdit = QLineEdit("")

        layout = QGridLayout()
        layout.addWidget(maxPressureLabel, 1, 1)
        layout.addWidget(self.maxPressureLineEdit, 1, 2)
        layout.addWidget(rmsPressureLabel, 2, 1)
        layout.addWidget(self.rmsPressureLineEdit, 2, 2)
        self.statisticsGroupBox.setLayout(layout)

    def populateStatisticsGroupBox(self, max_p, rms_p):
        self.maxPressureLineEdit.setText(f"{max_p:.1f}")
        self.rmsPressureLineEdit.setText(f"{rms_p:.1f}")

    def deconvolve(self):
        self.time = self.raw_data[:, 0].T
        self.signal = self.raw_data[:, self.selectedChannel].T
        self.freq, self.fourier, self.pressure = deconvolve.deconvolution(
            self.time,
            self.signal,
            self.units[:2],
            self.probe,
            self.probe_position,
            None,
        )

        # Display in the bottom left table widget
        self.resultsTableWidget.setColumnCount(2)
        self.resultsTableWidget.setRowCount(len(self.time) + 1)

        for column, columnvalue in enumerate(
            [f"Time {self.units[0]}", "Pressure (Pa)"]
        ):
            # Display header in first row
            self.resultsTableWidget.setItem(0, column, QTableWidgetItem(columnvalue))
            # Display the rest of the data in all the rows below
            for row, value in enumerate(self.time):
                if column == 0:
                    value = self.time[row]
                else:
                    value = self.pressure.real[row]
                self.item = QTableWidgetItem(str(value))
                # row + 1 because header is at row 0
                self.resultsTableWidget.setItem(row + 1, column, self.item)
                self.item.setFlags(Qt.ItemIsEnabled)

        self.populateStatisticsGroupBox(
            max(self.pressure.real) / 1e3,
            sqrt(mean(square(self.pressure.real))) / 1e3,
        )

        figure = ResultsWindow(self)


def main():
    app = QApplication(argv)
    gallery = CavitometerDeconvolveGUI()
    gallery.show()
    exit(app.exec())


if __name__ == "__main__":
    main()
