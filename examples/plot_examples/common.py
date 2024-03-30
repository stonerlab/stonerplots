# -*- coding: utf-8 -*-
"""Variables and functions common to the examples."""
import numpy as np
from pathlib import Path

__all__ = ["figures", "model", "x", "pparam"]

figures = Path(__file__).parent.parent / "figures"


def model(x, p):
    """Make some nice data."""
    return x ** (2 * p + 1) / (1 + x ** (2 * p))


pparam = dict(xlabel="Voltage (mV)", ylabel=r"Current ($\mu$A)")
x = np.linspace(0.75, 1.25, 201)
