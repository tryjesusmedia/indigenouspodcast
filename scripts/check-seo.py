"""Validate crawlable static pages and preserve the original guide lesson text."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote
import collections
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT/'dist'
BASE = 'https://indigenouspodcast.org'
BASELINE = sys.argv[1] if len(sys.argv) > 1 else 'HEAD'

class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.metas = collections.defaultdict(list)
        self.ids = []
        self.links = []
        self.assets = []
        self.titles = []
        self.headings = []
        self.canonicals = []
        self.schemas = []
        self.capture = None
        self.value = ''
        self.feed(source)
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a: self.ids.append(a['id'])
        if tag == 'meta': self.metas[a.get('name',a.get('property'))].append(a.get('content',''))
        if tag == 'a' and 'href' in a: self.links.append(a['href'])
        if tag in ('img','script') and 'src' in a: self.assets.append(a['src'])
        if tag == 'img': assert 'alt' in a, 'Image missing alt attribute'
        if tag == 'link' and a.get('rel') == 'canonical': self.canonicals.append(a['href'])
        if tag == 'link' and a.get('rel') in ('stylesheet','icon','preload'): self.assets.append(a['href'])
        if tag in ('title','h1') or (tag == 'script' and a.get('type') == 'application/ld+json'):
            self.capture = tag
            self.value = ''
    def handle_data(self, data):
        if self.capture: self.value += data
    def handle_endtag(self, tag):
        if tag == self.capture:
            if tag == 'title': self.titles.append(self.value.strip())
            if tag == 'h1': self.headings.append(self.value.strip())
            if tag == 'script': self.schemas.append(json.loads(self.value))
            self.capture = None

sources = {('/' if p.stem=='index' else '/'+p.stem):p.read_text(encoding='utf-8') for p in DIST.glob('*.html')}
pages = {url:Page(source) for url,source in sources.items()}
indexable = set(pages)-{'/welcome','/404'}
all_titles, all_descriptions = [], []
for path,p in pages.items():
    assert len(p.titles) == len(p.headings) == 1, (path,'title/H1 count')
    assert len(p.metas['description']) == 1, (path,'description count')
    assert len(p.ids) == len(set(p.ids)), (path,'duplicate IDs')
    assert len(p.metas['robots']) == 1, (path,'robots count')
    all_titles += p.titles
    all_descriptions += p.metas['description']
    if path in indexable:
        assert p.canonicals == [BASE+path], (path,'canonical mismatch')
        assert 'noindex' not in p.metas['robots'][0], path
        assert len(p.schemas) == 1 and p.schemas[0]['@context'] == 'https://schema.org', path
        assert p.metas['og:url'] == [BASE+path], path
        assert p.metas['og:title'] == p.titles, path
        assert p.metas['twitter:description'] == p.metas['description'], path
    else:
        assert 'noindex' in p.metas['robots'][0], path
    for href in p.links+p.assets:
        url = urlsplit(urljoin(BASE+path,href))
        if url.netloc != 'indigenouspodcast.org': continue
        route = unquote(url.path)
        if route in pages:
            if url.fragment: assert unquote(url.fragment) in pages[route].ids, (path,href,'missing anchor')
        else:
            assert (DIST/route.lstrip('/')).is_file(), (path,href,'missing file')
assert len(set(all_titles))==len(all_titles),'duplicate page titles'
assert len(set(all_descriptions))==len(all_descriptions),'duplicate descriptions'
tree = ET.parse(DIST/'sitemap.xml')
sitemap = [n.text for n in tree.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
assert set(sitemap)=={BASE+p for p in indexable} and len(sitemap)==32, 'sitemap mismatch'
assert '<html' not in (DIST/'robots.txt').read_text() and BASE+'/sitemap.xml' in (DIST/'robots.txt').read_text()
reached, queue = set(), ['/']
while queue:
    path = queue.pop()
    if path in reached: continue
    reached.add(path)
    for href in pages[path].links:
        url = urlsplit(urljoin(BASE+path,href))
        if url.netloc == 'indigenouspodcast.org' and url.path in pages: queue.append(url.path)
assert indexable <= reached, ('orphan pages',indexable-reached)
for i in range(1,31):
    path = f'/guide{i:02}'
    original = subprocess.check_output(['git','show',f'{BASELINE}:dist/guide{i:02}.html'],cwd=ROOT).decode('utf-8')
    pattern = r'<section class="guide-section".*?</section>'
    assert re.findall(pattern,original,re.S)==re.findall(pattern,sources[path],re.S), (path,'lesson text changed')
    article = next(n for n in pages[path].schemas[0]['@graph'] if n['@type']=='Article')
    assert article['headline'] == pages[path].headings[0], (path,'schema headline mismatch')
print(json.dumps({'html_pages':len(pages),'indexable_pages':len(indexable),'sitemap_urls':len(sitemap),
                  'guides_with_original_lesson_text':30,'orphan_pages':0,'broken_internal_links_or_assets':0,
                  'duplicate_titles':0,'duplicate_descriptions':0,'structured_data':'valid JSON, matching page metadata'},indent=2))
