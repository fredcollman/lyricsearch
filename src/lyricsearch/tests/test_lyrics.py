from unittest import TestCase
from unittest.mock import Mock

from lyricsearch.controller import average_words, count_words


class FakeRepository:
    def find_lyrics(self, artist, song):
        return "These are some words"

    def all_songs_by(self, artist):
        return ["This is a song"]


class AverageWordsTest(TestCase):
    def test_counts_the_lyrics(self):
        repository = Mock(wraps=FakeRepository())
        repository.find_lyrics.return_value = (
            "Living in a material world, I am a material girl."
        )
        assert average_words("Madonna", repository=repository) == 10

    def test_fetches_lyrics_for_the_correct_song(self):
        repository = Mock(wraps=FakeRepository())
        repository.all_songs_by.return_value = ["Eleanor Rigby"]
        average_words("The Beatles", repository=repository)
        repository.find_lyrics.assert_called_once_with("The Beatles", "Eleanor Rigby")

    def test_fetches_lyrics_for_multiple_songs(self):
        repository = Mock(wraps=FakeRepository())
        repository.all_songs_by.return_value = [
            "Brown Sugar",
            "Jumpin Jack Flash",
            "Gimme Shelter",
            "Sympathy for the Devil",
        ]
        average_words("The Rolling Stones", repository=repository)
        assert repository.find_lyrics.call_count == 4

    def test_returns_average_number_of_words(self):
        repository = Mock(wraps=FakeRepository())
        repository.all_songs_by.return_value = ["one", "two", "three", "four"]
        repository.find_lyrics.side_effect = [
            "one",
            "two two",
            "three three three",
            "four four four four",
        ]
        assert average_words("Example", repository=repository) == 2.5


class CountWordsTest(TestCase):
    def test_counts_words_for_simple_lyrics(self):
        assert count_words("We can breathe in space") == 5

    def test_contractions_treated_as_single_word(self):
        """TODO: is this desired behaviour? (check)"""
        assert count_words("Don't tread on me") == 4

    def test_instrumental_has_no_words(self):
        assert count_words(None) == 0
