from .logging import get_logger


def average_words(artist):
    logger = get_logger(__name__)
    logger.info(f"Beginning search for {artist}")
    # GET https://musicbrainz.org/ws/2/artist?query=Daft%20Punk&limit=1
    # -> id="056e4f3e-d505-4dad-8ec1-d04f521cbb56"
    # GET https://musicbrainz.org/ws/2/artist/056e4f3e-d505-4dad-8ec1-d04f521cbb56?inc=works
    # -> ["Aerodynamic", "Around the World", ...]
    # GET https://api.lyrics.ovh/v1/Daft Punk/Around the World
    # -> "Around the world, around the world, ..."
    return 3
