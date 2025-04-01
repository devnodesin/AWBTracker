"""
OCR utilities for processing India Post captcha images.
"""
import easyocr
import os
from PIL import Image
import pytesseract
import cv2
import numpy as np


def convert_to_jpg(image_path, output_jpg=None):
    """
    Convert image (gif,png) to JPG format for better OCR processing.
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

def ocr_easyocr(image_path, debug=False):
    """
    Process captcha image and extract text using EasyOCR.
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
                if debug:
                    print(f"Image dimensions: {img_width}x{img_height}")
        except Exception as img_error:
            print(f"Failed to verify image before OCR: {img_error}")
            return None
        
        # Initialize EasyOCR with minimal verbosity
        reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        
        # Perform OCR
        if debug:
            print(f"Processing image with EasyOCR: {jpg_path}")
        results = reader.readtext(jpg_path)
        
        # Process results - combine all detections and remove spaces
        if results:
            text = "".join([detection[1].replace(" ", "") for detection in results])
            if debug:
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

def opencv_preprocess_image(image):
    """
    Preprocess image for better OCR results with Tesseract.
    
    Args:
        image: PIL Image object
        
    Returns:
        Preprocessed PIL Image
    """
    # Convert PIL Image to cv2 format
    img = np.array(image)
    
    # Convert to grayscale if it's not already
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    # Apply thresholding to make text more distinct
    _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Optional: Remove noise
    img = cv2.medianBlur(img, 3)
    
    # Convert back to PIL Image
    return Image.fromarray(img)

def ocr_tesseract(image_path, debug=False):
    """
    Process captcha image and extract text using Tesseract OCR.
    
    Args:
        image_path: Path to the image file
        debug: Whether to print debug information
        
    Returns:
        Extracted text string or None if processing failed
    """
    try:
        # Open the image
        image = Image.open(image_path)
        
        # Print image info if debug is enabled
        if debug:
            print(f"Image format: {image.format}, Size: {image.size}, Mode: {image.mode}")
        
        # Preprocess the image for better OCR results
        preprocessed = opencv_preprocess_image(image)
        
        # Save preprocessed image if debug is enabled
        if debug:
            debug_path = f"{os.path.splitext(image_path)[0]}_preprocessed.png"
            preprocessed.save(debug_path)
            print(f"Saved preprocessed image to {debug_path}")
        
        # Configure Tesseract options for captcha
        config = '--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        
        # Use Tesseract to do OCR with custom configuration
        text = pytesseract.image_to_string(image, config=config)
        
        # Clean up the result
        text = text.strip()
        
        if debug:
            print(f"Tesseract OCR results: '{text}'")
            
        return text
    except Exception as e:
        print(f"Error processing {image_path} with Tesseract: {e}")
        return None

def ocr_processor(image_path, ocr="easyocr", debug=True):
    """
    Process captcha image and extract text using the specified OCR engine.
    
    Args:
        image_path: Path to the image file
        ocr: OCR engine to use ('tesseract' or 'easyocr')
        debug: Whether to print debug information
        
    Returns:
        Extracted text string or None if processing failed
    """
    if ocr.lower() == "easyocr":
        return ocr_easyocr(image_path, debug)
    else:  # default to tesseract
        return ocr_tesseract(image_path, debug)
