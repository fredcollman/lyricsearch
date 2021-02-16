from unittest import TestCase

from lyricsearch.transforms import (
    count_words,
    extract_artist_id,
    extract_count,
    extract_lyrics,
    extract_titles,
)


class CountWordsTest(TestCase):
    def test_counts_words_for_simple_lyrics(self):
        assert count_words("We can breathe in space") == 5

    def test_contractions_treated_as_single_word(self):
        """TODO: is this desired behaviour? (check)"""
        assert count_words("Don't tread on me") == 4

    def test_instrumental_has_no_words(self):
        assert count_words(None) == 0


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

    def test_extracts_count_from_payload(self):
        payload = {"work-count": 101, "work-offset": 25, "works": [{"title": "etc"}]}
        assert extract_count(payload) == 101
