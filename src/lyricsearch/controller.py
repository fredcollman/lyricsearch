import json

import requests

from .logging import get_logger


def count_words(lyrics):
    return len(lyrics.split(" ")) if lyrics else 0


def extract_artist_id(data):
    return data["artists"][0]["id"]


def extract_lyrics(data):
    return data["lyrics"]


def extract_titles(data):
    return [work["title"] for work in data["works"]]


class CachedFileRepository:
    def all_songs_by(self, artist):
        with open("data/songs-daft_punk.json") as f:
            data = json.load(f)
            return extract_titles(data)

    def find_lyrics(self, artist, song):
        with open("data/lyrics-around_the_world.json") as f:
            data = json.load(f)
            return extract_lyrics(data)


class WebRepository:
    def _artist_id(self, artist):
        url = f"https://musicbrainz.org/ws/2/artist?query={artist}&limit=1"
        response = requests.get(url)
        return extract_artist_id(response.json())

    def all_songs_by(self, artist):
        artist_id = self._artist_id(artist)
        url = f"https://musicbrainz.org/ws/2/artist/{artist_id}?inc=works"
        response = requests.get(url)
        return extract_titles(response.json())

    def find_lyrics(self, artist, song):
        url = f"https://api.lyrics.ovh/v1/{artist}/{song}"
        response = requests.get(url)
        return extract_lyrics(response.json())


def default_repository():
    return WebRepository()


def average_words(artist, repository=None):
    logger = get_logger(__name__)
    logger.info(f"Beginning search for {artist}")
    words = 0
    songs = 0
    if repository is None:
        repository = default_repository()
    # GET https://musicbrainz.org/ws/2/artist?query=Daft%20Punk&limit=1
    # -> id="056e4f3e-d505-4dad-8ec1-d04f521cbb56"
    # GET https://musicbrainz.org/ws/2/artist/056e4f3e-d505-4dad-8ec1-d04f521cbb56?inc=works
    # -> ["Aerodynamic", "Around the World", ...]
    for song in repository.all_songs_by(artist):
        # GET https://api.lyrics.ovh/v1/Daft Punk/Around the World
        # -> "Around the world, around the world, ..."
        lyrics = repository.find_lyrics(artist, song)
        words += count_words(lyrics)
        songs += 1
    return words / songs
