import pytest

from numpy import abs, append, array, linspace, pi, sin

from cavitometer_deconvolve.math.FFT import (
    fast_fourier_transform,
)


class TestFFT:
    number_of_cycles = 1000
    number_of_points_per_cycle = 20
    units = ["s", "V"]

    @pytest.mark.parametrize("f", [0.1, 1.0, 1e3, 20e3, 50e3, 1e6, 100e6])
    def test_FFT(self, f):
        """Test simple FFT for range of frequencies encountered in sonication."""
        T = 1/f
        t = linspace(
            0,
            self.number_of_cycles * T,
            self.number_of_cycles * self.number_of_points_per_cycle,
        )
        s = sin(2 * pi * f * t)
        freq, fourier = fast_fourier_transform(t, s, self.units)
        assert f == pytest.approx(abs(freq[abs(fourier).argmax()]), freq[1] - freq[0])
