import re
from urllib.parse import urlparse, quote
from bs4 import BeautifulSoup
from utils import httputil, common
from models import SongList

QISHUI_V3_REGEX = re.compile(r'https?://qishui\.douyin\.com/s/[a-zA-Z0-9]+/?')
QISHUI_V1_REGEX = re.compile(r'https?://[a-zA-Z0-9./?=&_-]+')

def qishui_music_discover(link):
    extracted_link = QISHUI_V3_REGEX.search(link)
    if extracted_link:
        link = extracted_link.group(0)
    
    # Follow potential redirects and fetch the final page
    resp = httputil.get(link)
    if resp.status_code != 200:
        raise Exception("Failed to fetch Qishui music page")
        
    return parse_song_list(resp.text)

def parse_song_list(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Selectors from Go code:
    # Name: #root > div > div > div > div > div:nth-child(1) > div:nth-child(3) > h1 > p
    # Author: ... > div > div > div:nth-child(2) > p
    
    # BS4 select is similar to querySelector
    try:
        name_el = soup.select_one("#root > div > div > div > div > div:nth-child(1) > div:nth-child(3) > h1 > p")
        author_el = soup.select_one("#root > div > div > div > div > div:nth-child(1) > div:nth-child(3) > div > div > div:nth-child(2) > p")
        
        name = name_el.get_text() if name_el else "Unknown"
        author = author_el.get_text() if author_el else "Unknown"
        
        list_name = f"{name}-{author}"
        
        songs = []
        
        # Song items
        items = soup.select("#root > div > div > div > div > div:nth-child(2) > div > div > div > div > div")
        
        for item in items:
            title_el = item.select_one("div:nth-child(2) > div:nth-child(1) > p")
            artist_el = item.select_one("div:nth-child(2) > div:nth-child(2) > p")
            
            title = title_el.get_text() if title_el else ""
            artist = artist_el.get_text() if artist_el else ""
            
            # Remove "•" and after
            if "•" in artist:
                artist = artist.split("•")[0].strip()
                
            title = common.standard_song_name(title)
                
            songs.append(f"{title} - {artist}")
            
        return SongList(name=list_name, songs=songs, songs_count=len(songs))
        
    except Exception as e:
        print(f"Parse error: {e}")
        return SongList(name="Error", songs=[], songs_count=0)
