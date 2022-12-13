import pytest

from os import sep

from cavitometer_deconvolve.hardware.sensitivities import Probe


class TestSensitivities:
    FILENAME = f"data{sep}hardware{sep}Probe_2.csv"
    SENSITIVITIES = [
        -263.6,
        -263.3,
        -263.8,
        -264.8,
        -264.8,
        -264.9,
        -266.5,
        -266.4,
        -267.4,
        -270.1,
        -277.3,
        -268.3,
        -263.2,
        -261.6,
        -262.7,
        -265.7,
        -273.2,
        -271.3,
        -270.5,
        -269.4,
        -265.7,
        -262.8,
        -262.3,
        -263.5,
        -268.8,
        -283.3,
        -274.2,
        -271.0,
        -278.6,
        -275.1,
        -267.6,
        -265.3,
        -267.2,
        -274.5,
        -277.0,
        -267.3,
        -263.8,
        -262.3,
        -262.1,
        -262.8,
        -265.0,
        -268.7,
        -273.5,
        -278.6,
        -276.5,
        -271.7,
        -267.9,
        -265.2,
        -263.7,
        -263.2,
        -264.1,
        -266.5,
        -272.2,
        -281.5,
        -275.1,
        -270.8,
        -269.1,
        -268.2,
        -267.8,
        -267.8,
        -269.6,
        -273.5,
        -277.9,
        -279.0,
        -275.1,
        -271.9,
        -267.8,
        -264.7,
        -263.6,
        -264.1,
        -266.7,
    ]

    @pytest.fixture(autouse=True)
    def test_probe(self):
        """Test if probe csv file can be read."""
        try:
            self.PROBE = Probe(self.FILENAME)
        except Exception as e:
            assert False, f"Reading {self.FILENAME} raised exception {e}."

    def test_get_sensitivities(self):
        sensitivities = self.PROBE.get_sensitivities()
        sensitivities = sensitivities.tolist()

        assert len(sensitivities) == len(self.SENSITIVITIES)
        assert all(
            list(map(lambda x, y: x == y, sensitivities, self.SENSITIVITIES))
        )
