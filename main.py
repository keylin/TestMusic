from flask import Flask, request, send_from_directory
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from handler import music_handler, excel_handler

# Resolve paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'frontend', 'dist')

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path='')

@app.route('/')
def index():
    return send_from_directory(STATIC_DIR, 'index.html')

# Register route
app.add_url_rule('/songlist', view_func=music_handler, methods=['POST'])
app.add_url_rule('/export/excel', view_func=excel_handler, methods=['POST'])

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'
    app.run(host='0.0.0.0', port=8866, debug=debug_mode)
