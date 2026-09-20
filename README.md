# Personal website

English static HTML with shared CSS and native MathML. The checked-in pages are ready to serve; readers need no JavaScript or third-party font requests.

## Preview

```bash
python3 -m http.server 8765 --bind 127.0.0.1
```

Open `http://127.0.0.1:8765/`. The server is local to this computer. Press Ctrl-C to stop it.

## Edit and check

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python scripts/build_article.py
python scripts/prepare_site.py
python scripts/check_site.py
```

The essay source is `content/article-en.md`. Paper and project pages live directly in `papers/` and `projects/`; the essay is under `writing/`.

The renderer preserves the page shell and converts LaTeX to static MathML. Other pages are edited directly. `assets/styles.css` owns the shared layout, typography, full-width subtitles, date fields and resource links. Display dates use a full month and year, with a matching `time` element. Software versions remain in structured metadata.

`check_site.py` checks internal links, PDF names, anchors, canonical URLs, sitemap coverage, structured data and MathML structure. Review desktop and mobile rendering after visual changes.

## Prepare publication

`site.json` holds the canonical origin and modification date. The current origin, `https://vidal-llaurado.github.io`, is provisional. Once the final domain is chosen:

```bash
python scripts/prepare_site.py --base-url https://example.com
python scripts/check_site.py
python scripts/prepare_site.py --output /path/to/new-public-site
python scripts/check_site.py --root /path/to/new-public-site
```

Choose a new output directory. The export contains `index.html`, `assets/`, `papers/`, `projects/`, `writing/`, `robots.txt`, `sitemap.xml` and `.nojekyll`. Maintenance scripts and article source stay in the source repository.

Any static host that serves directory `index.html` files can serve the export. The home page lives at `/`; every page has a single canonical URL.

For the configured GitHub Pages address, create an empty public repository named `vidal-llaurado.github.io` under `vidal-llaurado`. Leave the README, license and `.gitignore` initialization options off because this source already contains the required files. After pushing the site to `main`, select **Settings → Pages → Deploy from a branch → main → /(root)**. `.nojekyll` keeps the checked-in HTML and MathML intact. [GitHub's publishing guide](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site) describes these settings.

After deploying, check HTTPS, page and PDF responses, and canonical URLs. Submit `/sitemap.xml` in the site's Search Console property and inspect representative URLs.

[Google's SEO guidance](https://developers.google.com/search/docs/fundamentals/seo-starter-guide) explains crawlability, descriptive links and indexing checks.
