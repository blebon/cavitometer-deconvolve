# -*- coding: utf-8 -*-
""" Sensitivities of hydrophones and amplification factors

This file contains the classes for the probes (hydrophones) and pre-amplifiers.

"""

from numpy import genfromtxt


class Probe:
    """Contains the probe sensitivity values.

    Probes are calibrated when resting vertically (i = 0) or at 45 deg (i = 1).
    """
    def __init__(self, filename):
        """Initializes the frequency and sensitivity arrays from file

        Keyword arguments:
        filename -- the name of the probe sensitivity values csv file
        """
        self.filename = filename
        _file_array = genfromtxt(filename,
                                 delimiter=',',
                                 skip_header=1,
                                 usecols=None,
                                 unpack=False,
                                 )
        self.frequencies = _file_array[:, 0]
        self.sensitivities = _file_array[:, 1:]
    
    def get_frequencies(self):
        """Return frequencies"""
        return self.frequencies

    def get_sensitivities(self, i=0):
        """Return sensitivities.

        Keyword arguments:
        i -- 0 = vertical probe, 1 = probe inclined at 45 deg.
        """
        return self.sensitivities[:, i]

    def __repr__(self):
        return self.filename

    def __unicode__(self):
        return self.filename

    def __str__(self):
        return self.filename


class PreAmplifier(Probe):
    def get_sensitivities(self):
        """Return sensitivities. No orientation."""
        return self.sensitivities[:, 0]
