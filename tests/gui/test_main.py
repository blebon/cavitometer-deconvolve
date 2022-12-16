import pytest

from sys import argv

from cavitometer_deconvolve.gui.main import CavitometerDeconvolveGUI

from PyQt5.QtWidgets import QApplication


@pytest.fixture(scope="module")
def Application():
    app = QApplication(argv)
    gallery = CavitometerDeconvolveGUI()
    return app, gallery


@pytest.mark.usefixtures("Application")
class TestInvalidDataFile:
    @pytest.fixture(autouse=True)
    def set_up_invalid_data_file(self, Application):
        _, self.gallery = Application
        self.gallery.invalidDataFile()

    def test_data_file_flag_set_to_invalid(self):
        assert not self.gallery.valid_data_file

    def test_channel_list_widget_cleared(self):
        assert self.gallery.channelListWidget.count() == 0
    
    def test_data_table_widget_cleared(self):
        assert self.gallery.dataTableWidget.rowCount() == 0
        assert self.gallery.dataTableWidget.columnCount() == 0
    
    def test_data_file_line_edit_cleared(self):
        assert not self.gallery.dataFileLineEdit.text()

@pytest.mark.usefixtures("Application")
class TestInvalidProbeFile:
    @pytest.fixture(autouse=True)
    def set_up_invalid_probe_file(self, Application):
        _, self.gallery = Application
        self.gallery.invalidProbeFile()

    def test_probe_file_flag_set_to_invalid(self):
        assert not self.gallery.valid_probe_file
    
    def test_probe_table_widget_cleared(self):
        assert self.gallery.probeTableWidget.rowCount() == 0
        assert self.gallery.probeTableWidget.columnCount() == 0
    
    def test_probe_file_line_edit_cleared(self):
        assert not self.gallery.probeLineEdit.text()
