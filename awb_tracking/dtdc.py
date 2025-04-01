import requests
import json
import re
import base64
import os
from bs4 import BeautifulSoup
from awb_tracking.ocr import ocr_processor
from . import utils

class DTDCTracker:
    """
    Tracker implementation for DTDC courier service.
    """

    def fetch_captcha_image(self, session):
        """
        Fetch captcha image directly from the DTDC captcha API service.
        This function mimics the JavaScript fetch operation in the DTDC website.
        
        Args:
            session (requests.Session): The session to use for making the request
            
        Returns:
            tuple: (captcha_text, captcha_key)
        """
        # CAPTCHA API URL and endpoint from the JavaScript code
        captcha_api_url = "https://d-captcha-com.dtdc.com/captch-service/captcha/generate"
        
        # Headers with the X-API-KEY from the JavaScript code
        headers = {
            "X-API-KEY": "captchargxcEHG5ViM0H1HlnQ4xS2v5SR20gsAUOAxA64JsQ2qkOO7oaRG3gVqHtevvCwveOlDleicLrnAyAzSZnWPqYgszNeqMcVfk2ifyuo4eORGTrsUIVocZ6v0g5",
        }
        
        try:
            # Make the request to get the captcha
            response = session.get(captcha_api_url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract the base64 image and key
            captcha_image_base64 = data.get("image")
            captcha_key = data.get("key")
            
            # Save the captcha image
            if captcha_image_base64:
                with open("out/captcha_dtdc.png", "wb") as f:
                    f.write(base64.b64decode(captcha_image_base64))
                
                # Process the captcha with OCR
                captcha_text = ocr_processor("out/captcha_dtdc.png")
                return captcha_text, captcha_key
            else:
                print("No captcha image returned from API")
                return "", ""
                
        except Exception as e:
            print(f"Error fetching captcha: {str(e)}")
            return "", ""

    def track(self, awb_number):
        # Create a session for maintaining cookies
        session = requests.Session()
        os.makedirs("out", exist_ok=True)
        
        try:
            # Step 1: Fetch the tracking page
            tracking_url = "https://www.dtdc.in/trace.asp"
            response = session.get(tracking_url)
            response.raise_for_status()
            
            # Save the home page HTML
            with open("out/dtdc_tracking_home.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            
            # Step 2: Extract CSRF token from the page
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_token = soup.find('input', {'name': 'formDtdc'}).get('value', '')
            
            # Step 3: Fetch captcha image using the API directly
            captcha_text, captcha_key = self.fetch_captcha_image(session)
            
            if not captcha_text or not captcha_key:
                return {
                    "tracking_number": awb_number,
                    "status": "error",
                    "status_txt": "Failed to fetch or process captcha"
                }
            
            # Step 4: Submit the tracking form with captcha
            payload = {
                'formDtdc': csrf_token,
                'action': 'track',
                'captchaKeyval': captcha_key,
                'sec': 'tr',
                'ctlActiveVal': '1',
                'Ttype': '',
                'GES': '',
                'flag': '1',
                'trackingType': 'consignmentNo',
                'trackingNumber': awb_number,
                'captchaInput': captcha_text
            }

            print(payload)
            print("Submitting tracking request...")
            
            # Make the POST request
            response = session.post(tracking_url, data=payload)
            response.raise_for_status()
            
            # Save the tracking result page
            with open("out/dtdc_tracking_status.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            
            # Parse the tracking information
            tracking_details = utils.get_html_value_by_id(response.content, "printdiv")
            if tracking_details is not None:
               
                # Initialize variables to extract
                location = ""
                date_time = ""
                status = "in_transit"
    
                if "Delivered" in tracking_details:
                   status = "delivered"
        
                
                tracking_info = {
                    "tracking_number": awb_number,
                    "status": status,
                    "location": location,
                    "date_time": date_time,
                    "status_txt": tracking_details
                }
                
                return tracking_info
            else:
                return {
                    "tracking_number": awb_number,
                    "status": "error",
                    "status_txt": "Could not find tracking information"
                }
            
            
                
        except requests.RequestException as e:
            return {
                "tracking_number": awb_number,
                "status": "error",
                "status_txt": f"Request failed: {str(e)}"
            }


