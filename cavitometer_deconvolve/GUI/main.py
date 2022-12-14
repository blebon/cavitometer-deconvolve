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
    QPushButton,
    # QSizePolicy,
    QStyleFactory,
    QRadioButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from pandas import read_csv, read_excel
from numpy import max, mean, square, sqrt

from cavitometer_deconvolve.hardware import sensitivities
from cavitometer_deconvolve.utils.read import read_signal
from cavitometer_deconvolve.math import deconvolve

# from matplotlib.backends.backend_qt5agg import FigureCanvasAgg as FigureCanvas
# from matplotlib.figure import Figure


class CavitometerDeconvolveGUI(QDialog):
    def __init__(self, parent=None):
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
        self.createTableWidget()  # View data and probe dataframes
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
        mainLayout.setRowStretch(1, 1)
        mainLayout.setRowStretch(3, 1)
        self.setLayout(mainLayout)

        self.setWindowTitle("Cavitometer-Deconvolve")

    def changeStyle(self, styleName):
        QApplication.setStyle(QStyleFactory.create(styleName))
        self.changePalette()

    def changePalette(self):
        if self.useStylePaletteCheckBox.isChecked():
            QApplication.setPalette(QApplication.style().standardPalette())
        else:
            QApplication.setPalette(self.originalPalette)

    def createFileIOGroupBox(self):
        self.fileIOGroupBox = QGroupBox("Select voltage and probe files")
        self.fileIOGroupBox.setCheckable(True)
        self.fileIOGroupBox.setChecked(True)

        # Select the csv file and show in line edit

        self.dataFileLineEdit = QLineEdit("")

        selectDataFilePushButton = QPushButton("Select data file")
        selectDataFilePushButton.setDefault(True)
        selectDataFilePushButton.clicked.connect(self.openDataFile)

        # Select probe sensitivities

        self.probeLineEdit = QLineEdit("")

        selectProbePushButton = QPushButton("Select probe sensitivities file")
        selectProbePushButton.setDefault(True)
        selectProbePushButton.clicked.connect(self.openProbeFile)

        self.channelGroupBox = QGroupBox("Channel selection")
        channelLayout = QHBoxLayout()
        self.channelListWidget = QListWidget()
        channelLayout.addWidget(self.channelListWidget)
        self.channelGroupBox.setLayout(channelLayout)
        self.channelGroupBox.setEnabled(False)
        self.selectedChannel = 1
        self.channelListWidget.itemClicked.connect(self.setChannel)

        self.probeRadioGroupBox = QGroupBox("Probe position")
        probeRadioLayout = QHBoxLayout()
        self.probe_position = 0
        self.b0 = QRadioButton("Vertical")
        self.b0.setChecked(True)
        self.b0.toggled.connect(lambda: self.selectProbePosition(self.b0))
        probeRadioLayout.addWidget(self.b0)

        self.b1 = QRadioButton("45 degrees")
        self.b0.setChecked(False)
        self.b1.toggled.connect(lambda: self.selectProbePosition(self.b1))

        probeRadioLayout.addWidget(self.b0)
        probeRadioLayout.addWidget(self.b1)
        self.probeRadioGroupBox.setLayout(probeRadioLayout)
        self.probeRadioGroupBox.setEnabled(False)

        self.can_deconvolve = False
        self.valid_data_file = False
        self.valid_probe_file = False
        self.deconvolvePushButton = QPushButton("Deconvolve")
        self.deconvolvePushButton.setDefault(True)
        self.deconvolvePushButton.setEnabled(self.can_deconvolve)
        self.deconvolvePushButton.clicked.connect(self.deconvolve)

        # Button to run deconvolution

        layout = QGridLayout()
        layout.addWidget(self.dataFileLineEdit, 1, 1)
        layout.addWidget(selectDataFilePushButton, 1, 2, 1, 2)
        layout.addWidget(self.probeLineEdit, 2, 1)
        layout.addWidget(selectProbePushButton, 2, 2, 1, 2)
        layout.addWidget(self.channelGroupBox, 3, 1)
        layout.addWidget(self.probeRadioGroupBox, 3, 2)
        layout.addWidget(self.deconvolvePushButton, 3, 3)
        self.fileIOGroupBox.setLayout(layout)

    def openDataFile(self):
        # Open filename using QT dialog
        dataFileSelector = QFileDialog()
        filenames = dataFileSelector.getOpenFileName(
            self,
            "Open data file",
            "",
            "Data files (*.csv *.xls *.xlsx)",
        )

        if not filenames[0]:
            self.valid_data_file = False
            self.dataFileLineEdit.setText("")
            self.channelListWidget.clear()
            self.enableOrDisableDeconvolveButton()
            return None

        # Show path in the line edit box
        self.filename = filenames[0]
        self.dataFileLineEdit.setText(self.filename)

        # Read the data into a pandas dataframe
        extension = self.filename.split(".")[-1]
        if extension == "csv":
            self.data = read_csv(self.filename, low_memory=False)
        else:
            self.data = read_excel(self.filename)

        self.channelListWidget.addItems(self.data.columns[1:])

        # Display in the bottom left table widget
        self.dataTableWidget.setColumnCount(self.data.shape[1])
        self.dataTableWidget.setRowCount(self.data.shape[0])

        for column, columnvalue in enumerate(self.data):
            # Display header in first row
            self.dataTableWidget.setItem(0, column, QTableWidgetItem(columnvalue))
            # Display the rest of the data in all the rows below
            for row, value in enumerate(self.data[columnvalue]):
                self.item = QTableWidgetItem(str(value))
                # row + 1 because header is at row 0
                self.dataTableWidget.setItem(row + 1, column, self.item)
                self.item.setFlags(Qt.ItemIsEnabled)

        self.valid_data_file = True
        self.enableOrDisableDeconvolveButton()

    def setChannel(self, item):
        self.selectedChannel = self.channelListWidget.currentRow() + 1

    def openProbeFile(self):
        # Open filename using QT dialog
        dataFileSelector = QFileDialog()
        filenames = dataFileSelector.getOpenFileName(
            self,
            "Open data file",
            "",
            "Data files (*.csv *.xls *.xlsx)",
        )
        if not filenames[0]:
            self.probeLineEdit.setText("")
            self.valid_probe_file = False
            self.enableOrDisableDeconvolveButton()
            return None
        # Show path in the line edit box
        self.probeLineEdit.setText(filenames[0])
        self.probe = sensitivities.Probe(filenames[0])
        self.probe_position = 0

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
        self.can_deconvolve = self.valid_data_file and self.valid_probe_file
        self.channelGroupBox.setEnabled(self.valid_data_file)
        self.probeRadioGroupBox.setEnabled(self.valid_probe_file)
        self.deconvolvePushButton.setEnabled(self.can_deconvolve)

    def selectProbePosition(self, b):
        if b.text() == "Vertical":
            if b.isChecked() == True:
                self.probe_position = 0

        if b.text() == "45 degrees":
            if b.isChecked() == True:
                self.probe_position = 1

        # Update sensitivities
        self.updateSensitivitiesColumn()

    def updateSensitivitiesColumn(self):
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
        # Open filename using QT dialog
        self.units, self.raw_data = read_signal(self.filename)

        time = self.raw_data[:, 0].T
        signal = self.raw_data[:, self.selectedChannel].T
        freq, fourier, pressure = deconvolve.deconvolution(
            time, signal, self.units[:2], self.probe, self.probe_position, None
        )

        # Display in the bottom left table widget
        self.resultsTableWidget.setColumnCount(2)
        self.resultsTableWidget.setRowCount(len(time) + 1)

        for column, columnvalue in enumerate(
            [f"Time {self.units[0]}", "Pressure (Pa)"]
        ):
            # Display header in first row
            self.resultsTableWidget.setItem(0, column, QTableWidgetItem(columnvalue))
            # Display the rest of the data in all the rows below
            for row, value in enumerate(time):
                if column == 0:
                    value = time[row]
                else:
                    value = pressure.real[row]
                self.item = QTableWidgetItem(str(value))
                # row + 1 because header is at row 0
                self.resultsTableWidget.setItem(row + 1, column, self.item)
                self.item.setFlags(Qt.ItemIsEnabled)

        self.populateStatisticsGroupBox(
            max(pressure.real) / 1e3,
            sqrt(mean(square(pressure.real))) / 1e3,
        )


def main():
    app = QApplication(argv)
    gallery = CavitometerDeconvolveGUI()
    gallery.show()
    exit(app.exec())


if __name__ == "__main__":
    main()
