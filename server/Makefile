.PHONY: test
test:
	@./scripts/test.sh

.PHONY: coverage
coverage:
	@./scripts/coverage.sh

.PHONY: fmt
fmt:
	@./scripts/format_and_lint.sh

.PHONY: typecheck
typecheck:
	@uv run mypy .

.PHONY: clean
clean:
	@rm -rf .coverage ./htmlcov ./logs