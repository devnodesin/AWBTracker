"""
OCR utilities for processing India Post captcha images.
"""
import easyocr
import os
import base64
import urllib.request
import logging
from PIL import Image


def convert_to_jpg(image_path, output_jpg=None):
    """
    Convert image to JPG format for better OCR processing.
    
    Args:
        image_path: Path to the source image
        output_jpg: Path for output JPG (if None, uses out/captcha.jpg)
        
    Returns:
        Path to the JPG image
    """
    # Check if file exists
    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        return None
    
    # Check if already a jpg/jpeg
    if image_path.lower().endswith(('.jpg', '.jpeg')):
        # For JPG files, just verify we can open it
        try:
            with Image.open(image_path) as img:
                # Validate image dimensions
                width, height = img.size
                if width == 0 or height == 0:
                    print(f"Invalid image dimensions: {width}x{height}")
                    return None
                return image_path
        except Exception as e:
            print(f"Failed to verify existing JPG: {e}")
            return None
    
    # Generate output filename if not provided
    if not output_jpg:
        output_dir = "out"
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_jpg = os.path.join(output_dir, "captcha.jpg")
    
    try:
        # Open and convert image
        with Image.open(image_path) as img:
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Validate image dimensions
            width, height = img.size
            if width == 0 or height == 0:
                print(f"Invalid image dimensions: {width}x{height}")
                return None
            
            # Save as JPG
            img.save(output_jpg, 'JPEG')
            
        # Verify the output file exists
        if not os.path.exists(output_jpg) or os.path.getsize(output_jpg) == 0:
            print(f"Failed to save output JPG or file is empty: {output_jpg}")
            return None
            
        print(f"Converted {image_path} to {output_jpg}")
        return output_jpg
    
    except Exception as e:
        print(f"Image conversion failed: {e}")
        return None

def ocr_processor(image_path):
    """
    Process captcha image and extract text using OCR.       
    Returns:
        Extracted text string or None if processing failed
    """
    # Convert to JPG (will use out/captcha.jpg by default)
    jpg_path = convert_to_jpg(image_path)
    if not jpg_path:
        print(f"Failed to convert image to JPG: {image_path}")
        return None
    
    try:
        # Verify the image file before processing
        if not os.path.exists(jpg_path) or os.path.getsize(jpg_path) == 0:
            print(f"Invalid or empty JPG file: {jpg_path}")
            return None
            
        # Test that we can open the image
        try:
            with Image.open(jpg_path) as test_img:
                img_width, img_height = test_img.size
                print(f"Image dimensions: {img_width}x{img_height}")
        except Exception as img_error:
            print(f"Failed to verify image before OCR: {img_error}")
            return None
        
        # Initialize EasyOCR with minimal verbosity
        reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        
        # Perform OCR
        print(f"Processing image with EasyOCR: {jpg_path}")
        results = reader.readtext(jpg_path)
        
        # Process results - combine all detections and remove spaces
        if results:
            text = "".join([detection[1].replace(" ", "") for detection in results])
            print(f"OCR extracted: '{text}'")
            return text
        else:
            print("No text detected in captcha")
            return ""
    
    except Exception as e:
        print(f"OCR processing failed: {e}")
        # Print more detailed error information
        import traceback
        traceback.print_exc()
        return None
