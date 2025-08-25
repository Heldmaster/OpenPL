.PHONY: format run run-web clean

HOST ?= localhost
PORT ?= 5173

format:
	@python -m black src;

run:
	@python -m src.cmd.main;

run-web:
	cd ./web && pnpm install && pnpm run dev --host $(HOST) --port $(PORT)

run-web-host:
	cd ./web && pnpm install && pnpm run dev --host $(host) --port $(port)

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	cd ./web && rm -rf ./node_modules

help:
	@echo "Использование:"
	@echo "  make run-web"
	@echo "  make run-web-host host=0.0.0.0 port=3000"
	@echo ""
	@echo "Значения по умолчанию: HOST=localhost PORT=5173"
