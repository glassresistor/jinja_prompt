# Changelog

All notable changes to this project are documented here, following the
format of [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and
the project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- `{% prompt %} ... {% endprompt %}` Jinja2 extension block that renders its
  contents, sends them to an LLM client (`environment.jinja_prompt_client`),
  and inserts the Markdown response into the template.
- Optional `model=` and `system=` attributes on the opening tag, forwarded
  to the client.
- Sync and async render hooks (`template.render()` and
  `await template.render_async()`).
- Test suite (pytest) using a mocked LLM client; no network access needed.
- Packaging metadata (pyproject), README, CONTRIBUTING guide, MIT license,
  `py.typed` marker, GitHub Actions CI (black + pytest matrix).

## [0.1.dev0] - 2026-10-08

Initial development release of the extension core and test suite.

[Unreleased]: https://github.com/examples/jinja-prompt/compare/v0.1.dev0...HEAD
[0.1.dev0]: https://github.com/examples/jinja-prompt/releases/tag/v0.1.dev0
