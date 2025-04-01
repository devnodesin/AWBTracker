import sys
import os
from awb_tracking.ocr import ocr_processor

def main():
    # Check if image path is provided as command line argument
    if len(sys.argv) < 2:
        print("Usage: python test_ocr.py <image_path>")
        sys.exit(1)
    
    # Get image path from command line arguments
    image_path = sys.argv[1]
    
    # Process the image with both OCR engines
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return None, None
    
    print(f"Processing image: {image_path}")
    
    # Process with EasyOCR
    print("\n=== EasyOCR Results ===")
    easyocr_results = ocr_processor(image_path, ocr="easyocr")
    print(easyocr_results)
    
    # Process with Tesseract
    print("\n=== Tesseract Results ===")
    tesseract_results = ocr_processor(image_path)
    print(tesseract_results)

if __name__ == "__main__":
    main()
