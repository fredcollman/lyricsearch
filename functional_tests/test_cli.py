from unittest import TestCase
from lyricsearch.controller import average_words


class AverageWordsTest(TestCase):
    def test_gets_words_for_an_artist(self):
        artist = "Daft Punk"
        result = average_words(artist=artist)
        assert float(result) > 0

    def test_rapper_has_more_words_than_punk(self):
        rap_words = average_words("Jay Z")
        punk_words = average_words("Sex Pistols")
        self.skipTest("TODO")
        assert float(rap_words) > float(punk_words)
