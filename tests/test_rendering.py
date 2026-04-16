import pytest
from tools import convert


class TestXSS:
    def test_script_tag_neutralized(self):
        assert "<script>" not in convert("<script>alert('xss')</script>")

    def test_img_onerror_neutralized(self):
        assert "<img" not in convert('<img src=x onerror="alert(1)">')

    def test_javascript_url_rejected(self):
        assert '<a href="javascript:' not in convert("[click](javascript:alert(1))")

    def test_iframe_neutralized(self):
        assert "<iframe" not in convert("<iframe src='http://evil'></iframe>")


class TestFeatures:
    def test_heading(self):
        assert "<h1" in convert("# hello")

    def test_bold(self):
        assert "<strong>bold</strong>" in convert("**bold**")

    def test_italic(self):
        assert "<em>italic</em>" in convert("*italic*")

    def test_breaks(self):
        assert "<br" in convert("line one\nline two")

    def test_fenced_code(self):
        out = convert("```python\nprint('hi')\n```")
        assert "<pre>" in out
        assert "<code" in out

    def test_table(self):
        assert "<table>" in convert("| a | b |\n|---|---|\n| 1 | 2 |")

    def test_strikethrough(self):
        assert "<s>" in convert("~~gone~~")

    def test_footnotes(self):
        assert "footnote" in convert("Foo[^1]\n\n[^1]: the note")

    def test_smart_quotes(self):
        assert "\u201c" in convert('He said "hello" today.')

    def test_em_dash(self):
        out = convert("dash -- here")
        assert "\u2013" in out or "\u2014" in out

    def test_anchor_ids(self):
        assert 'id="' in convert("## My Section")


class TestWikilinks:
    def test_bare(self):
        assert '<a href="/view/MyNote">MyNote</a>' in convert("See [[MyNote]].")

    def test_with_label(self):
        assert '<a href="/view/Target">Friendly</a>' in convert("See [[Target|Friendly]].")

    def test_stem_form_no_md(self):
        out = convert("[[Foo]]")
        assert "/view/Foo" in out
        assert ".md" not in out
