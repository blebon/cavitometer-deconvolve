# -*- coding: utf-8 -*-
""" Sensitivities of hydrophones and amplification factors.

This file contains the classes for the probes (hydrophones) and pre-amplifiers.

"""

from numpy import ndarray
from pandas import read_csv


class Probe:
    """Contains the probe sensitivity values.

    Probes are calibrated when being rested vertically (i = 0) or at 45 deg (i = 1).
    """

    def __init__(self, filename: str) -> None:
        """Initializes the frequency and sensitivity arrays from filename.

        :param filename: the name of the probe sensitivity values csv file
        :rtype: None
        """
        self._filename = filename
        _df = read_csv(
            filename,
        )
        self._frequencies = _df.iloc[:, 0].values
        self._sensitivities = _df.iloc[:, 1:].values

    @property
    def frequencies(self) -> ndarray:
        """Returns frequencies.

        :rtype: ndarray
        """
        return self._frequencies

    def get_sensitivities(self, i: int = 0) -> ndarray:
        """Returns sensitivities.

        :param i:  0 = probe vertical, 1 = probe inclined at 45 deg.
        :rtype: ndarray
        """
        return self._sensitivities[:, i]

    def __repr__(self):
        return self._filename

    def __unicode__(self):
        return self._filename

    def __str__(self):
        return self._filename


class PreAmplifier(Probe):
    def get_sensitivities(self) -> ndarray:
        """Return sensitivities. No orientation.

        :rtype: ndarray
        """
        return self._sensitivities[:, 0]
