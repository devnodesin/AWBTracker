# AWB Tracker

AWBTracker is a Python package for tracking shipments across multiple courier and logistics providers, including India Post, DTDC, Delhivery, Ecom Express, VRL Logistics, ST Courier, and more.

## Features

✅ Unified tracking interface for multiple couriers
✅ Simple usage: tracker.indiapost("AWB123456789")
✅ Supports API-based and web-scraped tracking
✅ Easily extendable for new logistics providers

## Installation

1. Clone the repository or download the source code
2. Install the required Python packages:

```bash
pip install requests beautifulsoup4 easyocr pillow
```

## Usage

```python
from awb_tracking import AWBTracker

tracker = AWBTracker()
status = tracker.indiapost("AWB123456789")
print(status)
```

## Contributing

Feel free to submit PRs for new couriers or improvements! 🚀
