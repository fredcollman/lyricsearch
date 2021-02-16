from unittest import TestCase

from lyricsearch import async_controller


class AsyncAverageWordsTest(TestCase):
    def test_gets_words_for_an_artist(self):
        artist = "Daft Punk"
        result = async_controller.average_words(artist=artist)
        assert float(result) > 0

    def test_rapper_has_more_words_than_punk(self):
        rap_words = async_controller.average_words("Jay-Z")
        punk_words = async_controller.average_words("Sex Pistols")
        assert float(rap_words) > float(punk_words)

    def test_fails_gracefully_for_unrecognised_artist(self):
        nonsense = "dikfhuadghuisadfiusdfikgskdiygvfdy"
        with self.assertRaises(ValueError):
            async_controller.average_words(nonsense)
