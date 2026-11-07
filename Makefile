.PHONY: test build clean

test:
	uv run python -m unittest discover

build: clean
	uv build

clean:
	rm -rf build dist *.egg-info
