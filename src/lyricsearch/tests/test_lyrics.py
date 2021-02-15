import re
from unittest import TestCase
from unittest.mock import Mock

import responses
from lyricsearch.controller import WebRepository, average_words, count_words


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
            "five five five five five",
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


def configure_war_pigs_lyrics():
    responses.add(
        responses.GET,
        re.compile("https://api.lyrics.ovh/v1/.*"),
        json={"lyrics": "Generals gathered in their masses"},
    )


FAKE_ARETHA_ID = "b5e66d98-985b-4258-8903-b8cd2144789a"


def configure_aretha_songs():
    responses.add(
        responses.GET,
        "https://musicbrainz.org/ws/2/artist",
        json={"artists": [{"id": FAKE_ARETHA_ID}]},
    )
    responses.add(
        responses.GET,
        re.compile("https://musicbrainz.org/ws/2/artist/.*"),
        json={
            "works": [
                {
                    "title": "A Natural Woman",
                },
                {
                    "title": "Respect",
                },
                {
                    "title": "I Say a Little Prayer",
                },
            ],
        },
    )


class WebRepositoryTest(TestCase):
    @responses.activate
    def test_can_find_lyrics_for_a_particular_song(self):
        configure_war_pigs_lyrics()
        lyrics = WebRepository().find_lyrics("Black Sabbath", "War Pigs")
        assert lyrics == "Generals gathered in their masses"

    @responses.activate
    def test_finds_lyrics_for_specified_song(self):
        configure_war_pigs_lyrics()
        WebRepository().find_lyrics("Black Sabbath", "War Pigs")
        assert (
            responses.calls[0].request.url
            == "https://api.lyrics.ovh/v1/Black%20Sabbath/War%20Pigs"
        )

    @responses.activate
    def test_lyric_search_includes_appropriate_headers(self):
        configure_war_pigs_lyrics()
        WebRepository().find_lyrics("Black Sabbath", "War Pigs")
        assert responses.calls[0].request.headers["Accept"] == "application/json"

    @responses.activate
    def test_can_find_all_songs_by_artist(self):
        configure_aretha_songs()
        lyrics = WebRepository().all_songs_by("Aretha Franklin")
        assert lyrics == ["A Natural Woman", "Respect", "I Say a Little Prayer"]

    @responses.activate
    def test_finding_song_searches_for_correct_artist(self):
        configure_aretha_songs()
        WebRepository().all_songs_by("Aretha Franklin")
        assert (
            responses.calls[0].request.url
            == "https://musicbrainz.org/ws/2/artist?query=Aretha%20Franklin&limit=1"
        )

    @responses.activate
    def test_finding_song_searches_for_correct_artist(self):
        configure_aretha_songs()
        WebRepository().all_songs_by("Aretha Franklin")
        assert (
            responses.calls[1].request.url
            == "https://musicbrainz.org/ws/2/artist/b5e66d98-985b-4258-8903-b8cd2144789a?inc=works"
        )

    @responses.activate
    def test_finding_song_includes_correct_headers(self):
        configure_aretha_songs()
        WebRepository().all_songs_by("Aretha Franklin")
        assert responses.calls[0].request.headers["Accept"] == "application/json"
        assert responses.calls[1].request.headers["Accept"] == "application/json"
