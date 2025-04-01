
from awb_tracking import AWBTracker

        
if __name__ == '__main__':
    # Create an instance of the AWBTracker
    tracker = AWBTracker()

    # Example AWB numbers for testing
    awb_numbers = {
        "dtdc": "C45160501"
    }

    # Track each AWB number using the appropriate courier service
    for courier, awb_no in awb_numbers.items():
        tracking_info = getattr(tracker, courier.lower())(awb_no)
        print(f"Tracking info for {courier} ({awb_no}): {tracking_info}")
