# -*- coding: utf-8 -*-
""" Read signal files

This module contains the codes for reading the raw files.

"""

from numpy import genfromtxt, isnan, nan_to_num


def get_units(filename, extension=".csv"):
    """ Read the units from the raw signal file.

    Keyword arguments
    filename -- name of raw signal file, including path
    extension -- extension of raw files (default '.csv')
    """
    with open(filename, "r") as f:
        # Units are always in the second line
        f.readline()
        u = f.readline()
        if extension == '.csv':
            units = u.replace('\n', '').split(',')
        else:
            units = u.replace('\r', '').split('\t')
    return units


def read_signal(filename, extension='.csv'):
    """ Read signals and remove Infs

    Keyword arguments
    filename -- name of raw signal file, including path
    extension -- extension of raw files (default '.csv')
    """
    units = get_units(filename, extension=extension)

    if extension == '.csv':
        sep = ','
    else:
        sep = '\t'
    # Read signal
    _signals_array = genfromtxt(filename,
                                delimiter=sep,
                                skip_header=3,
                                usecols=None,
                                unpack=False,
                                )

    # Remove Infs if any
    for i in range(1, _signals_array.shape[1]):
        _signal = _signals_array[:, i]
        if any(isnan(_signal)):
            _signals_array[:, i] = nan_to_num(_signal)

    return units, _signals_array
