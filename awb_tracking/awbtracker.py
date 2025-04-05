from .indiapost import IndiaPostTracker
from .ecomexpress import EcomExpressTracker
from .dtdc import DTDCTracker
from .vrl import VRLTracker

class AWBTracker:
    """
    Central class to manage multiple courier tracking services dynamically.
    """

    def __init__(self):
        """
        Initializes all supported courier trackers.
        """
        self.trackers = {
            "indiapost": IndiaPostTracker(),
            "ecomexpress": EcomExpressTracker(),
            "dtdc": DTDCTracker(),
            "vrl": VRLTracker(),
        }

    def __getattr__(self, courier_name):
        """
        Dynamically call tracking methods for each courier.
        Allows `tracker.indiapost("AWB123456789")` usage.
        """
        if courier_name in self.trackers:
            return self.trackers[courier_name].track
        raise AttributeError(f"'AWBTracker' has no attribute '{courier_name}'")
