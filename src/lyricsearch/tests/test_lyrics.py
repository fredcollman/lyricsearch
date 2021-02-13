from unittest import TestCase
from lyricsearch.controller import count_words


class CountWordsTest(TestCase):
    def test_counts_words_for_simple_lyrics(self):
        assert count_words("We can breathe in space") == 5

    def test_contractions_treated_as_single_word(self):
        """TODO: is this desired behaviour? (check)"""
        assert count_words("Don't tread on me") == 4
