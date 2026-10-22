# Issues found while preparing this repo for GitHub deployment

This was produced during the deploy-readiness pass (docs, black, pytest,
packaging verification). Everything marked **[BLOCKER]** must be resolved
before pushing; the rest are tracked follow-ups.

## Pre-push blockers

1. **[BLOCKER] Placeholder repository URL.** `pyproject.toml`
   (`[project.urls]`), `CONTRIBUTING.md`, and `CHANGELOG.md` all reference
   `https://github.com/examples/jinja-prompt`. Replace with the real repo
   URL, then create the remote and push:

   ```bash
   git remote add origin https://github.com/<owner>/<repo>.git
   git push -u origin main
   ```

2. **[BLOCKER] No git remote is configured** (`git remote -v` is empty).
   Nothing can be deployed until the real remote is added (see above).

3. **[BLOCKER] The `[openai]` extra promises a module that does not exist.**
   `pyproject.toml` declares `openai = ["openai>=1.0"]` and the README
   describes `jinja_prompt.openai.OpenAIClient` as "planned". Installing
   the extra today pulls the OpenAI SDK but provides no usable adapter.
   Either ship `src/jinja_prompt/openai.py` behind the extra, or remove
   the extra and the README paragraph until it exists.

## Verified behaviours worth noting (not bugs, but surprising)

4. **Duplicate attributes silently last-wins.** `{% prompt model="a"
   model="b" %}` does not raise; `model="b"` wins (`_parse_attrs` builds a
   dict). Consider raising on duplicates.

5. **Whitespace inside the opening tag is safe** — Jinja's lexer collapses
   inter-token whitespace, so multi-line attribute lists parse correctly
   (regression-tested now).

6. **Python version support is claimed but untested below 3.13.** The
   local sandbox only has Python 3.13; the CI matrix in
   `.github/workflows/ci.yml` covers 3.8–3.13, but it cannot be exercised
   until the repo is pushed. Keep `requires-python >=3.8` only if CI
   passes there (Jinja2 and pytest resolve compatible versions per
   interpreter).

## Environment notes (this machine only)

7. **`python -m build` with build isolation fails here** because the
   isolated build environment cannot reach PyPI from this sandbox;
   `python -m build --no-isolation` succeeds and `twine check dist/*`
   passes for both sdist and wheel (wheel correctly contains
   `py.typed` and LICENSE). This is a sandbox limitation, not a repo
   defect.

8. **Default branch renamed `master` → `main`** to match what the docs
   already promised (`CONTRIBUTING.md` says branch off / PR against
   `main`). When creating the GitHub repo, ensure the default branch is
   `main`, since the CI workflow triggers on `push: branches: [main]`.

## Status of the deploy-readiness checks

- `black --check src tests` — clean (config in `[tool.black]`).
- `pytest` — 17 passed, mocked clients only, no network needed.
- `python -m build --no-isolation && twine check dist/*` — PASSED.
- Docs: README, CONTRIBUTING, CHANGELOG, LICENSE present; docstrings
  throughout the module; `py.typed` shipped.
