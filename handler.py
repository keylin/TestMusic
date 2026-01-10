import re
from flask import request, jsonify
from logic import neteasy, qqmusic, qishuimusic, excel_export
from models import Result

# Regex patterns
NET_EASY_REGEX = re.compile(r'(163cn)|(\.163\.)')
QQ_MUSIC_REGEX = re.compile(r'.qq.')
QISHUI_MUSIC_REGEX = re.compile(r'(qishui)|(douyin)')

SUCCESS_CODE = 1
FAILURE_CODE = 2

import logging


from utils import common

# logger = logging.getLogger(__name__)

def music_handler():
    raw_link = request.form.get('url')
    # Pre-process: Extract URL from text (handles sharing text from apps)
    link = common.standard_url(raw_link) if raw_link else ""
    
    detailed = request.args.get('detailed') == 'true'
    fmt = request.args.get('format')
    order = request.args.get('order')
    
    try:
        # ... existing logic ...
        if NET_EASY_REGEX.search(link):
            song_list = neteasy.net_easy_discover(link, detailed)
        elif QQ_MUSIC_REGEX.search(link):
            if link == "https://i.y.qq.com/v8/playsong.html":
                 return jsonify(Result(code=FAILURE_CODE, msg="Invalid link", data=None).__dict__), 200
            song_list = qqmusic.qq_music_discover(link, detailed)
        elif QISHUI_MUSIC_REGEX.search(link):
            song_list = qishuimusic.qishui_music_discover(link, detailed)
        else:
            return jsonify(Result(code=FAILURE_CODE, msg="Unsupported link format", data=None).__dict__), 200
            
        format_song_list(song_list, fmt)
        process_song_order(song_list, order)
        
        return jsonify(Result(code=SUCCESS_CODE, msg="success", data=song_list.__dict__).__dict__)
        
    except Exception as e:
        return jsonify(Result(code=FAILURE_CODE, msg=str(e), data=None).__dict__), 200

def format_song_list(song_list, fmt):
    if not song_list or not song_list.songs:
        return

    if not fmt or fmt == "song-singer":
        return

    new_songs = []
    # ... existing processing ...
    for song in song_list.songs:
        parts = song.split(" - ")
        if fmt == "singer-song":
            if len(parts) >= 2:
                # Reconstruct singer - song 
                new_songs.append(f"{parts[1]} - {parts[0]}")
            else:
                new_songs.append(song)
        elif fmt == "song":
            if len(parts) > 0:
                new_songs.append(parts[0])
            else:
                new_songs.append(song)
        else:
            new_songs.append(song)
            
    song_list.songs = new_songs

def process_song_order(song_list, order):
    if not song_list or not song_list.songs:
        return
        
    if order == "reverse":
        song_list.songs.reverse()

from flask import send_file

def excel_handler():
    try:
        data = request.json
        songs = data.get('songs', [])
        
        if not songs:
            return jsonify(Result(code=FAILURE_CODE, msg="No songs to export", data=None).__dict__), 200
            
        excel_io = excel_export.generate_excel(songs)
        
        return send_file(
            excel_io,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='songlist.xlsx'
        )
    except Exception as e:
        return jsonify(Result(code=FAILURE_CODE, msg=str(e), data=None).__dict__), 200
