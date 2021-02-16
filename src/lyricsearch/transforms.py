def count_words(lyrics):
    return len(lyrics.split(" ")) if lyrics else 0


class ArtistNotRecognised(ValueError):
    pass


def extract_artist_id(data):
    try:
        return data["artists"][0]["id"]
    except (KeyError, IndexError):
        raise ArtistNotRecognised()


def extract_lyrics(data):
    return data.get("lyrics") or ""


def extract_titles(data):
    return [work["title"] for work in data.get("works") or []]


def extract_count(data):
    return data["work-count"]
