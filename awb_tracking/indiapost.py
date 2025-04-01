import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

from . import ocr

# Create a session object to maintain cookies and state
session = requests.Session()

def captcha2answer(captcha_question, ocr_text):
    """
    Process the captcha question and OCR text to determine the correct answer.
    
    :param captcha_question: The captcha question text
    :param ocr_text: The text extracted from the captcha image via OCR
    :return: The answer to the captcha
    """
    try:
        print(f"Processing captcha - Question: '{captcha_question}', OCR Text: '{ocr_text}'")
        
        # Case 1: Enter characters as displayed in image
        if "Enter characters as displayed in image" in captcha_question:
            return ocr_text.strip().lower()
        
        # Case 2: Evaluate the Expression
        elif "Evaluate the Expression" in captcha_question:
            # Clean up OCR text to make it evaluable
            expression = ocr_text.strip()
            expression = re.sub(r'=', '', expression)
            # Replace common OCR mistakes
            expression = expression.replace('x', '*')
            expression = expression.replace('X', '*')
            expression = expression.replace('×', '*')
            expression = expression.replace('÷', '/')
        
            # Safely evaluate the expression
            result = eval(expression)
            return str(int(result))  # Convert to integer then string
        
        # Case 3: Enter the 1-5 number
        elif "Enter the First number" in captcha_question:
            return ocr_text[0]
        elif "Enter the Second number" in captcha_question:
            return ocr_text[1]
        elif "Enter the Third number" in captcha_question:
            return ocr_text[2]
        elif "Enter the Fourth number" in captcha_question:
            return ocr_text[3]
        elif "Enter the Fifth number" in captcha_question:
            return ocr_text[4]
        
        # Default case: Return the OCR text as is
        else:
            print(f"Unknown captcha question type: {captcha_question}")
            return ocr_text
            
    except Exception as e:
        print(f"Error processing captcha: {e}")
        return ocr_text  # Return original text if any error occurs

def get_html_value_by_id(html_content, element_id):
    """
    Extract the HTML value of an element with the specified ID from HTML content.
    
    Args:
        html_content (bytes or str): The HTML content to parse
        element_id (str): The ID of the element to find
        
    Returns:
        str: The inner HTML of the element if found, None otherwise
    """
    try:
        # Create a BeautifulSoup object to parse the HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the element with the specified ID
        element = soup.find(id=element_id)
        
        # Return the inner HTML if element is found
        if element:
            return element.decode_contents()
        else:
            print(f"Element with ID '{element_id}' not found")
            return None
    except Exception as e:
        print(f"Error parsing HTML: {e}")
        return None

def get_img_src_by_id(html_content, img_id, base_url="https://www.indiapost.gov.in"):
    """
    Extract the 'src' attribute of an image element with the specified ID from HTML content.
    
    Args:
        html_content (bytes or str): The HTML content to parse
        img_id (str): The ID of the image element to find
        base_url (str): The base URL to create absolute URLs from relative paths
        
    Returns:
        str: The absolute 'src' attribute URL if found, None otherwise
    """
    try:
        # Create a BeautifulSoup object to parse the HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the image element with the specified ID
        img_element = soup.find('img', id=img_id)
        
        # Return the src attribute if the element is found
        if img_element and img_element.has_attr('src'):
            # Convert relative URL to absolute URL
            return urljoin(base_url, img_element['src'])
        else:
            print(f"Image with ID '{img_id}' not found or has no src attribute")
            return None
    except Exception as e:
        print(f"Error parsing HTML: {e}")
        return None

def get_captcha_img_url(html_content):
    """
    Try to find the captcha image URL by checking multiple possible image IDs.
    
    Args:
        html_content (bytes or str): The HTML content to parse
        base_url (str): The base URL to create absolute URLs from relative paths
        
    Returns:
        str: The absolute URL of the captcha image if found, None otherwise
    """
    captcha_image_ids = [
        "ctl00_PlaceHolderMain_ucNewLegacyControl_ucCaptcha1_imgMathCaptcha",
        "ctl00_PlaceHolderMain_ucNewLegacyControl_ucCaptcha1_imgCaptcha"
    ]

    base_url="https://www.indiapost.gov.in/_layouts/15/DOP.Portal.Tracking/TrackConsignment.aspx"
    
    for img_id in captcha_image_ids:
        img_url = get_img_src_by_id(html_content, img_id, base_url)
        if img_url:
            return img_url
    
    print("No captcha image found with the specified IDs")
    return None

