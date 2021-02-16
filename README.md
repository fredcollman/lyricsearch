# Lyric Search

Given the name of an artist, finds the average number of words in their songs.

## Installation

Requirements: Python >= 3.7

1. Clone the repo: `git clone https://github.com/fredcollman/lyricsearch`
2. (Optional, recommended) set up a virtualenv: `python -m venv ./.venv; . .venv/bin/activate`
3. Install dependencies: `pip install .`, or `pip install -e ".[dev]"` to include development dependencies
4. Run the script: `python -m lyricsearch <ARTIST_NAME>`

## Example usage

```sh
# basic
python -m lyricsearch madonna
# also creates a plot in the plots/ directory
WITH_PLOT=1 python -m lyricsearch "Fleetwood Mac"
# for extra info about HTTP traffic, especially useful in a concurrent world
LOG_LEVEL=DEBUG python -m lyricsearch "van halen"
```

## Repo structure
Production code lives in `src/lyricsearch/`.
Unit tests live in `src/lyricsearch/tests/`.
Functional tests live in `functional_tests/`.
Helper scripts live in `scripts/`.
Example data live in `data/`.
Generated plots live in `plots/`.

## Design choices
I wanted to demonstrate how I "typically" work, although since this project is smaller than a "typical" codebase, I
made some choices that I would not typically make.

For starters, this would have been much easier in JavaScript, where code runs asynchronously by default.
However, since I'm applying for a Python role, I figured it was best to implement it in Python.

I followed fairly strict "myopic" TDD here, as I tend to prefer avoiding making design decisions up front.
However, given the simple nature of the problem it was clear that an asyncio/aiohttp implementation would be desirable.
In a more real-world scenario, I would have made that choice before coding (which would have directed me towards JS).

I also went a bit over-the-top with unit testing.
On a larger project, I would carve out some time to implement wrappers around requests/aiohttp to help testing, but it
was not worthwhile here.
That being said, the responses library does make requests much easier to test with on small projects.

I began by getting an end-to-end example working, using stubbed responses.
Then I hooked this up fully (via requests), continuing synchronously because nothing from the tests forced me to switch.

Only at this point did I attempt to switch to async.
Typically I favour readability (= maintainability) over performance, where the two are at odds.
However, this switch was to simulate responding to user feedback that performance was "inadequate".
It doesn't matter how readable your code is if poor UX drives users away.

The original synchronous implementation has now been removed, but can be found in the git log.

I haven't bothered with much error handling, as the simplest thing to do is to let exceptions bubble up.
Since the script only really has two possible outcomes ("it worked" or "it didn't"), this seems good enough.
The user gets reasonable feedback that something has gone wrong, and approximately what.

I chucked a bokeh plot in there for a bit of fun at the end, since it's one of my favourite Python libs.
It would also help drive further refinement, e.g. by observing that many songs have 0 words.
Why is this? How could we detect instrumentals vs unrecognised songs? Is there a way to improve recognition? etc

The "CLI" aspect of this is only a thin wrapper around the main code.
It would be simple to wrap this in a Flask app or similar, but I'll "leave that as an exercise for the reader".
