import re

from markdown_it import MarkdownIt
from mdit_py_plugins.anchors import anchors_plugin
from mdit_py_plugins.footnote import footnote_plugin

WIKILINK_RE = re.compile(r"\[\[([^\[\]|]+)(?:\|([^\[\]]+))?\]\]")


def wikilinks_plugin(md: MarkdownIt, base_url: str = "/view/", suffix: str = "") -> None:
    """Parse [[Target]] and [[Target|Label]] into links to base_url+Target+suffix."""

    def rule(state, silent):
        if state.src[state.pos : state.pos + 2] != "[[":
            return False
        m = WIKILINK_RE.match(state.src, state.pos)
        if not m:
            return False
        if silent:
            state.pos = m.end()
            return True
        target = m.group(1).strip()
        label = (m.group(2) or m.group(1)).strip()
        tok_open = state.push("link_open", "a", 1)
        tok_open.attrs["href"] = f"{base_url}{target}{suffix}"
        tok_text = state.push("text", "", 0)
        tok_text.content = label
        state.push("link_close", "a", -1)
        state.pos = m.end()
        return True

    md.inline.ruler.before("link", "wikilink", rule)


md = (
    MarkdownIt(
        "commonmark",
        {"html": False, "breaks": True, "typographer": True},
    )
    .enable(["table", "strikethrough", "replacements", "smartquotes"])
    .use(footnote_plugin)
    .use(anchors_plugin, max_level=3)
    .use(wikilinks_plugin)
)


def convert(text: str) -> str:
    return md.render(text)