def fetch_image(url, output_path=None):
    """
    Fetch an image from a URL and save it to the specified path.
    
    Args:
        url (str): The URL of the image to fetch
        output_path (str, optional): The path where to save the image.
                                    If None, saves to 'out/captcha.jpg'
    
    Returns:
        str: The path where the image was saved if successful, None otherwise
    """
    try:
        print(f"Fetching image from {url}...")
        # Use session instead of requests directly
        response = session.get(url, stream=True)
        response.raise_for_status()
        
        # Check if the content is an image
        content_type = response.headers.get('Content-Type', '')
        if not any(img_type in content_type.lower() for img_type in ['jpeg', 'jpg', 'png', 'gif']):
            print(f"Warning: URL might not be an image. Content-Type: {content_type}")
        
        # Set default output path if not specified
        output_path = os.path.join("out", "captcha.gif")
        
        # Save the image
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        print(f"Image successfully saved to {output_path}")
        return output_path
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching image: {e}")
        return None
    except IOError as e:
        print(f"Error saving image: {e}")
        return None

def fetch_tracking_page():
    """Fetch the India Post tracking page and return the content"""
    url = "https://www.indiapost.gov.in/_layouts/15/DOP.Portal.Tracking/TrackConsignment.aspx"
    try:
        print(f"Fetching data from {url}...")
        # Use session instead of requests directly
        response = session.get(url)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def save_content(content, filename):
    """Save content to the specified file"""
    try:
        with open(filename, "wb") as f:
            f.write(content)
        print(f"Data successfully saved to {filename}")
        return True
    except IOError as e:
        print(f"Error saving file: {e}")
        return False

