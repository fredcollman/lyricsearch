import asyncio

import aiohttp

from .logging import get_logger
from .transforms import (
    count_words,
    extract_artist_id,
    extract_count,
    extract_lyrics,
    extract_titles,
)

LOGGER = get_logger(__name__)


class AsyncWebRepository:
    def __init__(self, session):
        self._session = session

    async def _get_json(self, url):
        LOGGER.debug(f"request: GET {url}")
        response = await self._session.get(url, headers={"accept": "application/json"})
        LOGGER.debug(f"response: GET {url}, status: {response.status}")
        return await response.json()

    async def _artist_id(self, artist):
        url = f"https://musicbrainz.org/ws/2/artist?query={artist}&limit=1"
        data = await self._get_json(url)
        return extract_artist_id(data)

    async def all_songs_by(self, artist):
        artist_id = await self._artist_id(artist)
        done = False
        offset = 0
        while not done:
            url = (
                f"https://musicbrainz.org/ws/2/work?artist={artist_id}&offset={offset}"
            )
            data = await self._get_json(url)
            titles = extract_titles(data)
            LOGGER.info(f"Found {len(titles)} songs by {artist}")
            for title in titles:
                yield title
            offset += len(titles)
            done = offset >= extract_count(data)

    async def find_lyrics(self, artist, song):
        url = f"https://api.lyrics.ovh/v1/{artist}/{song}"
        data = await self._get_json(url)
        return extract_lyrics(data)


def post_process(all_lyrics):
    words = sum(count_words(lyrics) for lyrics in all_lyrics)
    return words / len(all_lyrics)


async def average_words_coro(artist, repository=None):
    if repository is None:
        async with aiohttp.ClientSession() as session:
            repository = AsyncWebRepository(session)
            return await average_words_coro(artist, repository)

    LOGGER.info(f"Beginning search for {artist}")
    songs = repository.all_songs_by(artist)
    tasks = []
    async for song in songs:
        LOGGER.info(f"Analysing {song}")
        tasks.append(asyncio.create_task(repository.find_lyrics(artist, song)))
    all_lyrics = await asyncio.gather(*tasks)
    return post_process(all_lyrics)


def average_words(artist, repository=None):
    return asyncio.run(average_words_coro(artist, repository))
