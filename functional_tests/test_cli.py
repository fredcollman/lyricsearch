from unittest import TestCase
from lyricsearch.controller import average_words


class AverageWordsTest(TestCase):
    def test_gets_words_for_an_artist(self):
        artist = "Daft Punk"
        result = average_words(artist=artist)
        assert float(result) > 0
