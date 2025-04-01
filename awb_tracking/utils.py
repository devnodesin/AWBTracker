from bs4 import BeautifulSoup

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