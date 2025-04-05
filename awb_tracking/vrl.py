import requests

class VRLTracker:
    """
    Tracker for VRL logistics
    """

    def track(self, awb_number):
        """
        Track a VRL shipment
        
        Args:
            awb_number: The LR number to track
            
        Returns:
            Dictionary with tracking information
        """
        url = f"https://vrlgroup.in/track_consignment.aspx?lrtrack=1&lrno={awb_number}"
        
        # Initialize tracking info with default values
        tracking_info = {
            "tracking_number": awb_number,
            "status": "error",
            "location": "",
            "date_time": "",
            "status_txt": "No tracking information found"
        }
        
        try:
            response = requests.post(url)
            result = response.json()
            
            if result.get("Status") == "Success":
                status_txt = result.get("LrStatus", "")

                tracking_info["location"] = result.get("LrStatusLocation", "")
                tracking_info["date_time"] = result.get("LrStatusDatetime", "")
                tracking_info["status_txt"] = status_txt
                
                # Determine status
                if "delivered" in status_txt.lower():
                    tracking_info["status"] = "delivered"
                else:
                    tracking_info["status"] = "intransit"
            
        except Exception as e:
            tracking_info["status_txt"] = str(e)
            
        return tracking_info
