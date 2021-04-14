#!/usr/bin/env python3

#
# Generate leaderboards from the DDPB dataset
#
# Usage:
#   $ python3 analyze.py
#
# Requirements:
#   - dataset.json
#

import datetime
import json
import operator
from typing import List, Tuple
from build import DAYS, EPOCH


MIN_DDPB = 30
MOV_AVG = 5


def moving_average(series: List[int], window: int) -> List[int]:
    """ Averages a series over a moving *window* of elements

    >>> moving_average([1, 4, 12, 24, 128], 3)
    [1, 2, 5, 13, 54]
    """
    result = [0 for x in series]
    acc = 0

    for i in range(0, window):
        acc += series[i]
        result[i] = int(acc / (i+1))

    for i in range(window, len(series)):
        acc = acc - series[i-window] + series[i]
        result[i] = int(acc / window)

    return result


def find_peak(series: List[int]) -> Tuple[int, int]:
    """ Returns the max value and its index

    >>> find_peak([1, 2, 5, 2, 8, 2])
    (4, 8)
    >>> find_peak([])
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    ValueError: max() arg is an empty sequence
    """
    return max(enumerate(series), key=operator.itemgetter(1))


def find_start(series: List[int], ) -> int:
    """ Returns the first index where DDPB is high enough to consider the epidemic alive

    >>> find_start([0, 15, 134, 390, 102, 12])
    2
    >>> find_start([0, 1, 1, 0])
    -1
    >>> find_start([100, 300])
    0
    """
    index = -1
    i = 0
    while i < len(series):
        if series[i] >= MIN_DDPB:
            index = i
            break
        i += 1
    return index


def find_boundaries(series: List[int]) -> Tuple[int, int]:
    """ Returns the first and last index where DDPB is high enough to consider the epidemic alive

    >>> find_boundaries([0, 15, 134, 390, 102, 12])
    (2, 4)
    >>> find_boundaries([0, 1, 1, 0])
    (-1, -1)
    >>> find_boundaries([139, 300])
    (0, 1)
    >>> find_boundaries([139])
    (0, 0)
    """
    start = find_start(series)
    end = find_start(list(reversed(series)))
    if end >= 0:
        end = len(series) - 1 - end
    return start, end


def date_from_epoch(day: int) -> datetime.date:
    return EPOCH + datetime.timedelta(days=day)


markdown = '''
# Analysis

Generated from data up to {lastdate} (included), on {timestamp}.

{ong} countries have a hard-hitting epidemic ongoing out of {cnt} with enough data.

We consider a `DDPB`, or Daily Death Per Billion, over {minddpb} to mean the epidemic is ongoing.
mAverage is moving over the last {movavg} days.

{table}
'''

table = '''
| Rank | Country | DDPB | mAverage | Total | Status |
|------|---------|-----:|---------:|------:|--------|
'''

if __name__ == "__main__":
    with open('dataset.json') as f:
        dataset = json.load(f)

    # add world stats
    dataset['World'] = [sum([d[n] for d in dataset.values()]) for n in range(DAYS)]
    dataset['World'] = list(map(lambda x: int(x/len(dataset)-1), dataset['World']))

    summary = []
    for c, d in dataset.items():
        tdpb = sum(d)
        peakday, _ = find_peak(d)
        peakvalue = d[peakday]
        mavg = moving_average(d, MOV_AVG)
        start, end = find_boundaries(d)
        duration = end - start

        if start > -1 and end < len(d) - 1:
            status = 'finished'
        elif start > -1:
            status = 'ongoing'
        else:
            status = 'not started'

        r = {
            'country': c,
            'ddpb': d[-1],
            'mavg': mavg[-1],
            'tdpb': tdpb,
            'tavg': int(tdpb / duration) if duration else 0,
            'peakvalue': peakvalue,
            'peakdate': date_from_epoch(peakday),
            'start': date_from_epoch(start) if start else None,
            'end': date_from_epoch(end) if end != len(d) - 1 else None,
            'duration': duration,
            'status': status,
        }
        summary.append(r)

    summary.sort(key=lambda d: d['ddpb'], reverse=True)

    for i, s in enumerate(summary):
        peak = '**' if s["ddpb"] == s["peakvalue"] else ''
        table += f'| {i+1} | {s["country"]} | {peak}{s["ddpb"]:,}{peak} | {s["mavg"]:,} |' \
                 f' {s["tdpb"]:,} |' \
                 f' {s["status"]} |\n'

    markdown = markdown.format(
        timestamp=datetime.datetime.utcnow().isoformat(),
        lastdate=date_from_epoch(DAYS-1).isoformat(),
        minddpb=MIN_DDPB,
        movavg=MOV_AVG,
        table=table,
        cnt=len(summary) - 1,
        ong=len([s for s in summary if s["status"] == "ongoing"]) - 1
    )

    with open('analysis.md', 'w') as f:
        f.write(markdown)