def extract_form_fields(html_content):
    """
    Extract all form fields that need to be submitted, including hidden fields
    
    Args:
        html_content: HTML content of the page
        
    Returns:
        dict: Dictionary of form field names and values
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        form_data = {}
        
        # Extract all input fields
        for input_tag in soup.find_all('input'):
            # Skip the submit button
            if input_tag.get('type') == 'submit':
                continue
                
            name = input_tag.get('name')
            value = input_tag.get('value', '')
            
            if name:
                form_data[name] = value
                
        # Extract all select fields
        for select_tag in soup.find_all('select'):
            name = select_tag.get('name')
            if name:
                # Find the selected option
                selected_option = select_tag.find('option', selected=True)
                if selected_option:
                    form_data[name] = selected_option.get('value', '')
                else:
                    # If no option is selected, use the first one
                    first_option = select_tag.find('option')
                    if first_option:
                        form_data[name] = first_option.get('value', '')
                        
        return form_data
    except Exception as e:
        print(f"Error extracting form fields: {e}")
        return {}

def submit_tracking_form(tracking_number, captcha_answer, html_content):
    """
    Submit the tracking form with the tracking number and captcha text
    
    Args:
        tracking_number: The tracking/article number to search
        captcha_text: The text extracted from the captcha
        html_content: The original HTML content containing the form
        
    Returns:
        str: HTML content of the response page or None if submission failed
    """
    try:
        # URL for form submission
        url = "https://www.indiapost.gov.in/_layouts/15/DOP.Portal.Tracking/TrackConsignment.aspx"
        
        # Extract all existing form fields including hidden ones
        form_data = extract_form_fields(html_content)
        
        # Set form-specific fields - using correct field names
        form_data['ctl00$PlaceHolderMain$ucNewLegacyControl$txtOrignlPgTranNo'] = tracking_number
        
        # IMPORTANT: Use the correct captcha field - this is the key fix
        form_data['ctl00$PlaceHolderMain$ucNewLegacyControl$ucCaptcha1$txtCaptcha'] = captcha_answer
        
        # Set radio button value correctly 
        form_data['ctl00$PlaceHolderMain$ucNewLegacyControl$Track'] = 'rbTrackConsignment'
        
        # Add the submit button target value
        form_data['__EVENTTARGET'] = 'ctl00$PlaceHolderMain$ucNewLegacyControl$btnSearch'
        
        # Add the submit button value (may be needed in some cases)
        form_data['ctl00$PlaceHolderMain$ucNewLegacyControl$btnSearch'] = 'Search'
        
        # Add ScriptManager for AJAX handling
        form_data['ctl00$ScriptManager'] = 'ctl00$PlaceHolderMain$ucNewLegacyControl$upnlTrackConsignment|ctl00$PlaceHolderMain$ucNewLegacyControl$btnSearch'
        
        # Add LASTFOCUS field that the JavaScript might set
        if '__LASTFOCUS' not in form_data:
            form_data['__LASTFOCUS'] = ''
        
        # Mark as asynchronous post
        form_data['__ASYNCPOST'] = 'true'
        
        # Make sure __EVENTARGUMENT is empty as seen in the JavaScript code
        form_data['__EVENTARGUMENT'] = ''
        
        # Print form data for debugging
        print(f"Submitting form with tracking number: {tracking_number} and captcha: {captcha_answer}")
        
        # Set appropriate headers for form submission
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'X-Requested-With': 'XMLHttpRequest',
            'X-MicrosoftAjax': 'Delta=true',
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
            'Origin': 'https://www.indiapost.gov.in',
            'Connection': 'keep-alive',
            'Referer': url
        }
        
        # Print form data for debugging
        # Save the form data to a file for debugging
        form_data_path = os.path.join("out", "indiapost_formdata.json")
        with open(form_data_path, "w") as f:
            f.write(str(form_data))
        #print(f"Form data saved to {form_data_path}")        

        # Submit the form
        print(f"Submitting form")
        response = session.post(url, data=form_data, headers=headers)
        response.raise_for_status()
        
        # Check if response contains tracking results
        if "No Records Found" in response.text:
            print("No tracking records found for the given number")
        elif "Invalid Captcha" in response.text:
            print("Invalid captcha entered")
        else:
            print("Form submitted successfully")
            
        # Save the response
        save_content(response.content, os.path.join("out", "indiapost_tracking_result.html"))
        
        return response.content
    except Exception as e:
        print(f"Error submitting form: {e}")
        import traceback
        traceback.print_exc()
        return None

def details_tables_to_json(content):
    print(f"Parsing details table from content...")
    try:
        detail_soup = BeautifulSoup(content, 'html.parser')
        table_rows = detail_soup.find_all('tr')

        result = {}  # Change this from list to dictionary
        
        if len(table_rows) > 1:  # Ensure we have header and data rows
            # Get column headers (from first row th elements)
            headers = [th.get_text().strip() for th in table_rows[0].find_all('th')]
            
            # Get data from second row (first data row)
            data_cells = table_rows[1].find_all('td')
            data_values = [td.get_text().strip() for td in data_cells]
            
            # Create dictionary from headers and values
            detail_dict = dict(zip(headers, data_values))
            
            # Add these details to our result
            result["booked_at"] = detail_dict.get("Booked At", "")
            result["booked_on"] = detail_dict.get("Booked On", "")
            result["destination_pincode"] = detail_dict.get("Destination Pincode", "")
            result["article_type"] = detail_dict.get("Article Type", "")
            result["delivery_location"] = detail_dict.get("Delivery Location", "")
            result["delivery_time"] = detail_dict.get("Delivery Confirmed On", "")
            
            # Set the date_time field to the delivery or booking time
            if detail_dict.get("Delivery Confirmed On"):
                result["date_time"] = detail_dict.get("Delivery Confirmed On")
            else:
                result["date_time"] = detail_dict.get("Booked On", "")
                
            # Set the location field
            if detail_dict.get("Delivery Location"):
                result["location"] = detail_dict.get("Delivery Location")
            else:
                result["location"] = detail_dict.get("Booked At", "")
                
            # Add the full details dictionary to the result
            result["details"] = detail_dict
            
            #print(f"Extracted shipping details: {detail_dict}")
            
        return result  # Add a return statement
    except Exception as e:
        print(f"Error parsing detail table: {e}")
        return None  # Return None on error

def get_delivery_status(content, tracking_number):
    """
    Extract delivery status from the tracking results HTML content.
    
    Args:
        content (bytes or str): The HTML content of the tracking results page
        tracking_number (str): The tracking number being tracked
        
    Returns:
        dict: JSON-like dictionary with tracking number, status, and complete status text
    """
    try:
        # ID of the status element
        status_element_id = "ctl00_PlaceHolderMain_ucNewLegacyControl_lblMailArticleCurrentStatusOER"
        delivery_status = get_html_value_by_id(content, status_element_id)
        
        # If status element was not found or is empty
        if not delivery_status:
            print("Status information not found in the response")
            return {
                "tracking_number": tracking_number,
                "status": "unknown",
                "status_txt": "Status information not available"
            }

        # ID of the status element
        detail_table_id = "ctl00_PlaceHolderMain_ucNewLegacyControl_gvTrckMailArticleDtlsOER"
        detail_table = get_html_value_by_id(content, detail_table_id)
        if detail_table:
            details_table_json = details_tables_to_json(detail_table)
            #print(f"Details Table JSON: {details_table_json}")
                    
        # Clean up the status text
        status_text = delivery_status.strip()
        
        # Determine the status category
        status_category = "transit"  # Default status
        
        if "Item Delivered" in status_text:
            status_category = "delivered"
        elif "failure" in status_text.lower() or "returned" in status_text.lower():
            status_category = "returned"
        elif "attempted" in status_text.lower():
            status_category = "attempted"
        elif "received" in status_text.lower() or "booked" in status_text.lower():
            status_category = "booked"
        # Keep as "transit" for all other statuses
        
        # Create result dictionary
        result = {
            "tracking_number": tracking_number,
            "status": status_category,
            "location": details_table_json.get("delivery_location", "") if details_table_json else "",
            "date_time": details_table_json.get("date_time", "") if details_table_json else "",
            "status_txt": details_table_json
        }
        
        # Print the result for debugging
        #print(f"Delivery Status: {result}")
        
        return result
    
    except Exception as e:
        print(f"Error extracting delivery status: {e}")
        return {
            "tracking_number": tracking_number,
            "status": "error",
            "status_txt": f"Error extracting status: {str(e)}"
        }
    
#################################################
def track_consignment(tracking_number):
    """
    Main function to track a consignment using the tracking number
    
    Args:
        tracking_number: The tracking/article number to search
        
    Returns:
        str: HTML content of the result page or None if tracking failed
    """

    output_dir = "out"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Fetch the tracking page
    content = fetch_tracking_page()
    if not content:
        return None
    
    # Extract the captcha question
    captcha_question_id = "ctl00_PlaceHolderMain_ucNewLegacyControl_ucCaptcha1_lblCaptcha"
    captcha_question = get_html_value_by_id(content, captcha_question_id)
    if not captcha_question:
        print("Captcha question not found, ID: {captcha_question_id}")
        return None
    else:
        print(f"Captcha Question: {captcha_question}")
    
    # Extract the captcha image URL
    captcha_img_url = get_captcha_img_url(content)
    if not captcha_img_url:
        return None
    
    # Download the captcha image
    captcha_img_path = fetch_image(captcha_img_url)
    if not captcha_img_path:
        return None
    
    # Process the captcha
    captcha_img_path = 'out/captcha.gif'
    captcha_text = ocr.ocr_processor(captcha_img_path)
    if not captcha_text:
        return None
    
    captcha_answer = captcha2answer(captcha_question, captcha_text)
    print(f"Captcha Answer: {captcha_answer}")

    # Submit the form with the tracking number and captcha
    content = submit_tracking_form(tracking_number, captcha_answer, content)

    tracking_result = get_delivery_status(content, tracking_number)

    return tracking_result

class IndiaPostTracker:
    """
    Tracker implementation for India Post courier service.
    """
    
    def track(self, awb_number):
        """
        Track an India Post AWB number.
        
        Args:
            awb_number (str): The AWB tracking number
            
        Returns:
            dict: Tracking status information
        """
        # Call the track_consignment function to get real tracking data
        tracking_result = track_consignment(awb_number)
        return tracking_result

