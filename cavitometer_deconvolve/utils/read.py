# -*- coding: utf-8 -*-
""" Read the signal files.

This module contains the codes for reading the raw files.

"""

from numpy import isnan, nan_to_num
from pandas import read_csv, read_excel


def read_signal(filename: str) -> tuple:
    """Read signals and remove Infs.

    :param filename: name of raw signal file, including path
    :rtype: tuple
    """
    extension = filename.split('.')[-1]

    if extension == "csv":
        read_fun = read_csv
        drop_indices = [0]
    elif extension in ["xls", "xlsx"]:
        read_fun = read_excel
        drop_indices = [0, 1]
    else:
        raise Exception(f"File format {extension} not supported.")
    
    _signal_df = read_fun(
        filename,
    )

    units = _signal_df.iloc[0].tolist()

    _signal_df.drop(drop_indices, inplace=True)

    _signals_array = _signal_df.to_numpy(dtype=float)

    # Remove Infs if any
    for i in range(1, _signals_array.shape[1]):
        _signal = _signals_array[:, i]
        if any(isnan(_signal)):
            _signals_array[:, i] = nan_to_num(_signal)

    return units, _signals_array
