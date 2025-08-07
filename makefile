.PHONY: format run clean

format:
	@python -m black src;

run:
	@python -m src.cmd.main;

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
