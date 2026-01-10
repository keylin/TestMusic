import re
from urllib.parse import urlparse, parse_qs

# Pre-compile regex
brackets_pattern = r'（|）'
misc_pattern = r'\s?【.*】'
net_easy_v2 = r'163cn'
shard_model = r'https?://[a-zA-Z0-9\.\/\?\:@\-_=#&%]+'
restful_model = r'playlist/(\d+)'

brackets_regex = re.compile(brackets_pattern)
misc_regex = re.compile(misc_pattern)
net_easy_v2_regex = re.compile(net_easy_v2)
shard_model_regex = re.compile(shard_model, re.IGNORECASE)
restful_mode_regex = re.compile(restful_model)

def get_qq_music_param(link):
    try:
        parsed = urlparse(link)
        query = parse_qs(parsed.query)
        return query.get('id', [None])[0]
    except Exception as e:
        print(f"fail to parse url: {e}")
        return None

def get_net_easy_param(link):
    try:
        link = standard_url(link)
        parsed = urlparse(link)
        query = parse_qs(parsed.query)
        return query.get('id', [None])[0]
    except Exception as e:
        print(f"fail to parse url: {e}")
        return None

from . import httputil

def standard_url(link):
    # Extract link from text
    match = shard_model_regex.search(link)
    if match:
        link = match.group(0)
    
    # Short link conversion
    if net_easy_v2_regex.search(link):
        return httputil.get_redirect_location(link)
    
    match = restful_mode_regex.search(link)
    if match:
        link = "https://music.163.com/playlist?id=" + match.group(1)
        
    return link

def standard_song_name(song_name):
    return misc_regex.sub("", replace_cn_brackets(song_name))

def replace_cn_brackets(s):
    def replace(match):
        if match.group(0) == "（":
            return " ("
        return ")"
    return brackets_regex.sub(replace, s)
