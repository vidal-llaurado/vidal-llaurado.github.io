"""Shared paths and HTML formatting for the static site."""
from pathlib import Path
import re

PUBLIC_DIRECTORIES = ('assets', 'papers', 'projects', 'writing')
PUBLIC_FILES = ('.nojekyll', 'index.html', 'robots.txt', 'sitemap.xml')


def page_files(root: Path):
    return [root/'index.html', *sorted(path for directory in PUBLIC_DIRECTORIES[1:]
                                     for path in (root/directory).rglob('index.html'))]


def public_files(root: Path):
    for name in PUBLIC_FILES:
        yield root/name
    for directory in PUBLIC_DIRECTORIES:
        for path in sorted((root/directory).rglob('*')):
            if path.is_file() and not any(part.startswith('.') for part in path.relative_to(root).parts):
                yield path


def write_html(path: Path, soup):
    text = re.sub(r'(?<=>)(?=</?(?:head|body|main|aside|header|nav|section|article|p|h[1-6]|ul|ol|li|table|thead|tbody|tr|div|script|meta|link|title)\b)', '\n', str(soup))
    path.write_text(text.rstrip()+'\n', encoding='utf-8')
