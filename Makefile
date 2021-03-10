
.PHONY: test
test:
	python -m unittest -f


.PHONY: coverage
coverage:
	coverage run -m unittest
	coverage html

.PHONY: benchmark
benchmark:
	python -O performance.py

.PHONY: profile
profile:
	python -O performance.py --profile

.PHONY: build
build: clean
	python setup.py sdist bdist_wheel

.PHONY: clean
clean:
	python -Bc "import pathlib; [p.unlink() for p in pathlib.Path('.').rglob('*.py[co]')]"
	python -Bc "import pathlib; [p.rmdir() for p in pathlib.Path('.').rglob('__pycache__')]"
	rm -f .coverage
	rm -rf .tox
	rm -rf htmlcov
	rm -rf python_liquid.egg-info
	rm -rf build
	rm -rf dist

