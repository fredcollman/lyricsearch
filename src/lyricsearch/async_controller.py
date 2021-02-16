import asyncio
import os

import aiohttp

from .log import get_logger
from .plot import plot
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
            LOGGER.info(f"Queued {offset} songs by {artist} (total: {total})")
            for title in titles:
                yield title
            done = offset >= extract_count(data)

    async def find_lyrics(self, artist, song):
        url = f"https://api.lyrics.ovh/v1/{url_escape(artist)}/{url_escape(song)}"
        data = await self._get_json(url)
        return extract_lyrics(data)


class EmptySequenceHasNoAverage(RuntimeError):
    pass


def calculate_average(titles, word_counts):
    if not titles:
        raise EmptySequenceHasNoAverage(
            "cannot calculate the average when there are no songs"
        )
    LOGGER.info(f"Total of {sum(word_counts)} words across {len(word_counts)} songs")
    least = min(zip(word_counts, titles))
    most = max(zip(word_counts, titles))
    LOGGER.info(f"min: {least}, max: {most}")
    return sum(word_counts) / len(word_counts)


def post_process(artist, titles, all_lyrics):
    word_counts = [count_words(lyrics) for lyrics in all_lyrics]
    average = calculate_average(titles, word_counts)
    if os.environ.get("WITH_PLOT"):
        path = plot(
            artist=artist,
            titles=titles,
            word_counts=word_counts,
        )
        LOGGER.info("chart plotted at %s", path)
    return average


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
    return post_process(artist, titles, all_lyrics)


def average_words(artist, repository=None):
    return asyncio.run(average_words_coro(artist, repository))
