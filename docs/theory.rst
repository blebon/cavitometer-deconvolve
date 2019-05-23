Theory
============

1. The sensitivity of calibrated hydrophones is generally available in discrete steps
that do not exactly match FFT data frequencies. To convert voltages to pressures, the
sensitivity values :math:`M(f)` are first interpolated to match the frequencies at which
the calibration points are acquired.

2. Given a recorded voltage signal :math:`V(t)` and its associated Fourier transform
:math:`\mathscr{F}[V(t)]`, the Fourier transform is converted to a one sided spectrum
and then divided by the interpolated sensitivities,
yielding :math:`\frac{\mathscr{F}[V(t)]}{M(f)}`.

3. The pressure values are obtained by performing an inverse Fourier transform on the
above division, giving :math:`p(t) = \mathscr{F}^{-1}\left[\frac{\mathscr{F}[V(t)]}{M(f)}\right]`.

The process is described in the paper Lebon *et al.* (2018) Experimental and numerical investigation of acoustic
pressures in different liquids. Ultrasonics Sonochemistry (42) 411-421.
`doi:10.1016/j.ultsonch.2017.12.002 <https://doi.org/10.1016/j.ultsonch.2017.12.002>`__.