import re
from unittest import IsolatedAsyncioTestCase, TestCase
from unittest.mock import Mock

from lyricsearch.async_controller import AsyncWebRepository, average_words


class FakeRepository:
    def __init__(self, lyrics=None, songs=None):
        self._lyrics = lyrics or "These are some words"
        self._songs = songs or ["This is a song"]

    async def find_lyrics(self, artist, song):
        return self._lyrics

    async def all_songs_by(self, artist):
        for song in self._songs:
            yield song


class AverageWordsTest(TestCase):
    def test_counts_the_lyrics(self):
        repository = Mock(
            wraps=FakeRepository(
                lyrics="Living in a material world, I am a material girl."
            )
        )
        assert average_words("Madonna", repository=repository) == 10

    def test_fetches_lyrics_for_the_correct_song(self):
        repository = Mock(wraps=FakeRepository(songs=["Eleanor Rigby"]))
        average_words("The Beatles", repository=repository)
        repository.find_lyrics.assert_called_once_with("The Beatles", "Eleanor Rigby")

    def test_fetches_lyrics_for_multiple_songs(self):
        repository = Mock(
            wraps=FakeRepository(
                songs=[
                    "Brown Sugar",
                    "Jumpin Jack Flash",
                    "Gimme Shelter",
                    "Sympathy for the Devil",
                ]
            )
        )
        average_words("The Rolling Stones", repository=repository)
        assert repository.find_lyrics.call_count == 4

    def test_returns_average_number_of_words(self):
        lyrics = iter(
            [
                "one",
                "two two",
                "three three three",
                "four four four four",
                "five five five five five",
            ]
        )

        class ExtendedFakeRepository:
            async def all_songs_by(self, artist):
                yield "one"
                yield "two"
                yield "three"
                yield "four"

            async def find_lyrics(self, song, artist):
                return next(lyrics)

        repository = Mock(wraps=ExtendedFakeRepository())
        assert average_words("Example", repository=repository) == 2.5


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    async def json(self):
        return self._payload


class FakeSession:
    def __init__(self):
        self.responses = []

    async def get(self, url, headers):
        for match, json in self.responses:
            if isinstance(match, str) and url.startswith(match):
                return FakeResponse(json)
            elif isinstance(match, re.Pattern) and match.match(url):
                return FakeResponse(json)

    def add_response(self, url_pattern, json):
        self.responses.append([url_pattern, json])


def configure_war_pigs_lyrics(session):
    session.add_response(
        re.compile("https://api.lyrics.ovh/v1/.*"),
        json={"lyrics": "Generals gathered in their masses"},
    )


FAKE_ARETHA_ID = "b5e66d98-985b-4258-8903-b8cd2144789a"


def configure_aretha_songs(session):
    session.add_response(
        "https://musicbrainz.org/ws/2/artist?query",
        json={"artists": [{"id": FAKE_ARETHA_ID}]},
    )
    session.add_response(
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


class AsyncWebRepositoryTest(IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = Mock(wraps=FakeSession())
        self.repo = AsyncWebRepository(self.session)

    async def test_can_find_lyrics_for_a_particular_song(self):
        configure_war_pigs_lyrics(self.session)
        lyrics = await self.repo.find_lyrics("Black Sabbath", "War Pigs")
        assert lyrics == "Generals gathered in their masses"

    async def test_finds_lyrics_for_specified_song(self):
        configure_war_pigs_lyrics(self.session)
        await self.repo.find_lyrics("Black Sabbath", "War Pigs")
        self.session.get.assert_called_once_with(
            "https://api.lyrics.ovh/v1/Black Sabbath/War Pigs",
            headers={"accept": "application/json"},
        )

    async def test_can_find_all_songs_by_artist(self):
        configure_aretha_songs(self.session)
        lyrics = [l async for l in self.repo.all_songs_by("Aretha Franklin")]
        assert lyrics == ["A Natural Woman", "Respect", "I Say a Little Prayer"]

    async def test_finding_songs_searches_for_correct_artist(self):
        configure_aretha_songs(self.session)
        [l async for l in self.repo.all_songs_by("Aretha Franklin")]
        call = self.session.get.mock_calls[0]
        assert call.args == (
            "https://musicbrainz.org/ws/2/artist?query=Aretha Franklin&limit=1",
        )
        assert call.kwargs == {
            "headers": {"accept": "application/json"},
        }

    async def test_finding_songs_uses_correct_artist_id(self):
        configure_aretha_songs(self.session)
        [l async for l in self.repo.all_songs_by("Aretha Franklin")]
        call = self.session.get.mock_calls[1]
        assert call.args == (
            "https://musicbrainz.org/ws/2/artist/b5e66d98-985b-4258-8903-b8cd2144789a?inc=works",
        )
        assert call.kwargs == {
            "headers": {"accept": "application/json"},
        }
