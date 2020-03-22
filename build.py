#!/usr/bin/env python3

#
# Build the DDPB dataset from remote sources
#
# Usage:
#   $ python3 build.py
#
# Requirements (get them with `make download`):
#   - country-code.json
#   - country-population.json
#   - ncov.json
#

import datetime
import json
import csv
from typing import List

EPOCH = datetime.date(2020, 1, 23)
DAYS = (datetime.date.today() - EPOCH).days + 1


def totald(ncov: List[dict], country: str) -> List[int]:
    """ Builds the list of daily total death datapoints for a country

    >>> td = totald([], 'IT')
    >>> sum(td)
    0
    >>> len(td) == DAYS
    True
    >>> td = totald([{'dead': 1, 'countryCode': 'UK', 'date': '2020-01-23'}, {'dead': 0, 'date': '2020-01-23'}, {'dead': 12, 'countryCode': 'CN', 'date': '2020-01-23'}, {'dead': 2, 'countryCode': 'UK', 'date': '2020-01-25'}], 'UK')
    >>> td[0:3]
    [1, 0, 2]
    """  # noqa
    series = [0]*DAYS

    for d in ncov:
        if d.get('countryCode') and d['countryCode'] == country:
            date = datetime.datetime.strptime(d["date"], '%Y-%m-%d').date()
            delta = (date - EPOCH).days
            # exclude out of range data
            if delta < 0 or delta >= DAYS:
                continue
            series[delta] = d['dead']

    return series


def deltad(history: List[int]) -> List[int]:
    """ Computes a delta between daily datapoints

    >>> deltad([1,2,3,5])
    [1, 1, 1, 2]
    >>> deltad([])
    []
    """
    if not history:
        return []
    return [history[0]] + [max(0, history[n] - history[n-1]) for n in range(1, len(history))]


def ddpb(daily: int, pop: int) -> int:
    """ Computes the daily death rate per billion people

    >>> ddpb(32, 1000000000)
    32
    >>> ddpb(1, 60009)
    16664
    """
    return int(daily / pop * 10**9)


def trimzero(data: List[int]) -> List[int]:
    """ Removes zeroes at the hedge of a list, in-place

    >>> trimzero([])
    []
    >>> trimzero([1, 0, 3])
    [1, 0, 3]
    >>> trimzero([0, 0, 1, 0, 3, 0, 0])
    [1, 0, 3]
    """
    # trim left
    while data and data[0] == 0:
        data.pop(0)

    # trim right
    while data and data[-1] == 0:
        data.pop(len(data)-1)

    return data


if __name__ == "__main__":
    with open('country-code.json') as c:
        code = {d['country']: d['abbreviation'] for d in json.load(c)}

    with open('country-population.json') as p:
        population = {d['country']: int(d['population']) for d in json.load(p) if d['population']}

    with open('ncov.json') as n:
        ncov = json.load(n)
        ncov = [r for r in ncov if not r.get('provinceCode')]

    ds = {}
    for country, pop in population.items():
        # exclude countries with no matching code
        if country not in code:
            continue

        td = totald(ncov, code[country])
        dd = deltad(td)

        # exclude countries without "enough" daily deaths
        sg = trimzero(list(dd))
        if not sg or len(sg) < 10 or (sum(sg) / len(sg)) < 2:
            continue

        # compute series of daily death per billion
        ds[country] = [ddpb(d, pop) for d in dd]

    # output
    with open('dataset.json', 'w') as f:
        json.dump(ds, f)

    with open('dataset.csv', 'w', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)

        # headers
        headers = ['Country']
        for d in range(DAYS):
            headers.append((EPOCH + datetime.timedelta(days=d)).isoformat())
        writer.writerow(headers)

        # one row per country
        for c, d in ds.items():
            writer.writerow([c] + d)
