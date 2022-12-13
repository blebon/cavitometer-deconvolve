import pytest

from os import sep

from cavitometer_deconvolve.utils import walker


class TestWalker:
    FOLDERS = [f"tests{sep}Measurements"]
    FILES = [f"tests{sep}Measurements{sep}Two_Probes.csv"]

    def test_folders(self):
        folders = walker.get_folders(f"tests{sep}")
        assert list(folders) == self.FOLDERS

    def test_files(self):
        files = walker.get_raw_files(f"tests{sep}")
        assert list(files) == self.FILES
