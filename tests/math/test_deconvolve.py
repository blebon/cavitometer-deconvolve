import pytest

from numpy import max, mean, square, sqrt

from cavitometer_deconvolve.hardware import sensitivities
from cavitometer_deconvolve.utils import read, walker
from cavitometer_deconvolve.math import deconvolve


class TestDeconvolution:
    probe2 = sensitivities.Probe("data/hardware/Probe_2.csv")
    filename = walker.get_raw_files("tests")[0]
    units, raw_data = read.read_signal(filename)
    time, signal, _ = raw_data.T
    freq, fourier, pressure = deconvolve.deconvolution(
        time, signal, units[:2], probe2, 0, None
    )

    def test_first_entry_in_units_is_time(self):
        """First entry in units must be time."""
        assert "s)" in self.units[0]

    def test_other_entries_in_units_are_voltages(self):
        """All other entries in units must be in volts."""
        assert all(["V)" in unit for unit in self.units[1:]])

    def test_correct_pressure_array_size(self):
        """Test if deconvolution yields correct pressure array size."""
        assert self.time.size == self.pressure.size

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            (0, -754338.53169751),
            (-1, -201627.77935355),
        ],
    )
    def test_deconvolution(self, test_input, expected):
        """Test if deconvolution fails."""
        assert expected == pytest.approx(self.pressure.real[test_input])
    
    @pytest.mark.parametrize(
        "expected",
        [
            1185386.3563065997,
        ],
    )
    def test_max_pressure(self, expected):
        """Test if maximum measured pressure changed."""
        assert expected == max(self.pressure.real)
    
    @pytest.mark.parametrize(
        "expected",
        [
            370999.3144212581,
        ],
    )
    def test_max_pressure(self, expected):
        """Test if measured rms pressure changed."""
        assert expected == sqrt(mean(square(self.pressure.real)))
