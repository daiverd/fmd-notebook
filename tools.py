from markdown import Markdown
from markdown.extensions.wikilinks import WikiLinkExtension

class MarkdownWrapper:
  """A class to render Markdown with specific configurations."""

  def __init__(self, extensions=[], **kwargs):
    """
    Initialize the class with optional extensions and keyword arguments
    passed to the Markdown instance.
    """
    self.extensions = extensions + [
    'abbr',
    'admonition',
    'attr_list',
    'codehilite',
    'def_list',
    'extra',
    'fenced_code',
    'footnotes',
    'legacy_attrs',
    'legacy_em',
    'md_in_html',
    'meta',
    'nl2br',
    'sane_lists',
    'smarty',
    'tables',
    'toc'
    ]
    self.configure_extensions()
    self.markdown = Markdown(extensions=self.extensions, **kwargs)

  def configure_extensions(self):
    wiki_extension = WikiLinkExtension(base_url="/view/", end_url=".md")
    self.extensions.append(wiki_extension)
    
  def convert(self, text):
    """
    Converts Markdown text to HTML using the configured Markdown instance.
    """
    return self.markdown.convert(text)

markdown = MarkdownWrapper()

def convert(text):
  return markdown.convert(text)