# -*- coding: utf-8 -*-
""" GUI module.

This module contains the codes for a simple GUI.

"""

from sys import argv, exit

from PyQt5.QtWidgets import QApplication

from cavitometer_deconvolve.gui.main import CavitometerDeconvolveGUI


def launch():
    app = QApplication(argv)
    gallery = CavitometerDeconvolveGUI()
    gallery.show()
    exit(app.exec())


if __name__ == "__main__":
    launch()
