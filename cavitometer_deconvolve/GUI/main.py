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
    QPushButton,
    QStyleFactory,
    QRadioButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from pandas import read_csv, read_excel

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
        self.createFileIOGroupBox()
        self.createTableWidget()
        self.createResultsWidget()

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
        self.fileIOGroupBox = QGroupBox("Select voltage file")
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

        self.radioGroupBox = QGroupBox("Probe position")
        radioLayout = QHBoxLayout()
        self.probe_position = 0
        self.b0 = QRadioButton("Vertical")
        self.b0.setChecked(True)
        self.b0.toggled.connect(lambda: self.selectProbePosition(self.b0))
        radioLayout.addWidget(self.b0)

        self.b1 = QRadioButton("45 degrees")
        self.b0.setChecked(False)
        self.b1.toggled.connect(lambda: self.selectProbePosition(self.b1))

        radioLayout.addWidget(self.b0)
        radioLayout.addWidget(self.b1)
        self.radioGroupBox.setLayout(radioLayout)
        self.radioGroupBox.setEnabled(False)
        
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
        layout.addWidget(selectDataFilePushButton, 1, 2)
        layout.addWidget(self.probeLineEdit, 2, 1)
        layout.addWidget(selectProbePushButton, 2, 2)
        layout.addWidget(self.radioGroupBox, 3, 1)
        layout.addWidget(self.deconvolvePushButton, 3, 2)
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
            self.enable_or_disable_deconvolve_button()
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

        # Display in the bottom left table widget
        self.tableWidget.setColumnCount(self.data.shape[1])
        self.tableWidget.setRowCount(self.data.shape[0])

        for column, columnvalue in enumerate(self.data):
            # Display header in first row
            self.tableWidget.setItem(0, column, QTableWidgetItem(columnvalue))
            # Display the rest of the data in all the rows below
            for row, value in enumerate(self.data[columnvalue]):
                self.item = QTableWidgetItem(str(value))
                # row + 1 because header is at row 0
                self.tableWidget.setItem(row + 1, column, self.item)
                self.item.setFlags(Qt.ItemIsEnabled)
        
        self.valid_data_file = True
        self.enable_or_disable_deconvolve_button()

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
            self.enable_or_disable_deconvolve_button()
            return None
        # Show path in the line edit box
        self.probeLineEdit.setText(filenames[0])
        self.probe = sensitivities.Probe(filenames[0])

        self.valid_probe_file = True
        self.enable_or_disable_deconvolve_button()
    
    def enable_or_disable_deconvolve_button(self):
        self.can_deconvolve = self.valid_data_file and self.valid_probe_file
        self.radioGroupBox.setEnabled(self.valid_probe_file)
        self.deconvolvePushButton.setEnabled(self.can_deconvolve)

    def selectProbePosition(self, b):
        if b.text() == "Vertical":
            if b.isChecked() == True:
                self.probe_position = 0

        if b.text() == "45 degrees":
            if b.isChecked() == True:
                self.probe_position = 1

    def createTableWidget(self):
        self.tableGroupBox = QGroupBox("Data file reader")
        self.tableGroupBox.setCheckable(True)
        self.tableGroupBox.setChecked(True)

        self.tableWidget = QTableWidget()

        layout = QVBoxLayout()
        layout.addWidget(self.tableWidget)

        self.tableGroupBox.setLayout(layout)

    def createResultsWidget(self):
        self.resultsGroupBox = QGroupBox("Results")
        self.resultsGroupBox.setCheckable(True)
        self.resultsGroupBox.setChecked(True)

        self.resultsWidget = QTableWidget()

        layout = QVBoxLayout()
        layout.addWidget(self.resultsWidget)

        self.resultsGroupBox.setLayout(layout)

    def deconvolve(self):
        # Open filename using QT dialog
        self.units, self.raw_data = read_signal(self.filename)

        if len(self.raw_data.T) == 3:
            time, signal, _ = self.raw_data.T
        else:
            time, signal = self.raw_data.T
        freq, fourier, pressure = deconvolve.deconvolution(
            time, signal, self.units[:2], self.probe, self.probe_position, None
        )

        # Display in the bottom left table widget
        self.resultsWidget.setColumnCount(2)
        self.resultsWidget.setRowCount(len(time) + 1)

        for column, columnvalue in enumerate(
            [f"Time {self.units[0]}", "Pressure (Pa)"]
        ):
            # Display header in first row
            self.resultsWidget.setItem(0, column, QTableWidgetItem(columnvalue))
            # Display the rest of the data in all the rows below
            for row, value in enumerate(time):
                if column == 0:
                    value = time[row]
                else:
                    value = pressure.real[row]
                self.item = QTableWidgetItem(str(value))
                # row + 1 because header is at row 0
                self.resultsWidget.setItem(row + 1, column, self.item)
                self.item.setFlags(Qt.ItemIsEnabled)


def main():
    app = QApplication(argv)
    gallery = CavitometerDeconvolveGUI()
    gallery.show()
    exit(app.exec())


if __name__ == "__main__":
    main()
