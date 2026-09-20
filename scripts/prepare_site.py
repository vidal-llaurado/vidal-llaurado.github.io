#!/usr/bin/env python3
"""Refresh crawl metadata and optionally export only public static files."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit
from bs4 import BeautifulSoup
from site_utils import page_files, public_files, write_html

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'site.json'
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', help='Final HTTPS origin; omit to retain the configured address.')
    parser.add_argument('--output', type=Path, help='New external directory for the uploadable static site.')
    args = parser.parse_args()
    config = json.loads(CONFIG.read_text())
    old_base = config['base_url']
    base = (args.base_url or old_base).rstrip('/')
    url = urlsplit(base)
    if url.scheme != 'https' or not url.netloc or url.path or url.query or url.fragment:
        raise ValueError('Use an HTTPS origin without a subpath, query or fragment.')
    output = args.output.resolve() if args.output else None
    if output and (output.exists() or output == ROOT or ROOT in output.parents):
        raise ValueError('Choose a new output directory outside the source site.')
    revision = hashlib.sha256((ROOT / 'assets/styles.css').read_bytes()).hexdigest()[:12]
    pages = page_files(ROOT)
    for path in pages:
        text = path.read_text(encoding='utf-8').replace(old_base, base)
        text = re.sub(r'assets/styles\.css(?:\?v=[^"\s]+)?', f'assets/styles.css?v={revision}', text)
        soup = BeautifulSoup(text, 'html.parser')
        for tag in soup.select('link[hreflang]'):
            tag.decompose()
        if path == ROOT/'index.html':
            for item in soup.select('.paper'):
                link = item.select_one('.paper-doi a')
                if link:
                    link['aria-label'] = 'Read more: '+item.h2.get_text(' ', strip=True)
        write_html(path, soup)
    ET.register_namespace('', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    namespace = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
    sitemap = ET.Element(namespace + 'urlset')
    for path in pages:
        entry = ET.SubElement(sitemap, namespace + 'url')
        relative = path.parent.relative_to(ROOT).as_posix()
        ET.SubElement(entry, namespace + 'loc').text = base+'/' if relative == '.' else base+'/'+relative+'/'
        ET.SubElement(entry, namespace + 'lastmod').text = config['updated']
    ET.indent(sitemap, space='  ')
    ET.ElementTree(sitemap).write(ROOT / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
    (ROOT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n')
    config['base_url'] = base
    CONFIG.write_text(json.dumps(config, indent=2) + '\n')
    if output:
        output.mkdir(parents=True)
        for path in public_files(ROOT):
            dest = output / path.relative_to(ROOT)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)
        print(f'Exported static site to {output}')
    print(f'Refreshed metadata for {len(pages)} English pages.')

if __name__ == '__main__':
    main()
