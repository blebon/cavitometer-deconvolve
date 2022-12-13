import pytest

from os import sep

from cavitometer_deconvolve.utils import read


class TestRead:
    FILENAME = f"tests{sep}Measurements{sep}Two_Probes.csv"
    UNITS = ["(ms)", "(mV)", "(mV)"]

    def test_units(self):
        units = read.get_units(self.FILENAME)
        assert units == self.UNITS
    
    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (0, [0.0000, -44.85411, -0.5188622]),
            (1, [0.0002, -53.83958, -0.4517153]),
            (2, [0.0004, -51.98388, -0.6958857])
        ],
    )
    def test_read_signal(self, test_input, expected):
        _, signal = read.read_signal(self.FILENAME)
        assert signal.tolist()[test_input] == expected
