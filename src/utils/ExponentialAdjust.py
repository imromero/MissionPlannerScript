"""
Module: ExponentialAdjust.py
Description: Provides a utility function for exponential adjustment of joystick axis values.
"""

import math

def ExponentialAdjust(value, factor):
    """
    Adjusts the input value using an exponential factor while preserving its sign.
    
    Args:
        value (float): Input axis value.
        factor (float): Exponential factor.
        
    Returns:
        float: Adjusted value.
    """
    return math.copysign(abs(value) ** factor, value)