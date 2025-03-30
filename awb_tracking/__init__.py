"""
AWB Tracking package.

This package provides functionality for tracking air waybills (AWB).
"""

# Import the main tracker class
from .awbtracker import AWBTracker

# Package metadata
__version__ = "1.0.0"
__author__ = "AWBTracker Team"
__email__ = "support@awbtracker.com"
__license__ = "MIT"

# Define what should be imported with "from awb_tracking import *"
__all__ = ["AWBTracker"]
