import json

import requests

from .log import get_logger
from .transforms import count_words, extract_artist_id, extract_lyrics, extract_titles


class WebRepository:
    def _artist_id(self, artist):
        url = f"https://musicbrainz.org/ws/2/artist?query={artist}&limit=1"
        response = requests.get(url, headers={"accept": "application/json"})
        return extract_artist_id(response.json())

    def all_songs_by(self, artist):
        artist_id = self._artist_id(artist)
        url = f"https://musicbrainz.org/ws/2/artist/{artist_id}?inc=works"
        response = requests.get(url, headers={"accept": "application/json"})
        return extract_titles(response.json())

    def find_lyrics(self, artist, song):
        url = f"https://api.lyrics.ovh/v1/{artist}/{song}"
        response = requests.get(url, headers={"accept": "application/json"})
        return extract_lyrics(response.json())


def default_repository():
    return WebRepository()


def average_words(artist, repository=None):
    logger = get_logger(__name__)
    logger.info(f"Beginning search for {artist}")
    words = 0
    if repository is None:
        repository = default_repository()
    songs = repository.all_songs_by(artist)
    logger.info(f"Found {len(songs)} songs by {artist}")
    for song in songs:
        logger.info(f"Analysing {song}")
        lyrics = repository.find_lyrics(artist, song)
        words += count_words(lyrics)
    return words / len(songs)
