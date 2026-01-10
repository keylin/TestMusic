# MyMusic Python Version

This is a Python rewrite of the MyMusic project, using Flask.

## Prerequisites

- Python 3.8+
- pip

## Installation

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the server:
   ```bash
   python3 -m python_version.main
   ```
   The server will start on port 8888.

2. Test endpoints:
   ```bash
   curl -X POST -d "url=https://y.qq.com/n/ryqq/playlist/7364061065" http://localhost:8888/songlist
   ```

## Structure

- `main.py`: Entry point and Flask app setup.
- `handler.py`: Request handling and routing.
- `logic/`: Core logic for scraping/API calls (Netease, QQ, Qishui).
- `utils/`: Utility functions (encryption, HTTP).
- `models.py`: Data structures.

## Logic Implementation Notes

- **Netease**: Uses API v3/v6. Note that some Netease APIs might return 401 without valid cookies.
- **QQ Music**: Implements the `sign` generation logic and handles pagination.
- **Qishui**: Uses BeautifulSoup for HTML parsing.
