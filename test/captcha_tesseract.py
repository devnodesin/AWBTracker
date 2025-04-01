import argparse
import pytesseract
from PIL import Image
import os
import cv2
import numpy as np

def preprocess_image(image):
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
    try:
        # Open the image
        image = Image.open(image_path)
        
        # Print image info if debug is enabled
        if debug:
            print(f"Image format: {image.format}, Size: {image.size}, Mode: {image.mode}")
        
        # Preprocess the image for better OCR results
        preprocessed = preprocess_image(image)
        
        # Save preprocessed image if debug is enabled
        if debug:
            debug_path = f"{os.path.splitext(image_path)[0]}_preprocessed.png"
            preprocessed.save(debug_path)
            print(f"Saved preprocessed image to {debug_path}")
        
        # Configure Tesseract options for captcha
        config = '--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        
        # Use Tesseract to do OCR with custom configuration
        text = pytesseract.image_to_string(preprocessed, config=config)
        print(f"OCR results for: {text}")
        # Clean up the result
        text = text.strip()
        
        return text
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None

def main():
    # 1. Setup command line argument parser
    parser = argparse.ArgumentParser(description='Perform OCR on images using Tesseract')
    parser.add_argument('files', nargs='+', help='Image file(s) to process')
    parser.add_argument('--debug', action='store_true', help='Save preprocessed images and show debug info')
    args = parser.parse_args()
    
    # Process each file
    for file_path in args.files:
        if os.path.isfile(file_path):
            text = ocr_tesseract(file_path, args.debug)
            if text:
                print(f"OCR results for {file_path}: {text}")
        else:
            print(f"File not found: {file_path}")

if __name__ == "__main__":
    main()
