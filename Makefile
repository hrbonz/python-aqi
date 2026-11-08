# hatch versioning
SEGMENT ?= patch
REMOTE ?= origin

.ONESHELL:
.SHELLFLAGS = -ec
.NOTPARALLEL:

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

# Release: `make release SEGMENT=major|minor|patch`
#
# bump:    version, lock, changelog date, commit and tag (nothing is pushed)
# publish: build the tagged commit and upload it to PyPI, with the token in
#          UV_PUBLISH_TOKEN
# push:    commit and tag to the remote, once the upload worked
#
# The upload comes before the push so that a failed upload leaves nothing
# public: reset the commit and the tag, or fix and run `make publish push`.

.PHONY: bump
bump: test
	test -z "$$(git status --porcelain)" || { echo "the working tree is not clean" >&2; exit 1; }
	test "$$(git branch --show-current)" = master || { echo "not on master" >&2; exit 1; }
	uv run hatch version $(SEGMENT)
	uv lock
	ver=$$(uv run hatch version)
	if ! grep -qx "$$ver (unreleased)" docs/changelog.rst; then
		echo "docs/changelog.rst has no \"$$ver (unreleased)\" section" >&2
		git checkout aqi/__init__.py uv.lock
		exit 1
	fi
	sed -i "s/^$$ver (unreleased)$$/$$ver ($$(date +%F))/" docs/changelog.rst
	git add aqi/__init__.py uv.lock docs/changelog.rst
	git commit -m "release: bump to $$ver"
	git tag "$$ver"

# what publish needs: a token, and a clean tree on the tagged version
.PHONY: check-publish
check-publish:
	test -n "$$UV_PUBLISH_TOKEN" || { echo "UV_PUBLISH_TOKEN is not set (PyPI API token)" >&2; exit 1; }
	ver=$$(uv run hatch version)
	test -z "$$(git status --porcelain)" || { echo "the working tree is not clean" >&2; exit 1; }
	test "$$(git describe --exact-match --tags HEAD 2>/dev/null)" = "$$ver" || { echo "HEAD is not tagged $$ver" >&2; exit 1; }

.PHONY: publish
publish: check-publish build
	ver=$$(uv run hatch version)
	uv publish --check-url https://pypi.org/simple/ dist/*"$$ver"*

.PHONY: push
push:
	ver=$$(uv run hatch version)
	git push $(REMOTE) HEAD
	git push $(REMOTE) "$$ver"

.PHONY: release
release: bump publish push
