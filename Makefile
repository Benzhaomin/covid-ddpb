.PHONY: test download dataset update clean

all: download dataset check analyze

download:
	wget -q -N https://raw.githubusercontent.com/canghailan/Wuhan-2019-nCoV/master/Wuhan-2019-nCoV.json -O ncov.json
	wget -q -N https://raw.githubusercontent.com/samayo/country-json/master/src/country-by-abbreviation.json -O country-code.json
	wget -q -N https://raw.githubusercontent.com/samayo/country-json/master/src/country-by-population.json -O country-population.json

dataset:
	@python3 build.py

check:
	@test $(shell jq 'length' dataset.json) -ge 1

analyze:
	@python3 analyze.py

test:
	@python3 -m doctest *.py
	@flake8 --max-line-length=120 *.py

clean:
	rm -rf venv
	find . -type d -name '__pycache__' -exec rm -rf {} \;
	rm -f ncov.json country-code.json country-population.json || true
