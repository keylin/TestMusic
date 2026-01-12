import json
import re
from bs4 import BeautifulSoup
from utils import httputil, common
from models import SongList

def apple_music_discover(link):
    html_content = httputil.get(link).content.decode('utf-8')
    soup = BeautifulSoup(html_content, 'html.parser')
    
    script = soup.find('script', {'id': 'serialized-server-data', 'type': 'application/json'})
    if not script:
        raise Exception("Could not find Apple Music data script")

    try:
        data_list = json.loads(script.string)
        if not isinstance(data_list, list) or not data_list:
            raise Exception("Invalid JSON structure")
            
        data = data_list[0].get('data', {})
        sections = data.get('sections', [])
        
        song_list = []
        playlist_name = "Unknown Playlist"
        
        # First pass to find playlist name (usually in header or section 0)
        # In debug log: Section 0 first item Title: "Favorite Songs", Kind: "playlist"
        # Section 1 first item Title: "Song Name", Kind: "song"
        
        for section in sections:
            items = section.get('items', [])
            if not items:
                continue
                
            first_item = items[0]
            kind = first_item.get('contentDescriptor', {}).get('kind')
            
            # Identify Playlist Title
            # Sometimes it's in a header section
            if kind == 'playlist' and not playlist_name:
                 # Try to get title from the playlist item
                 playlist_name = first_item.get('title', playlist_name)
                 
            # Identify Song List section
            if kind == 'song':
                for item in items:
                    song_name = item.get('title', 'Unknown')
                    song_name = common.standard_song_name(song_name)
                    
                    artist_name = item.get('artistName', '')
                    if not artist_name:
                         # Fallback to extract from secondary text if needed, but artistName usually exists
                         pass

                    full_name = f"{song_name} - {artist_name}"
                    song_list.append(full_name)

        # Fallback for playlist name if not found in sections
        if playlist_name == "Unknown Playlist":
            title_tag = soup.find('title')
            if title_tag:
                 playlist_name = title_tag.get_text().replace(' - Apple Music', '').strip()

        return SongList(name=playlist_name, songs=song_list, songs_count=len(song_list))

    except Exception as e:
        print(f"Error parsing Apple Music data: {e}")
        raise Exception(f"Failed to parse Apple Music data: {e}")
