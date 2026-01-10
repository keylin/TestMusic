import requests

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded"
}

def post(url, data=None, headers=None):
    final_headers = DEFAULT_HEADERS.copy()
    if headers:
        final_headers.update(headers)
    return requests.post(url, data=data, headers=final_headers)

def get(url, params=None, headers=None):
    final_headers = DEFAULT_HEADERS.copy()
    if headers:
        final_headers.update(headers)
    return requests.get(url, params=params, headers=final_headers)

def get_redirect_location(url):
    try:
        response = requests.head(url, allow_redirects=True)
        return response.url
    except requests.RequestException:
        # Fallback to GET if HEAD fails
        try:
            response = requests.get(url, allow_redirects=True)
            return response.url
        except Exception as e:
            print(f"Failed to get redirect location: {e}")
            return url
