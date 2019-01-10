# vim: set noexpandtab:
pypi: pydist pypipush

pydist: pyclean test
	python setup.py sdist bdist_wheel

pypipush: dist
	twine upload dist/*

pyclean:
	python setup.py clean
	rm -rf *egg-info build dist

test: tox

unittest:
	python -m unittest discover

tox:
	tox


.PHONY: pypi pydist pypipush pyclean test unittest tox
