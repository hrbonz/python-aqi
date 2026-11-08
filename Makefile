.PHONY: test
test:
	uv run python -m unittest discover

.PHONY: build
build: clean
	uv build

.PHONY: clean
clean:
	rm -rf build dist *.egg-info

.PHONY: docs
docs:
	make -C docs/ -f Makefile html SPHINXBUILD='uv run sphinx-build'
