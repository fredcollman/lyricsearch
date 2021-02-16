import argparse

from .async_controller import average_words


def parse_args():
    parser = argparse.ArgumentParser(
        description="Find the average number of words in the songs of a specified artist."
    )
    parser.add_argument(
        "artist",
        type=str,
        help="Artist to search for, quoted if multiple words, e.g. 'Johnny Cash'",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    print(average_words(artist=args.artist))


if __name__ == "__main__":
    main()
