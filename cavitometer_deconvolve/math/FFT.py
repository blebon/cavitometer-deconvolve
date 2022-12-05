# -*- coding: utf-8 -*-
""" FFT module.

This module contains the FFT codes.

"""

from __future__ import division

from numpy import empty, ndarray
from pyfftw import interfaces


def fast_fourier_transform(time: ndarray, signal: ndarray, units: list) -> tuple:
    """Performs the Fast Fourier Transform on the time signal.

    :param time: the time numpy array
    :param signal: the signal numpy array
    :param units: the SI units for the time and signal arrays
    :return: frequency, fourier transform
    :rtype: tuple
    """
    # If units in ms, multiply step time by 1e-3
    step = time[1] - time[0]
    if "ms" in units[0]:
        step *= 1.0e-3
    # Convert voltage to volts if mV
    if "mV" in units[1]:
        signal = signal * 1.0e-3

    # N0 = len(s)
    # w = blackman(N0)
    fourier = interfaces.numpy_fft.rfft(signal, norm="ortho")
    # fourier = fft.fft(s, norm="ortho")
    freq = interfaces.numpy_fft.rfftfreq(signal.size, step)

    return freq, fourier
