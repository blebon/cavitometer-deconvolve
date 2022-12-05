from unittest import TestCase
import pytest

from numpy import max, mean, square, sqrt

from cavitometer_deconvolve.hardware import sensitivities
from cavitometer_deconvolve.utils import read, walker
from cavitometer_deconvolve.math import deconvolve


class TestDeconvolution(TestCase):
    def test_Deconvolution(self):
        """Test if deconvolution fails."""
        probe2 = sensitivities.Probe('data/hardware/Probe_2.csv')
        filename = walker.get_raw_files('tests')[0]
        units, raw_data = read.read_signal(filename)
        time, signal, _ = raw_data.T
        _, _, pressure = deconvolve.deconvolution(time, signal, units[:2], probe2, 0, None)
        # self.assertEqual(pressure.size, time.size)
        assert -754338.53169751 == pytest.approx(pressure.real[0])
