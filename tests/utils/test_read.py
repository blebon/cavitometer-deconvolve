import pytest

from os import sep

from cavitometer_deconvolve.utils import read


def test_exception_if_wrong_file_format():
    with pytest.raises(Exception):
        _, _, _ = read.read_signal(f"tests{sep}Measurements{sep}Two_Probes.dat")


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

    def test_assertion_error_if_time_not_found(self, ext):
        with pytest.raises(AssertionError):
            _, _, _ = read.read_signal(f"data{sep}hardware{sep}Probe_2.{ext}")

    def test_units(self, ext):
        _, units, _ = read.read_signal(f"{self.FILENAME}.{ext}")
        assert units == self.UNITS

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (0, [0.00000000e00, -4.48541100e01, -5.18862200e-01]),
            (1, [2.00000000e-04, -5.38395800e01, -4.51715300e-01]),
            (2, [4.00000000e-04, -5.19838800e01, -6.95885700e-01]),
            (-1, [2.00059988e00, 2.98376300e01, -1.10487100e00]),
        ],
    )
    def test_read_signal(self, test_input, expected, ext):
        _, _, signal = read.read_signal(f"{self.FILENAME}.{ext}")
        assert signal.tolist()[test_input] == expected
