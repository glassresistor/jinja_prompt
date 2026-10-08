"""Tests for the jinja_prompt Jinja2 extension.

These tests mock the LLM client so no network access is required.  They assert
the behaviour described in the README:

* ``{% prompt %} ... {% endprompt %}`` renders its contents, sends them to a
  large language model and inserts the response back into the template as
  Markdown.
* Optional ``model=`` / ``system=`` attributes are forwarded to the client.
"""
import pytest

import jinja2
from jinja2.exceptions import TemplateSyntaxError

import jinja_prompt


class FakeClient:
    """A deterministic stand-in for a real LLM API client."""

    def __init__(self, response="**hello world**"):
        self.response = response
        # Every call made against the client is recorded here.
        self.calls = []

    def complete(self, prompt_text, model=None, system=None):
        self.calls.append(
            {"prompt": prompt_text, "model": model, "system": system}
        )
        return self.response


def make_env(client, **env_kwargs):
    env = jinja2.Environment(**env_kwargs)
    env.add_extension(jinja_prompt.PromptExtension)
    env.jinja_prompt_client = client
    return env


def render(source, context=None, client=None):
    if client is None:
        client = FakeClient()
    env = make_env(client)
    out = env.from_string(source).render(context or {})
    return out, client


def test_block_renders_llm_response():
    out, client = render(
        "{% prompt %}\nWhat is 2+2?\n{% endprompt %}",
        client=FakeClient(response="4"),
    )
    assert out == "4"
    # The rendered contents were sent to the model.
    assert client.calls[0]["prompt"] == "What is 2+2?"


def test_contents_are_evaluated_first():
    client = FakeClient(response="R")
    out, _ = render(
        "{% prompt %}\n{{ who }} says hi\n{% endprompt %}",
        context={"who": "Bob"},
        client=client,
    )
    assert out == "R"
    assert client.calls[0]["prompt"] == "Bob says hi"


def test_model_attribute_forwarded():
    client = FakeClient(response="ok")
    out, _ = render(
        '{% prompt model="gpt-4o-mini" %}\nhi\n{% endprompt %}',
        client=client,
    )
    assert out == "ok"
    assert client.calls[0]["model"] == "gpt-4o-mini"


def test_system_attribute_forwarded():
    client = FakeClient(response="ok")
    _, _ = render(
        '{% prompt system="be terse" %}\nhi\n{% endprompt %}',
        client=client,
    )
    assert client.calls[0]["system"] == "be terse"


def test_response_is_returned_as_markdown_verbatim():
    md = "# Title\n\n- a\n- b\n"
    out, _ = render(
        "{% prompt %}\nprompt body\n{% endprompt %}",
        client=FakeClient(response=md),
    )
    assert out == md


def test_inline_usage_without_surrounding_newlines():
    out, client = render(
        "pre {% prompt %}body{% endprompt %} post",
        client=FakeClient(response="X"),
    )
    assert out == "pre X post"


def test_multiple_blocks_in_one_template():
    class Counting:
        def __init__(self):
            self.calls = []
            self.n = 0

        def complete(self, prompt_text, model=None, system=None):
            self.calls.append(prompt_text)
            self.n += 1
            return f"r{self.n}"

    client = Counting()
    out, _ = render(
        "A:{% prompt %}\none\n{% endprompt %}|"
        "B:{% prompt %}\ntwo\n{% endprompt %}",
        client=client,
    )
    assert out == "A:r1|B:r2"
    assert client.calls == ["one", "two"]


def test_no_client_configured_raises():
    env = jinja2.Environment()
    env.add_extension(jinja_prompt.PromptExtension)
    with pytest.raises(RuntimeError):
        env.from_string("{% prompt %}\nx\n{% endprompt %}").render()


def test_missing_end_tag_is_syntax_error():
    client = FakeClient()
    env = make_env(client)
    with pytest.raises(TemplateSyntaxError):
        env.from_string("{% prompt %}\nno closing tag\n").render()


def test_unknown_attribute_raises_template_syntax_error():
    client = FakeClient()
    env = make_env(client)
    with pytest.raises(TemplateSyntaxError) as excinfo:
        env.from_string('{% prompt bogus="x" %}\ny\n{% endprompt %}').render()
    assert "bogus" in str(excinfo.value)


def test_malformed_attribute_raises_template_syntax_error():
    client = FakeClient()
    env = make_env(client)
    with pytest.raises(TemplateSyntaxError):
        env.from_string("{% prompt model %}\ny\n{% endprompt %}").render()


def test_async_render_works():
    import asyncio

    client = FakeClient(response="async ok")
    env = make_env(client, enable_async=True)
    result = asyncio.run(
        env.from_string("{% prompt %}\nhello\n{% endprompt %}").render_async()
    )
    assert result == "async ok"



