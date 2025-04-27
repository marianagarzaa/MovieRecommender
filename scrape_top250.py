import requests
import json
import time
from bs4 import BeautifulSoup

# this is to mimic a real browser
HEADERS = {
    'Accept-Language': 'en-US,en;q=0.9',
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/112.0.0.0 Safari/537.36'
    )
}

TOP_URL = 'https://www.imdb.com/chart/top/'

def get_top_250_ids():
    resp = requests.get(TOP_URL, headers=HEADERS)
    # ensures successful response
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    ld = soup.find('script', type='application/ld+json')
    data = json.loads(ld.string)
    items = data.get('itemListElement', [])
    result = []
    for elem in items:
        itm = elem.get('item', {})

        url = itm.get('url') or itm.get('@id')
        if not url:
            continue
        
        imdb_id = url.split('/title/')[1].split('/')[0]
        result.append(imdb_id)
    return result

def get_movie_data(imdb_id):
    url = f'https://www.imdb.com/title/{imdb_id}/'
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    ld = soup.find('script', type='application/ld+json')
    data = json.loads(ld.string)

    # handles edge case
    if data.get('@type') != 'Movie' and isinstance(data, list):
        for block in data:
            if block.get('@type') == 'Movie':
                data = block
                break

    # extract relevant fields
    title   = data.get('name')
    dp      = data.get('datePublished', '')
    year    = int(dp.split('-')[0]) if dp else None
    genres  = data.get('genre') or []
    if isinstance(genres, str):
        genres = [genres]
    agg     = data.get('aggregateRating', {}) or {}
    rating  = float(agg.get('ratingValue')) if agg.get('ratingValue') else None

    return {
        'imdb_id': imdb_id,
        'title':   title,
        'year':    year,
        'rating':  rating,
        'genres':  genres
    }

if __name__ == '__main__':
    ids = get_top_250_ids()
    movies = []
    for i, mid in enumerate(ids, start=1):
        print(f"Fetching {i}/{len(ids)}: {mid}")
        movies.append(get_movie_data(mid))
        time.sleep(0.5)  # be polite to imdb :)
    with open('movies.json','w') as f:
        json.dump(movies, f, indent=2)
    print(f"\nSaved {len(movies)} movies into movies.json")
