import datetime as dt
import json
import sys
import typing as t


def jd(data: t.Any):
    """
    Pretty-print JSON with indentation.
    """
    print(json.dumps(data, indent=2, cls=JSONEncoderPlus), file=sys.stdout)  # noqa: T201


def str_contains(haystack, *needles):
    """
    Whether haystack contains any of the provided needles.
    """
    haystack = str(haystack)
    return any(needle in haystack for needle in needles)


class JSONEncoderPlus(json.JSONEncoder):
    """
    https://stackoverflow.com/a/27058505
    """

    def default(self, o):
        if isinstance(o, dt.datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)
