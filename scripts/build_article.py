#!/usr/bin/env python3
"""Render the English essay into the site's existing page shell."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from latex2mathml.converter import convert
from markdown_it import MarkdownIt
from site_utils import write_html

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / 'writing/commentary-on-compute-market-model/index.html'
SOURCE = ROOT / 'content/article-en.md'
MD = MarkdownIt('commonmark', {'html': True})
SECTION_IDS = ['service', 'curves', 'hedging', 'financing', 'evidence']


def render(source: str) -> str:
    """Render LaTeX and source notes before parsing prose as Markdown."""
    source = re.sub(r'\$\$\s*(.*?)\s*\$\$', lambda m: '<div class="equation" tabindex="0">' + convert(m[1], display='block') + '</div>', source, flags=re.S)
    source = re.sub(r'\$([^$\n]+)\$', lambda m: convert(m[1]), source)
    seen = set()
    def citation(match):
        number = match[1]
        anchor = f' id="cite-{number}"' if number not in seen else ''
        seen.add(number)
        return f'<sup class="cite"{anchor}><a href="#ref-{number}" aria-label="Reference {number}">{number}</a></sup>'
    return MD.render(re.sub(r'\[\^(\d+)\]', citation, source))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--english-source', type=Path, help='Import a Markdown essay before rendering.')
    args = parser.parse_args()
    if args.english_source:
        SOURCE.write_text(args.english_source.read_text(encoding='utf-8'), encoding='utf-8')
    source = SOURCE.read_text(encoding='utf-8')
    lines = source.splitlines()
    title, subtitle = lines[0][2:], lines[2].strip('*')
    body, references = '\n'.join(lines[4:]).split('\n## References\n', 1)
    parts = re.split(r'<h2>(.*?)</h2>\n', render(body))
    if len(parts) != 1 + 2 * len(SECTION_IDS):
        raise ValueError('Update SECTION_IDS when changing the essay sections.')
    html = f'<article class="document"><header><h2 class="page-title">{title}</h2><p class="page-subtitle">{subtitle}</p><p class="page-meta"><time datetime="2026-09">September 2026</time></p></header>'
    html += parts[0]
    for anchor, heading, content in zip(SECTION_IDS, parts[1::2], parts[2::2]):
        html += f'<section aria-labelledby="{anchor}"><h3 id="{anchor}">{heading}</h3>{content}</section>'
    html += '<section aria-labelledby="references"><h3 id="references">References</h3><ol class="reference-list">'
    urls = []
    for number, text in re.findall(r'^\[\^(\d+)\]: (.+)$', references, flags=re.M):
        rendered = MD.renderInline(text)
        html += f'<li class="reference-item" id="ref-{number}">{rendered} <a class="reference-back" href="#cite-{number}" aria-label="Back to citation {number}">↩</a></li>'
        urls.extend(re.findall(r'href="(https:[^"]+)"', rendered))
    html += '</ol></section></article>'
    soup = BeautifulSoup(ARTICLE.read_text(encoding='utf-8'), 'html.parser')
    soup.select_one('article.document').replace_with(BeautifulSoup(html, 'html.parser').article)
    soup.select_one('.back-link a').string = 'Back'
    soup.title.string = f'{title} | Joan Vidal Llauradó'
    for tag in soup.select('meta[property="og:title"], meta[name="twitter:title"]'):
        tag['content'] = title
    schema = soup.find('script', type='application/ld+json')
    data = json.loads(schema.string)
    data.update(name=title, headline=title, dateModified='2026-09-20', mainEntityOfPage=data['url'], citation=urls)
    data.pop('wordCount', None)
    data.pop('datePublished', None)
    schema.string = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    write_html(ARTICLE, soup)
    print(f'Rendered {title}: {len(SECTION_IDS)} sections and {len(urls)} references.')

if __name__ == '__main__':
    main()
