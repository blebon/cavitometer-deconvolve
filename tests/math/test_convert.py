from unittest import TestCase

from numpy import log10

from cavitometer_deconvolve.math.convert import (
    dBu_to_dBV,
    V_to_dBu,
    V_to_dBV,
    dBu_to_V,
    dBV_to_V,
    dB_to_V,
)


class TestSensitivities(TestCase):
    def test_dBu_to_dBV(self):
        """Test dBu to dBV conversion."""
        self.assertEqual(dBu_to_dBV(0), 20 * log10(0.775))
    
    def test_V_to_dBu(self):
        """Test V to dBu conversion."""
        self.assertEqual(V_to_dBu(0.775), 0)
        self.assertEqual(V_to_dBu(7.75), 20)
    
    def test_V_to_dBV(self):
        """Test V to dBV conversion."""
        self.assertEqual(V_to_dBV(1.0), 0)
        self.assertEqual(V_to_dBV(10.0), 20)
    
    def test_dBu_to_V(self):
        """Test dBu to V conversion."""
        self.assertEqual(dBu_to_V(0), 0.775)
    
    def test_dBV_to_V(self):
        """Test dBV to V conversion."""
        self.assertEqual(dBV_to_V(0), 1.0)
    
    def test_dB_to_V(self):
        """Test dB to V conversion."""
        self.assertEqual(dB_to_V(0), 1e9)
