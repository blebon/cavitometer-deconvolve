import pytest

from numpy import log10

from cavitometer_deconvolve.math.convert import (
    dBu_to_dBV,
    V_to_dBu,
    V_to_dBV,
    dBu_to_V,
    dBV_to_V,
    dB_to_V,
)


class TestSensitivities:
    @pytest.mark.parametrize(
        "test_input,expected",
        [
            (0, 20 * log10(0.775)),
        ],
    )
    def test_dBu_to_dBV(self, test_input, expected):
        """Test dBu to dBV conversion."""
        assert dBu_to_dBV(test_input) == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            (0.775, 0),
            (7.75, 20),
        ],
    )
    def test_V_to_dBu(self, test_input, expected):
        """Test V to dBu conversion."""
        assert V_to_dBu(test_input) == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            (1.0, 0),
            (10.0, 20),
        ],
    )
    def test_V_to_dBV(self, test_input, expected):
        """Test V to dBV conversion."""
        assert V_to_dBV(test_input) == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            (0, 0.775),
        ],
    )
    def test_dBu_to_V(self, test_input, expected):
        """Test dBu to V conversion."""
        assert dBu_to_V(test_input) == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            (0, 1.0),
        ],
    )
    def test_dBV_to_V(self, test_input, expected):
        """Test dBV to V conversion."""
        assert dBV_to_V(test_input) == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            (0, 1e9),
        ],
    )
    def test_dB_to_V(self, test_input, expected):
        """Test dB to V conversion."""
        assert dB_to_V(test_input) == expected
