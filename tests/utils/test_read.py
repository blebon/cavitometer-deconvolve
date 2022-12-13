import pytest

from os import sep

from cavitometer_deconvolve.utils import read


@pytest.mark.parametrize(
    "ext",
    [
        "csv",
        "xlsx",
    ],
)
class TestRead:
    FILENAME = f"tests{sep}Measurements{sep}Two_Probes"
    UNITS = ["(ms)", "(mV)", "(mV)"]

    def test_units(self, ext):
        units, _ = read.read_signal(f"{self.FILENAME}.{ext}")
        assert units == self.UNITS
    
    @pytest.mark.parametrize(
        "test_input, expected",
        [
            ( 0, [ 0.00000000e+00, -4.48541100e+01, -5.18862200e-01]),
            ( 1, [ 2.00000000e-04, -5.38395800e+01, -4.51715300e-01]),
            ( 2, [ 4.00000000e-04, -5.19838800e+01, -6.95885700e-01]),
            (-1, [ 2.00059988e+00,  2.98376300e+01, -1.10487100e+00]),
        ],
    )
    def test_read_signal(self, test_input, expected, ext):
        _, signal = read.read_signal(f"{self.FILENAME}.{ext}")
        assert signal.tolist()[test_input] == expected
