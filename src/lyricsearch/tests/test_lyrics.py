import re
from unittest import TestCase
from unittest.mock import Mock

import responses
from lyricsearch.controller import (
    WebRepository,
    average_words,
    count_words,
    extract_artist_id,
    extract_lyrics,
    extract_titles,
)


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


class ExtractionTest(TestCase):
    def test_extracts_artist_id_from_first_item(self):
        payload = {
            "created": "2021-02-15T20:40:41.326Z",
            "count": 47,
            "offset": 0,
            "artists": [
                {
                    "id": "5b11f4ce-a62d-471e-81fc-a69a8278c7da",
                    "type": "Group",
                    "score": 100,
                    "name": "Nirvana",
                    "country": "US",
                    "disambiguation": "90s US grunge band",
                },
                {
                    "id": "9282c8b4-ca0b-4c6b-b7e3-4f7762dfc4d6",
                    "type": "Group",
                    "score": 86,
                    "name": "Nirvana",
                    "country": "GB",
                    "disambiguation": "60s band from the UK",
                },
            ],
        }
        assert extract_artist_id(payload) == "5b11f4ce-a62d-471e-81fc-a69a8278c7da"

    def test_fails_to_extract_artist_id_when_no_matches(self):
        payload = {
            "created": "2021-02-15T20:40:41.326Z",
            "count": 0,
            "offset": 0,
            "artists": [],
        }
        with self.assertRaises(ValueError):
            extract_artist_id(payload)

    def test_extracts_lyrics_if_found(self):
        payload = {"lyrics": "Goodbye Norma Jean"}
        assert extract_lyrics(payload) == "Goodbye Norma Jean"

    def test_handles_case_where_song_has_no_lyrics(self):
        """TODO: how to handle https://api.lyrics.ovh/v1/Van%20Halen/Eruption ?"""
        payload = {"lyrics": None}
        assert extract_lyrics(payload) == ""

    def test_extracts_titles_from_all_songs(self):
        payload = {
            "type": "Group",
            "name": "Nirvana",
            "country": "US",
            "disambiguation": "90s US grunge band",
            "works": [
                {
                    "title": "(Don\u2019t Fear) The Reaper",
                    "id": "89c7ce29-9ffb-368c-8821-d5ad85b967bd",
                },
                {
                    "id": "b8aeb29b-6c42-38da-a179-12e1fdb97ad3",
                    "title": "(I Can\u2019t Get No) Satisfaction",
                },
                {
                    "id": "ee3e2a70-2efa-3b84-9aa4-7160e484abd8",
                    "title": "(New Wave) Polly",
                },
                {
                    "id": "7b77ce3b-1c90-3764-87c8-ca4006081028",
                    "title": "867-5309/Jenny",
                },
                {"id": "f4e29ec5-4806-3c2b-bc84-c802552e8f35", "title": "About a Girl"},
                {
                    "title": "Aero Zeppelin",
                    "id": "212c2e07-14b8-326a-bbbb-b9ea5a203be7",
                },
                {
                    "title": "Ain\u2019t It a Shame",
                    "id": "427548a0-ced0-4ee9-807b-ff7561dc0c93",
                },
                {"id": "d20a2bd8-366f-4087-8980-17d97d6660d3", "title": "Alien Boy"},
                {
                    "id": "0bb9704c-aa0d-30b6-b6a4-d6c08613057b",
                    "title": "All Apologies",
                },
            ],
        }
        assert extract_titles(payload) == [
            "(Don\u2019t Fear) The Reaper",
            "(I Can\u2019t Get No) Satisfaction",
            "(New Wave) Polly",
            "867-5309/Jenny",
            "About a Girl",
            "Aero Zeppelin",
            "Ain\u2019t It a Shame",
            "Alien Boy",
            "All Apologies",
        ]

    def test_handles_missing_data(self):
        payload = {
            "type": "Group",
            "name": "nope",
            "works": None,
        }
        assert extract_titles(payload) == []
