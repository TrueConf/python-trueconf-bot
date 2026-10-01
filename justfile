# justfile for python-trueconf-bot
# Environments:
#   .venv       - production-like install (runtime deps only)
#   .venv-tests - test environment (pytest + anyio + trio)
#   .venv-docs  - mkdocs documentation environment

# Python version for environments (override: just setup python=3.11)
python := env_var_or_default("PYTHON", "3.12")

# ── Environment setup ────────────────────────────────────────────────

# Create all environments
setup: setup-prod setup-test setup-docs

# .venv: install the library as in production (no groups at all)
setup-prod:
    UV_PROJECT_ENVIRONMENT=.venv uv sync --no-default-groups --python {{python}}
    .venv/bin/python -c "import trueconf; print('prod env OK:', trueconf.__file__)"

# .venv-tests: test environment (project + test group only)
setup-test:
    UV_PROJECT_ENVIRONMENT=.venv-tests uv sync --group test --no-default-groups --python {{python}}
    .venv-tests/bin/python -c "import trueconf; print('test env OK:', trueconf.__file__)"

# .venv-docs: mkdocs environment (project + docs group only)
setup-docs:
    UV_PROJECT_ENVIRONMENT=.venv-docs uv sync --group docs --no-default-groups --python {{python}}
    .venv-docs/bin/python -c "import mkdocs; print('docs env OK:', mkdocs.__version__)"

# ── Update ───────────────────────────────────────────────────────────

# Update dependencies in all environments (re-resolve + reinstall, keep envs)
refresh: refresh-prod refresh-test refresh-docs

refresh-prod:
    UV_PROJECT_ENVIRONMENT=.venv uv sync --no-default-groups --python {{python}} --refresh --reinstall

refresh-test:
    UV_PROJECT_ENVIRONMENT=.venv-tests uv sync --group test --no-default-groups --python {{python}} --refresh --reinstall

refresh-docs:
    UV_PROJECT_ENVIRONMENT=.venv-docs uv sync --group docs --no-default-groups --python {{python}} --refresh --reinstall

# ── Clean rebuild with cache purge ───────────────────────────────────

# Remove all environments
clean-envs:
    rm -rf .venv .venv-tests .venv-docs

# Purge the uv cache entirely
clean-cache:
    uv cache clean --force

# Rebuild everything from scratch: cache + environments + install
clean: clean-envs clean-cache setup

# ── Utilities ────────────────────────────────────────────────────────

# Run the test suite
test:
    .venv-tests/bin/python -m pytest tests/ -q

# Build documentation
docs:
    DYLD_FALLBACK_LIBRARY_PATH="$(brew --prefix)/lib" .venv-docs/bin/mkdocs build

# Local documentation server
serve:
    DYLD_FALLBACK_LIBRARY_PATH="$(brew --prefix)/lib" .venv-docs/bin/mkdocs serve

# Lint (ruff via uvx - does not touch environments)
check:
    uvx ruff check .

# Update uv.lock
lock:
    uv lock --refresh