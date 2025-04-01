from awb_tracking import AWBTracker
import csv
import time
import os
import sys

if __name__ == '__main__':
    # Check if command-line argument is provided
    if len(sys.argv) < 2:
        print("Usage: python test_tracking_bluk.py <csv_file>")
        print("Example: python test_tracking_bluk.py tracking_number.csv")
        print("CSV file should contain 'courier' and 'awb_number' columns")
        exit(1)
    
    # Get CSV file name from command-line argument
    csv_file = sys.argv[1]
    
    # Create an instance of the AWBTracker
    tracker = AWBTracker()
    
    # Check if file exists
    if not os.path.exists(csv_file):
        print(f"Error: File {csv_file} not found.")
        exit(1)
    
    # Read CSV file
    tracking_data = []
    with open(csv_file, 'r', newline='') as file:
        reader = csv.DictReader(file)
        tracking_data = list(reader)
    
    # Process each row
    for row in tracking_data:
        courier = row.get('courier', '')
        awb_no = row.get('awb_number', '')
        status = row.get('status', '')
        
        # Skip if status is already filled
        if status:
            print(f"Skipping {courier} AWB: {awb_no} - Status already exists")
            continue
        
        if not courier or not awb_no:
            print(f"Skipping row with missing courier or AWB number: {row}")
            continue
            
        print(f"Processing {courier} AWB: {awb_no}")
        
        # Get the appropriate tracking method
        if hasattr(tracker, courier.lower()):
            tracker_func = getattr(tracker, courier.lower())
            try:
                # Track directly without retries
                result = tracker_func(awb_no)
                
                # Update row with tracking results
                if isinstance(result, dict):
                    row['location'] = result.get('location', '')
                    row['date'] = result.get('date', '')
                    row['status'] = result.get('status', '')
                else:
                    # Handle case where result is not a dictionary
                    row['status'] = str(result)
            except Exception as e:
                row['status'] = f"Error: {str(e)}"
                print(f"Error tracking {courier} AWB {awb_no}: {str(e)}")
        else:
            row['status'] = f"Unsupported courier: {courier}"
            print(f"Unsupported courier: {courier}")
    
    # Write updated data back to CSV
    with open(csv_file, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=tracking_data[0].keys())
        writer.writeheader()
        writer.writerows(tracking_data)
    
    print(f"Successfully updated tracking information in {csv_file}")
