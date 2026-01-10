import json
import time
import re
from utils import httputil, sign, common
from models import SongList

QQ_MUSIC_API_URL = "https://u6.y.qq.com/cgi-bin/musics.fcg?sign={}&_={}"
MAX_SONGS_PER_PAGE = 1000
MAX_TOTAL_SONGS = 10000

# Regex
PLAYLIST_LINK_REGEX = re.compile(r'.*playlist/(\d+)$')
ID_PARAM_LINK_REGEX = re.compile(r'id=(\d+)')
SHORT_LINK_REGEX = re.compile(r'fcgi-bin')
DETAILS_LINK_REGEX = re.compile(r'details')

def qq_music_discover(link, detailed):
    tid = extract_playlist_id(link)
    if not tid:
        raise Exception("Invalid playlist link")
        
    data = fetch_playlist_data(tid)
    if not data:
        raise Exception("Failed to fetch playlist data")
        
    resp = json.loads(data)
    return build_song_list(resp, detailed)

def extract_playlist_id(link):
    match = PLAYLIST_LINK_REGEX.search(link)
    if match:
        return int(match.group(1))
        
    match = ID_PARAM_LINK_REGEX.search(link)
    if match:
        return int(match.group(1))
        
    if SHORT_LINK_REGEX.search(link):
        redirected = httputil.get_redirect_location(link)
        return extract_playlist_id(redirected)
        
    if DETAILS_LINK_REGEX.search(link):
        try:
            tid_str = common.get_qq_music_param(link)
            if tid_str:
                return int(tid_str)
        except Exception as e:
            print(f"Error extracting param: {e}")
            
    return None

def fetch_playlist_data(tid):
    try:
        # First page request
        basic_info_bytes = fetch_playlist_page(tid, 0, MAX_SONGS_PER_PAGE)
        if not basic_info_bytes:
             return None
             
        basic_info = json.loads(basic_info_bytes)
        
        # Check total songs
        dirinfo = basic_info.get('req_0', {}).get('data', {}).get('dirinfo', {})
        songlist = basic_info.get('req_0', {}).get('data', {}).get('songlist', [])
        
        total_songs = dirinfo.get('songnum', 0)
        received_songs = len(songlist)
        
        # If we got all songs, return immediately
        if received_songs >= total_songs:
            return basic_info_bytes

        # Pagination logic
        if total_songs > MAX_TOTAL_SONGS:
            total_songs = MAX_TOTAL_SONGS
            
        all_songs = list(songlist)
        current_count = received_songs
        
        while current_count < total_songs:
            # Determine chunk size.
            num_to_fetch = min(MAX_SONGS_PER_PAGE, total_songs - current_count)
            
            # Sanity check to avoid infinite loop if 0 requested
            if num_to_fetch <= 0:
                break
                
            page_bytes = fetch_playlist_page(tid, current_count, num_to_fetch)
            if not page_bytes:
                # Failed to fetch page, stopping partial
                break
                
            page_data = json.loads(page_bytes)
            new_songs = page_data.get('req_0', {}).get('data', {}).get('songlist', [])
            
            if not new_songs:
                break
                
            all_songs.extend(new_songs)
            current_count += len(new_songs)
            
            # Safety break if we aren't making progress
            if len(new_songs) == 0:
                break

        # Update the basic_info with full list
        basic_info['req_0']['data']['songlist'] = all_songs
        basic_info['req_0']['data']['dirinfo']['songnum'] = len(all_songs)
        
        return json.dumps(basic_info).encode('utf-8')
        
    except Exception as e:
        print(f"Fetch playlist data error: {e}")
        return None

def fetch_playlist_page(tid, begin, num):
    platforms = ["-1", "android", "iphone", "h5", "wxfshare", "iphone_wx", "windows"]
    for platform in platforms:
        req_data = {
            "req_0": {
                "module": "music.srfDissInfo.DissInfo",
                "method": "CgiGetDiss",
                "param": {
                    "disstid": tid,
                    "song_begin": begin,
                    "song_num": num,
                    "orderlist": 1,
                    "userinfo": 1,
                    "tag": 1
                }
            },
            "comm": {
                "g_tk": 5381,
                "uin": "",
                "format": "json",
                "ct": 24,
                "cv": 0,
                "platform": platform
            }
        }
        # Serialize with tight separators and sorted keys for signature consistency
        param_str = json.dumps(req_data, separators=(',', ':'), sort_keys=True)
        signature = sign.encrypt(param_str)
        url = QQ_MUSIC_API_URL.format(signature, int(time.time() * 1000))
        
        try:
            resp = httputil.post(url, data=param_str)
            if len(resp.content) != 108: # Error response length check from Go code
                try:
                    # Check if response is actually valid JSON and successful
                    data = json.loads(resp.content)
                    if data.get('req_0', {}).get('data') and data.get('req_0', {}).get('code') == 0:
                        return resp.content
                except:
                    pass
        except Exception as e:
            # print(f"Platform {platform} failed: {e}")
            pass
            
    return None

def build_song_list(resp, detailed):
    req_0 = resp.get('req_0', {})
    data = req_0.get('data')
    
    if not data:
        code = req_0.get('code')
        msg = req_0.get('msg', 'Unknown Error')
        raise Exception(f"QQ Music API Error: {code} - {msg} (Possible IP restriction)")

    dirinfo = data.get('dirinfo')
    songlist = data.get('songlist')
    
    if not dirinfo or songlist is None:
         raise Exception("Invalid Playlist Data from QQ Music")

    songs = []
    for song in songlist:
        name = song.get('name', 'Unknown')
        if not detailed:
            name = common.standard_song_name(name)
            
        singers = [s.get('name', '') for s in song.get('singer', [])]
        singer_str = " / ".join(singers)
        
        songs.append(f"{name} - {singer_str}")
        
    return SongList(name=dirinfo.get('title', 'Unknown Playlist'), songs=songs, songs_count=dirinfo.get('songnum', len(songs)))
