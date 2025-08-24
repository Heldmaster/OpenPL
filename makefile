.PHONY: format run run-web clean

format:
	@python -m pycln src;
	@python -m isort src;
	@python -m black src;

run:
	@python -m src.cmd.main;

run-web:
	cd ./web && pnpm install && pnpm run dev

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	cd ./web && rm -rf ./node_modules
