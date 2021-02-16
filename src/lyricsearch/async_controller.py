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

USER_AGENT = "lyricsearch/0.0.1 ( https://github.com/fredcollman/lyricsearch )"


def url_escape(fragment):
    return fragment.replace("/", "-")


class AsyncWebRepository:
    def __init__(self, session):
        self._session = session

    async def _get_json(self, url):
        LOGGER.debug(f"request: GET {url}")
        response = await self._session.get(
            url, headers={"accept": "application/json", "user-agent": USER_AGENT}
        )
        LOGGER.debug(f"response: GET {url}, status: {response.status}")
        response.raise_for_status()
        return await response.json()

    async def _artist_id(self, artist):
        url = f"https://musicbrainz.org/ws/2/artist?query={url_escape(artist)}&limit=1"
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
            total = extract_count(data)
            offset += len(titles)
            LOGGER.info(f"Queued {offset} songs by {artist} (total: {total}")
            for title in titles:
                yield title
            done = offset >= extract_count(data)

    async def find_lyrics(self, artist, song):
        url = f"https://api.lyrics.ovh/v1/{url_escape(artist)}/{url_escape(song)}"
        data = await self._get_json(url)
        return extract_lyrics(data)


def post_process(titles, all_lyrics):
    words = [count_words(lyrics) for lyrics in all_lyrics]
    LOGGER.info(f"{len(all_lyrics)} songs with a total of {sum(words)} words")
    least = min(zip(words, titles))
    most = max(zip(words, titles))
    LOGGER.info(f"min: {least}, max: {most}")
    return sum(words) / len(all_lyrics)


async def average_words_coro(artist, repository=None):
    if repository is None:
        async with aiohttp.ClientSession() as session:
            repository = AsyncWebRepository(session)
            return await average_words_coro(artist, repository)

    LOGGER.info(f"Beginning search for {artist}")
    songs = repository.all_songs_by(artist)
    tasks = []
    titles = []
    async for song in songs:
        LOGGER.info(f"Analysing {song}")
        titles.append(song)
        tasks.append(asyncio.create_task(repository.find_lyrics(artist, song)))
    all_lyrics = await asyncio.gather(*tasks)
    return post_process(titles, all_lyrics)


def average_words(artist, repository=None):
    return asyncio.run(average_words_coro(artist, repository))
