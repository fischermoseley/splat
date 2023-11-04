.PHONY: test format clean
test:
	pytest

format:
	black .

clean:
	git clean -Xdf