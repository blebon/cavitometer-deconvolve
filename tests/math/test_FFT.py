from unittest import TestCase
import pytest

from numpy import abs, append, array, linspace, pi, sin

from cavitometer_deconvolve.math.FFT import (
    fast_fourier_transform,
)


class TestFFT(TestCase):
    def test_FFT(self):
        """Test simple FFT."""
        number_of_cycles = 1000
        number_of_points_per_cycle = 20
        t = linspace(
            0, number_of_cycles * pi, number_of_cycles * number_of_points_per_cycle
        )
        s = sin(2 * pi * t) # f == 1.0
        units = ["s", "V"]
        freq, fourier = fast_fourier_transform(t, s, units)
        assert 1.0 == pytest.approx(abs(freq[abs(fourier).argmax()]), freq[1] - freq[0])
