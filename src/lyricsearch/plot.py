import datetime
from pathlib import Path

from bokeh.plotting import ColumnDataSource, figure, output_file, save


def to_url(filename):
    return Path(filename).absolute().as_uri()


def plot(*, artist, titles, word_counts):
    filename = f"plots/{artist}-{datetime.datetime.now()}.html".replace(
        " ", "-"
    ).replace(":", "")
    output_file(filename)
    title = f"Words in {artist} songs"
    tooltips = [("title", "@label"), ("words", "@y")]
    p = figure(
        title=title,
        x_axis_label="song",
        y_axis_label="word count",
        tooltips=tooltips,
    )

    sorted_pairs = list(sorted(zip(word_counts, titles)))
    index = range(1, len(sorted_pairs) + 1)
    value, label = zip(*sorted_pairs)

    cds = ColumnDataSource(data={"x": index, "y": value, "label": label})
    p.x("x", "y", source=cds, size=10, alpha=0.5)
    save(p, filename=filename, title=title)
    return to_url(filename)
