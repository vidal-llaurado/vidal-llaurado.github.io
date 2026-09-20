#!/usr/bin/env python3
"""Check links, crawl metadata and MathML in the static English site."""
from __future__ import annotations
import argparse
import json
import re
import sys
from datetime import datetime
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlsplit
from bs4 import BeautifulSoup
from site_utils import page_files, public_files

ROOT = Path(__file__).resolve().parents[1]


def check(root: Path):
    pages = {p: BeautifulSoup(p.read_text(encoding='utf-8'), 'html.parser') for p in page_files(root)}
    problems = []
    counts = {'pages':len(pages), 'math_expressions':0, 'local_links':0, 'pdfs':sum(p.suffix=='.pdf' for p in public_files(root))}
    canonical_urls = set()
    for path, soup in pages.items():
        name = path.relative_to(root).as_posix()
        def fail(message):
            problems.append(f'{name}: {message}')
        if soup.html.get('lang') != 'en':fail('non-English page')
        canonical = soup.find('link', rel='canonical')
        if not canonical:fail('missing canonical URL');continue
        url = canonical.get('href','')
        if not url.startswith('https://'):fail('canonical must be HTTPS')
        relative = path.parent.relative_to(root).as_posix()
        expected_path = '/' if relative=='.' else '/'+relative+'/'
        if urlsplit(url).path!=expected_path:fail('canonical path differs from page location')
        if url in canonical_urls:fail('duplicate canonical URL')
        canonical_urls.add(url)
        if not soup.title or not soup.title.get_text(strip=True):fail('missing title')
        if path == root/'index.html':
            if soup.find('meta', attrs={'name':'description'}):fail('homepage has a description fallback for link previews')
        elif not soup.find('meta',attrs={'name':'description'}):fail('missing description')
        if soup.select_one('meta[name="robots"][content*="noindex"]'):fail('indexable page has noindex')
        if not soup.main:fail('missing main content')
        if soup.select('.language-nav, link[hreflang]'):fail('obsolete language navigation')
        og = soup.find('meta',property='og:url')
        if not og or og['content']!=url:fail('Open Graph URL differs from canonical')
        if path == root/'index.html':
            share_image = url.rstrip('/')+'/assets/share-home.png'
            if not soup.find('meta', property='og:image', content=share_image):fail('homepage is missing its Open Graph share image')
            if not soup.find('meta', attrs={'name':'twitter:image', 'content':share_image}):fail('homepage is missing its Twitter share image')
            if soup.find('meta', property='og:description'):fail('homepage share preview has an Open Graph description')
            if soup.find('meta', attrs={'name':'twitter:description'}):fail('homepage share preview has a Twitter description')
            image = root/'assets/share-home.png'
            if not image.is_file():fail('homepage share image file is missing')
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data=json.loads(script.string)
                if data.get('url')!=url:fail('structured-data URL differs from canonical')
                if 'writing' in path.parts and data.get('headline')!=soup.select_one('.page-title').get_text():fail('article headline differs from visible title')
                def inspect_urls(value):
                    if isinstance(value,dict):
                        for child in value.values():inspect_urls(child)
                    elif isinstance(value,list):
                        for child in value:inspect_urls(child)
                    elif isinstance(value,str) and value.startswith('https://') and urlsplit(value).netloc==urlsplit(url).netloc:
                        target = root/unquote(urlsplit(value).path).lstrip('/')
                        if target.is_dir():target=target/'index.html'
                        if not target.is_file():fail(f'missing structured-data target {value}')
                inspect_urls(data)
                if data.get('@type')=='SoftwareSourceCode':
                    repository='https://github.com/vidal-llaurado/'+path.parent.name
                    if data.get('codeRepository')!=repository:fail('incorrect repository metadata')
                    if not soup.select_one(f'.resource-links a[href="{repository}"]'):fail('missing repository link')
            except (ValueError,TypeError):fail('invalid JSON-LD')
        for time in soup.select('time'):
            try:
                expected=datetime.strptime(time['datetime'],'%Y-%m').strftime('%B %Y')
                if time.get_text()!=expected:fail('date must use full month and year')
            except (KeyError,ValueError):fail('invalid month metadata')
        if path != root/'index.html':
            if not soup.select_one('header .page-meta time'):fail('missing shared date field')
            if not soup.select_one('.back-link a[href="/"]'):fail('missing Back link to home')
        if soup.select('.project-byline, .project-meta, .paper-meta, .project-links, .paper-links'):fail('obsolete page metadata or resource styles')
        ids = [el['id'] for el in soup.select('[id]')]
        if len(ids)!=len(set(ids)):fail('duplicate element id')
        for tag in soup.select('[href], img[src], meta[name="citation_pdf_url"]'):
            target = tag.get('href',tag.get('src',tag.get('content','')))
            parsed = urlsplit(target)
            if parsed.scheme in ['mailto','tel']:continue
            if parsed.netloc and parsed.netloc!=urlsplit(url).netloc:continue
            if parsed.scheme and parsed.scheme not in ['https','http']:continue
            relative = unquote(parsed.path)
            if re.match(r'^/(en|es|zh)/',relative):fail('language prefix remains in a local link')
            dest = (root/relative.lstrip('/')) if parsed.netloc or relative.startswith('/') else (path.parent/relative)
            if not relative:dest=path
            dest=dest.resolve()
            if dest.is_dir():dest=dest/'index.html'
            counts['local_links']+=1
            if not dest.is_file():fail(f'missing target {target}');continue
            if parsed.fragment and dest.suffix=='.html':
                target_soup=pages.get(dest)
                if target_soup is None:target_soup=BeautifulSoup(dest.read_text(),'html.parser')
                if not target_soup.find(id=unquote(parsed.fragment)):fail(f'missing anchor {target}')
        for math in soup.find_all('math'):
            counts['math_expressions']+=1
            if math.get('xmlns')!='http://www.w3.org/1998/Math/MathML':fail('MathML namespace missing')
        for child in soup.find_all(['msub','msup','mfrac','msubsup','mi','mo','mn','mrow']):
            if not child.find_parent('math'):fail(f'orphan MathML {child.name}')
            if child.name in ['msub','msup','mfrac','msubsup']:
                expected=3 if child.name=='msubsup' else 2
                if len(child.find_all(recursive=False))!=expected:fail(f'invalid {child.name} child count')
        for node in soup.find_all(string=True):
            if node.find_parent(['script','style','math']):continue
            if re.search(r'\\(?:[a-zA-Z]+|[([])|\b[A-Za-z]_[A-Za-z]|\^\{',str(node)):fail(f'unrendered math: {str(node)[:80]}')
        for img in soup.find_all('img'):
            if not all(key in img.attrs for key in ['alt','width','height']):fail('image missing alt or dimensions')
    sitemap = ET.parse(root/'sitemap.xml')
    locations={n.text for n in sitemap.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
    if locations!=canonical_urls:problems.append('Sitemap and English canonical pages differ')
    if any((root/language).exists() for language in ['en','es','zh']):problems.append('Language directories remain')
    if list(root.glob('papers/*/paper.pdf')):problems.append('Generic paper.pdf filenames remain')
    if not (root/'.nojekyll').is_file():problems.append('Missing static GitHub Pages marker')
    article=pages[root/'writing/commentary-on-compute-market-model/index.html']
    if article.select('.article-contents, .resource-links'):problems.append('Unrequested article navigation remains')
    if 'min read' in article.get_text():problems.append('Reading-time label remains')
    if article.select_one('.page-title').get_text()!='On modeling compute markets':problems.append('Incorrect essay title')
    if article.select_one('.back-link a').get_text()!='Back':problems.append('Incorrect Back link')
    return {'counts':counts,'problems':problems,'passed':not problems}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    report=check(args.root.resolve())
    if args.output:args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return 0 if report['passed'] else 1

if __name__=='__main__':
    sys.exit(main())
