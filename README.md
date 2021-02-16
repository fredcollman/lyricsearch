# Lyric Search

Given the name of an artist, finds the average number of words in their songs.

## Installation

1. Clone the repo: `git clone https://github.com/fredcollman/lyricsearch`
2. (Optional, recommended) set up a virtualenv: `python -m venv ./.venv; . .venv/bin/activate`
3. Install dependencies: `pip install .`, or `pip install -e ".[dev]"` to include development dependencies
4. Run the script: `python -m lyricsearch <ARTIST_NAME>`

## Example usage

```sh
python -m lyricsearch madonna
WITH_PLOT=1 python -m lyricsearch "Fleetwood Mac"
```

## Repo structure
Production code lives in `src/lyricsearch/`.
Unit tests live in `src/lyricsearch/tests/`.
Functional tests live in `functional_tests/`.
Helper scripts live in `scripts/`.
Example data live in `data/`.
Generated plots live in `plots/`.
