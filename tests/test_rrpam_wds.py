import runpy

import pytest

import rrpam_wds
from rrpam_wds.cli import main


def test_main():
    assert main([])==0
    
    
    
if __name__ == "__main__":
    test_main()
