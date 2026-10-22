# jinja-prompt

A [Jinja2](https://jinja.palletsprojects.com/) extension that adds a
`{% prompt %}` block tag to your templates. The block renders its own
template contents, sends the result to a large language model (LLM), and
inserts the response back into the template as Markdown.

```
{% prompt %}
{{ some_variable }} goes to the store.
{% endprompt %}
```

## Install

```bash
pip install jinja-prompt
# optional: helper for talking to OpenAI-compatible APIs
pip install "jinja-prompt[openai]"
```

## Usage

Add the extension to a Jinja environment and attach an LLM client:

```python
import jinja2
from jinja_prompt import PromptExtension

env = jinja2.Environment(...)
env.add_extension(PromptExtension)
env.jinja_prompt_client = MyLLMClient(...)  # see "Clients" below

template = env.from_string(
    "{% prompt %}\nSummarize: {{ text }}\n{% endprompt %}"
)
print(template.render(text="..."))
```

### Attributes

The opening tag accepts optional `key="value"` attributes, which are forwarded
to the client:

```
{% prompt model="gpt-4o-mini" system="Be terse." %}
What is {{ n }} plus one?
{% endprompt %}
```

Supported attributes: `model`, `system`. Anything else raises a Jinja
`TemplateSyntaxError`.

### Async templates

Works with both `template.render()` and `await template.render_async()`;
pick whichever matches your environment (`enable_async=True`).

## Clients

The extension talks to an object you provide as
`environment.jinja_prompt_client`. It only needs one method:

```python
class MyClient:
    def complete(self, prompt_text: str, model=None, system=None) -> str:
        ...  # call your LLM API and return the response text (Markdown)
```

This indirection keeps `jinja-prompt` dependency-free at its core. Bring any
SDK you like (OpenAI, Anthropic, Ollama, a local model, or even a cache).
For convenience an optional adapter for OpenAI-compatible chat-completions is
planned as `jinja_prompt.openai.OpenAIClient` (install with the `[openai]`
extra) -- see [CONTRIBUTING.md](CONTRIBUTING.md) if you'd like to help build
it.

## Why?

Embedding prompts directly inside templates keeps natural-language logic close
to the data it renders, without a separate prompt-management layer. The block
is evaluated lazily (during rendering), and its rendered contents are sent
verbatim as the user prompt after surrounding whitespace is stripped -- so
Jinja variables, loops, and conditionals all work inside the block.

## Testing and linting this package

```bash
python -m venv .venv && source .venv/bin/activate   # or: python -m venv venv
pip install -e ".[test]"
pytest                # run the test suite
black src tests       # format code; CI checks formatting with black --check
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the development workflow.
