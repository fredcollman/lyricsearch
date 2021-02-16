import aiohttp

from .transforms import count_words, extract_artist_id, extract_lyrics, extract_titles


class AsyncWebRepository:
    def __init__(self, session):
        self._session = session

    async def _get_json(self, url):
        response = await self._session.get(url, headers={"accept": "application/json"})
        return await response.json()

    async def _artist_id(self, artist):
        url = f"https://musicbrainz.org/ws/2/artist?query={artist}&limit=1"
        data = await self._get_json(url)
        return extract_artist_id(data)

    async def all_songs_by(self, artist):
        artist_id = await self._artist_id(artist)
        url = f"https://musicbrainz.org/ws/2/artist/{artist_id}?inc=works"
        data = await self._get_json(url)
        return extract_titles(data)

    async def find_lyrics(self, artist, song):
        url = f"https://api.lyrics.ovh/v1/{artist}/{song}"
        data = await self._get_json(url)
        return extract_lyrics(data)
