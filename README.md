# COVID DDPB

A look at the daily death per inhabitants caused by COVID-19 over time.

Source: [canghailan/Wuhan-2019-nCoV](https://github.com/canghailan/Wuhan-2019-nCoV).

## Rationale

The basic idea is that confirmed cases numbers can't be relied on, due to:

- widly varying amount of tests per country and over time (some countries don't test, then test a lot, then just give up on testing)
- high variance in test protocols, methods and reliability
- cooked numbers

The death numbers are closer to the truth, until localities get completely overwhelmed like in Bergamo, Italy according to the mayor [source](https://www.agi.it/cronaca/news/2020-03-18/coronavirus-quanti-morti-davvero-bergamo-7648225/).

Absolute numbers aren't that useful when comparing countries either so we use daily death per 1 billion people or `ddpb`.

Starting at ~30 ddpb (moving average over 3 days), we can say the epidemic is really underway, call it Day 0. We can then align countries and compare them over time.

## dataset.json

[dataset.json](dataset.json) is a map of `string: list[int]`. One datapoint per country per day, since our Epoch (set to `2020-01-23`).

```json
{
    "Country A": [0, 1, 3, 9],
    "Country B": [0, 0, 0, 2]
}
```

## dataset.csv

[dataset.csv](dataset.csv) is the same as [dataset.json](dataset.json) with headers on top.

```csv
Country, 2020-01-23, 2020-01-24, 2020-01-25, 2020-01-26, ...
Italy,   0,          1,          3,          9
China,   0,          0,          0,          2
```

## Analysis

See [analysis.md](analysis.md) for an up-to-date summary of the state of the pandemic based on the DDPB metric.

## Dev

Requirements

- jq
- flake8

Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip3 install flake8
```

Makefile

- `make` to update the dataset
- `make test` to test build.py
