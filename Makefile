.PHONY: test
test:
	pytest

.PHONY: format
format:
	black .
