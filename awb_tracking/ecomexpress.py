import requests
import json

'''
Install required packages using pip:
pip install requests
'''

class EcomExpressTracker:
    """
    Tracker implementation for EcomExpress courier service.
    """

    def track(self, awb_number):
        """
        Track an EcomExpress AWB number.
        
        Args:
            awb_number (str): The AWB tracking number
            
        Returns:
            dict: Tracking status information
        """
        # In a real implementation, this would make an API call to EcomExpress
        # For demonstration, we'll return a mock response
        # API endpoint for EcomExpress tracking
        url = "https://www.ecomexpress.in/api/track-awb"
        
        # Request payload
        payload = {"awb_field": awb_number}
        
        try:
            # Make the POST request to the API
            response = requests.post(url, json=payload)
            response.raise_for_status()  # Raise exception for bad status codes
            
            # Parse the JSON response
            data = response.json()
            
            if data.get("success"):
                result = data.get("result", {})
                
                # Get the latest status (last item in shipment_status array)
                shipment_status = result.get("shipment_status", [])
                latest_status = shipment_status[-1] if shipment_status else {}
                
                # Create a dictionary with the tracking information
                tracking_info = {
                    "tracking_number": awb_number,
                    "status": latest_status.get("external_status_desc", "Unknown"),
                    "location": latest_status.get("service_center_name", "Unknown"),
                    "date_time": latest_status.get("scan_date", "Unknown"),
                    "status_txt": result  # Including the full details for reference
                }
                
                # Return the tracking information as a JSON string
                return json.dumps(tracking_info)
            else:
                return json.dumps({"error": "Failed to retrieve tracking information", "details": data})
                
        except requests.RequestException as e:
            return json.dumps({"error": f"Request failed: {str(e)}"})

