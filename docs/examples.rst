Examples
============

Read calibration data
----------------------

.. code-block:: python

    >> from cavitometer_deconvolve.hardware import sensitivities
    >> probe2 = sensitivities.Probe('data/hardware/Probe_2.csv')
    >> probe2.get_sensitivities()
    array([-263.6, -263.3, -263.8, -264.8, -264.8, -264.9, -266.5, -266.4,
           -267.4, -270.1, -277.3, -268.3, -263.2, -261.6, -262.7, -265.7,
           -273.2, -271.3, -270.5, -269.4, -265.7, -262.8, -262.3, -263.5,
           -268.8, -283.3, -274.2, -271. , -278.6, -275.1, -267.6, -265.3,
           -267.2, -274.5, -277. , -267.3, -263.8, -262.3, -262.1, -262.8,
           -265. , -268.7, -273.5, -278.6, -276.5, -271.7, -267.9, -265.2,
           -263.7, -263.2, -264.1, -266.5, -272.2, -281.5, -275.1, -270.8,
           -269.1, -268.2, -267.8, -267.8, -269.6, -273.5, -277.9, -279. ,
           -275.1, -271.9, -267.8, -264.7, -263.6, -264.1, -266.7])

Read signal
-------------

.. code-block:: python

    >> from cavitometer_deconvolve.utils import read, walker
    >> filename = walker.get_raw_files('tests')[0]
    >> units, raw_data = read.read_signal(filename)
    >> units
    ['(ms)', '(mV)', '(mV)']
    >> raw_data
    array([[ 0.00000000e+00, -4.48541100e+01, -5.18862200e-01],
           [ 2.00000000e-04, -5.38395800e+01, -4.51715300e-01],
           [ 4.00000000e-04, -5.19838800e+01, -6.95885700e-01],
           ...,
           [ 2.00019988e+00,  1.47723100e+01, -7.99658100e-01],
           [ 2.00039988e+00,  2.18776700e+01, -1.10487100e+00],
           [ 2.00059988e+00,  2.98376300e+01, -1.10487100e+00]])

Deconvolve signal
-------------------

.. code-block:: python

    >> from cavitometer_deconvolve.math import deconvolve
    >> time, signal1, signal2 = raw_data.T
    >> freq, fourier, pressure = deconvolve.deconvolution(time, signal1, units[:2], probe2, None)
    >> pressure.real
    array([-1.06827665e+06, -1.77156427e+01, -3.59243816e+05, ...,
           -1.12191517e+02, -3.59243816e+05, -1.77156427e+01])
