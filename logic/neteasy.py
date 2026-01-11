import json
import concurrent.futures
from utils import httputil, common
from models import SongList

NET_EASY_URL_V6 = "https://music.163.com/api/v6/playlist/detail"
NET_EASY_URL_V3 = "https://music.163.com/api/v3/song/detail"
CHUNK_SIZE = 400

def net_easy_discover(link):
    # 1. Get playlist basic info
    song_ids_resp = get_songs_info(link)
    if not song_ids_resp:
        raise Exception("Unable to get playlist info or permission denied")

    playlist = song_ids_resp.get("playlist", {})
    playlist_name = playlist.get("name", "")
    track_ids = playlist.get("trackIds", [])
    tracks_count = playlist.get("trackCount", 0)

    if not track_ids:
        return SongList(name=playlist_name, songs=[], songs_count=0)

    # In Python rewrite, we simplify and assume detailed mode or just fetching all.
    # The Go version had caching. Here we just fetch.
    
    all_song_ids = [track['id'] for track in track_ids]
    
    # Fetch details
    song_details = batch_get_songs(all_song_ids)
    
    # Sort songs based on original order
    songs = []
    for song_id in all_song_ids:
        if song_id in song_details:
            songs.append(song_details[song_id])
            
    return SongList(name=playlist_name, songs=songs, songs_count=tracks_count)

def get_songs_info(link):
    song_list_id = common.get_net_easy_param(link)
    if not song_list_id:
        raise Exception("Failed to parse link")
        
    resp = httputil.post(NET_EASY_URL_V6, data={"id": song_list_id})
    if resp.status_code != 200:
        raise Exception("Failed to request NetEasy API")
    
    data = resp.json()
    if data.get("code") == 401:
        raise Exception("Permission denied")
        
    return data

def batch_get_songs(song_ids):
    results = {}
    chunks = [song_ids[i:i + CHUNK_SIZE] for i in range(0, len(song_ids), CHUNK_SIZE)]
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_chunk = {executor.submit(process_chunk, chunk): chunk for chunk in chunks}
        for future in concurrent.futures.as_completed(future_to_chunk):
            try:
                chunk_result = future.result()
                results.update(chunk_result)
            except Exception as e:
                print(f"Chunk processing failed: {e}")
                
    return results

def process_chunk(chunk):
    # Go's json.Marshal uses no spaces.
    c_param = json.dumps([{"id": x} for x in chunk], separators=(',', ':'))
    resp = httputil.post(NET_EASY_URL_V3, data={"c": c_param})
    data = resp.json()
    
    chunk_map = {}
    songs = data.get("songs", [])
    for song in songs:
        name = song.get("name", "")
        name = common.standard_song_name(name)
            
        artists = [ar.get("name", "") for ar in song.get("ar", [])]
        author = " / ".join(artists)
        
        chunk_map[song['id']] = f"{name} - {author}"
        
    return chunk_map
