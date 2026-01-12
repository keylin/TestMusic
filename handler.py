import re
from flask import request, jsonify
from logic import neteasy, qqmusic, qishuimusic, applemusic, excel_export
from models import Result

# Regex patterns
NET_EASY_REGEX = re.compile(r'(163cn)|(\.163\.)')
QQ_MUSIC_REGEX = re.compile(r'.qq.')
QISHUI_MUSIC_REGEX = re.compile(r'(qishui)|(douyin)')
APPLE_MUSIC_REGEX = re.compile(r'music\.apple\.com')

SUCCESS_CODE = 1
FAILURE_CODE = 2

import logging


from utils import common

# logger = logging.getLogger(__name__)

def music_handler():
    raw_link = request.form.get('url')
    # Pre-process: Extract URL from text (handles sharing text from apps)
    link = common.standard_url(raw_link) if raw_link else ""
    

    
    try:
        # ... existing logic ...
        if NET_EASY_REGEX.search(link):
            song_list = neteasy.net_easy_discover(link)
        elif QQ_MUSIC_REGEX.search(link):
            if link == "https://i.y.qq.com/v8/playsong.html":
                 return jsonify(Result(code=FAILURE_CODE, msg="Invalid link", data=None).__dict__), 200
            song_list = qqmusic.qq_music_discover(link)
        elif QISHUI_MUSIC_REGEX.search(link):
            song_list = qishuimusic.qishui_music_discover(link)
        elif APPLE_MUSIC_REGEX.search(link):
            song_list = applemusic.apple_music_discover(link)
        else:
            return jsonify(Result(code=FAILURE_CODE, msg="Unsupported link format", data=None).__dict__), 200
            
        deduplicate_songs(song_list)
        return jsonify(Result(code=SUCCESS_CODE, msg="success", data=song_list.__dict__).__dict__)
        
    except Exception as e:
        return jsonify(Result(code=FAILURE_CODE, msg=str(e), data=None).__dict__), 200



def deduplicate_songs(song_list):
    if not song_list or not song_list.songs:
        return
        
    seen = set()
    unique_songs = []
    duplicates_count = 0
    
    for song in song_list.songs:
        # Song string is already "Name - Singer"
        if song not in seen:
            seen.add(song)
            unique_songs.append(song)
        else:
            duplicates_count += 1
            
    song_list.songs = unique_songs
    song_list.songs_count = len(unique_songs)
    song_list.duplicate_count = duplicates_count

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
