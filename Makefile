
.PHONY: test
test:
	python -m unittest -f


.PHONY: coverage
coverage:
	coverage run -m unittest
	coverage html

.PHONY: benchmark
benchmark:
	python performance.py

.PHONY: profile
profile:
	python performance.py --profile

.PHONY: clean
clean:
	python -Bc "import pathlib; [p.unlink() for p in pathlib.Path('.').rglob('*.py[co]')]"
	python -Bc "import pathlib; [p.rmdir() for p in pathlib.Path('.').rglob('__pycache__')]"
	rm -f .coverage
	rm -rf htmlcov

