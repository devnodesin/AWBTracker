import requests
import json
import os

'''
Install required packages using pip:
pip install requests
'''

class EcomExpressTracker:
    """
    Tracker implementation for EcomExpress courier service.
    """

    def track(self, awb_number):
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

                # Save tracking result to JSON file
                try:
                    # Write tracking info to JSON file
                    with open("out/ecomexpress_tracking.json", "w") as f:
                        json.dump(result, f, indent=4)
                except Exception as e:
                    print(f"Error saving tracking info to file: {str(e)}")
                
                # Get the latest status (last item in shipment_status array)
                shipment_status = result.get("shipment_status", [])
                latest_status = shipment_status[-1] if shipment_status else {}
                
                # Create a dictionary with the tracking information
                tracking_info = {
                    "tracking_number": awb_number,
                    "status": latest_status.get("external_status_desc", ""),
                    "location": latest_status.get("service_center_name", ""),
                    "date_time": latest_status.get("scan_date", ""),
                    "status_txt": result  # Including the full details for reference
                }
                                
                # Return the tracking information as a JSON string
                return tracking_info

            return {
                "tracking_number": awb_number,
                "status": "error",
                "status_txt": f"Error extracting status: {data}"
            }
                
        except requests.RequestException as e:
            return {
                "tracking_number": awb_number,
                "status": "error",
                "status_txt": f"Request failed: {str(e)}"
            }

