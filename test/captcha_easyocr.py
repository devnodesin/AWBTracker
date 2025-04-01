import argparse
import easyocr
import os

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Perform OCR on image files using EasyOCR')
    parser.add_argument('files', nargs='+', help='Image files to process')
    args = parser.parse_args()
    
    # Initialize EasyOCR reader (for English)
    print("Initializing EasyOCR reader...")
    reader = easyocr.Reader(['en'])
    
    # Process each file
    for file_path in args.files:
        if not os.path.isfile(file_path):
            print(f"Error: {file_path} is not a valid file")
            continue
        
        print(f"\nProcessing {file_path}...")
        
        # Perform OCR
        results = reader.readtext(file_path)
        
        # Print extracted text
        print("Extracted text:")
        if not results:
            print("No text detected.")
        else:
            for detection in results:
                text = detection[1]  # The text is the second element in each detection
                confidence = detection[2]  # The confidence score is the third element
                print(f"- {text} (confidence: {confidence:.2f})")

if __name__ == "__main__":
    main()
