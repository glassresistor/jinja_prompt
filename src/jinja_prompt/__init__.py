"""jinja_prompt: a Jinja2 extension for {% prompt %} blocks backed by an LLM.

Usage::

    {% prompt %}
    {{ some_variable }} goes to the store.
    {% endprompt %}

The block renders its contents, sends them to a large language model via a
pluggable client object installed on the Jinja environment as``environment.jinja_prompt_client``, and inserts the response back intothe template as Markdown.

Optional attributes are forwarded to the client: ``model=`` and ``system=``
"""

import json
from typing import Any, Dict, Optional

from jinja2 import nodes
from jinja2.exceptions import TemplateSyntaxError
from jinja2.ext import Extension

__version__ = "0.1.dev0"
__all__ = ["PromptExtension"]

# Attributes accepted inside the {% prompt %} opening tag.
ALLOWED_ATTRS = ("model", "system")


class PromptExtension(Extension):
    """Jinja2 extension implementing ``{% prompt %} ... {% endprompt %}``."""

    tags = {"prompt"}

    def parse(self, parser):
        # Consume the tag name; remember its line number for error reporting.
        lineno = next(parser.stream).lineno
        stream = parser.stream
        gathered = []
        # Gather ``name=`` / ``"value"`` token triples up to (but NOT including)
        # the closing '%}' block_end token.  parse_statements() will consume it,
        # which is why we must stop before consuming it here.
        while stream.current.type != "block_end":
            gathered.append(next(stream))
        attrs = self._parse_attrs(gathered, lineno)

        # Choose the render hook matching this environment's mode.  Jinja
        # compiles extension attribute lookups directly (``ext._render_sync``
        # or ``ext._render_async``), so a single method cannot serve both --
        # select it at parse time instead.
        if self.environment.is_async:
            hook_name = "_render_prompt_async"
        else:
            hook_name = "_render_prompt_sync"

        body = parser.parse_statements(["name:endprompt"], drop_needle=True)

        return nodes.CallBlock(
            self.call_method(hook_name, [nodes.Const(json.dumps(attrs))]),
            [],
            [],
            body,
        ).set_lineno(lineno)

    def _parse_attrs(self, gathered, lineno: int) -> Dict[str, str]:
        """Validate ``name=\"value\"`` attribute triples collected by parse()."""
        if len(gathered) % 3 != 0:
            raise TemplateSyntaxError(
                'Invalid syntax for prompt tag - attributes must be name="value"',
                lineno,
            )
        attrs: Dict[str, str] = {}
        for i in range(0, len(gathered), 3):
            name_tok, assign_tok, value_tok = gathered[i : i + 3]
            if not (
                name_tok.type == "name"
                and assign_tok.type == "assign"
                and value_tok.type == "string"
            ):
                raise TemplateSyntaxError(
                    "Invalid attribute syntax in prompt tag - got {!r}, should be "
                    'name="value"'.format([t.value for t in gathered[i : i + 3]]),
                    lineno,
                )
            name = name_tok.value
            if name not in ALLOWED_ATTRS:
                raise TemplateSyntaxError(
                    "Unknown attribute '{}' in prompt tag".format(name), lineno
                )
            attrs[name] = value_tok.value
        return attrs

    def _render_prompt_sync(self, kwargs_json: str, caller):
        """Synchronous render hook (``Environment.render``)."""

        return self._do_render(kwargs_json, caller())

    def _render_prompt_async(self, kwargs_json: str, caller):
        """Async render hook used by ``Environment.render_async``."""
        return self._do_render_async(kwargs_json, caller())

    async def _do_render_async(self, kwargs_json: str, inner_awaitable):
        inner = await inner_awaitable
        return self._do_render(kwargs_json, inner)

    def _do_render(self, kwargs_json: str, inner: str) -> str:
        attrs = json.loads(kwargs_json)
        # Strip surrounding whitespace/newlines around the rendered contents so
        # ``{% prompt %}\n...`` does not send stray blank lines to the model.
        prompt_text = inner.strip()
        client = self._get_client()
        response = client.complete(
            prompt_text,
            model=attrs.get("model"),
            system=attrs.get("system"),
        )
        # Return the response verbatim so Markdown reaches downstream consumers
        # unmodified.
        return str(response)

    def _get_client(self):
        environment = self.environment
        client = getattr(environment, "jinja_prompt_client", None)
        if client is None:
            raise RuntimeError(
                "The {% prompt %} tag needs an LLM client configured as "
                "environment.jinja_prompt_client"
            )
        return client
