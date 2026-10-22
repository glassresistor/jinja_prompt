# Contributing to jinja-prompt

Contributions are welcome — bug reports, documentation fixes, new features,
and adapters for additional LLM providers.

## Development setup

1. Clone the repository and create a virtual environment:

   ```bash
   git clone https://github.com/examples/jinja-prompt.git
   cd jinja-prompt
   python -m venv .venv && source .venv/bin/activate
   pip install -e ".[test]"
   ```

2. Run the tests:

   ```bash
   pytest
   ```

   All tests use mocked LLM clients — no API keys or network access required.

3. Format your code with [Black](https://black.readthedocs.io) before
   submitting (CI checks formatting with `black --check`):

   ```bash
   black src tests
   ```

## How the code is organized

- `src/jinja_prompt/__init__.py` — the Jinja extension (`PromptExtension`) and
  everything public. Keep the core dependency-free; provider-specific helpers
  belong in optional submodules guarded by extras (e.g.
  `jinja_prompt/openai.py` behind the `[openai]` extra).
- `tests/` — pytest suite, one test per behaviour described in README.md.

### Working on the tag parser

The `{% prompt %}` tag parses optional `name="value"` attributes using raw
Jinja tokens (see `PromptExtension.parse`). Two facts about Jinja's lexer are
important to know before editing it:

1. After consuming a tag name, the stream is already positioned on the merged
   `%}` token (`block_end`) — there is no separate `%` operator token.
2. `parser.parse_statements(...)` itself calls `expect("block_end")`, so custom
   tags must **not** consume that closing token before calling it; stop one
   token short when gathering attributes.

Also note: Jinja compiles extension method lookups directly, so a single
cannot be used for both sync and async rendering paths. `parse()` selects
`_render_prompt_sync` or `_render_prompt_async` based on
`environment.is_async`. Keep that behaviour if you refactor.

## Contribution workflow

- Open an issue first for large changes.
- Create a branch off `main`, make focused commits, and add/adjust tests as
  appropriate (`pytest`).
- Continuous integration (GitHub Actions, `.github/workflows/ci.yml`) runs
  `black --check` plus the pytest suite on Python 3.8–3.13 for every pull
  request; keep both green.
- Submit a pull request against `main`; include a description of what changed
  and why.

## Release checklist (maintainers)

1. Update `__version__` in `src/jinja_prompt/__init__.py`.
2. Ensure tests pass: `pytest`.
3. Build artifacts: `pip install build && python -m build`.
4. Check metadata: `twine check dist/*`.
5. Upload to PyPI with [Twine](https://twine.pypa.io): `twine upload dist/*`
   (or via a CI workflow using API tokens — never account passwords).

## Code of conduct

Be kind, assume good intent, and keep discussions on-topic.
