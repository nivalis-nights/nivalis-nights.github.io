#!/usr/bin/env python3
"""Validate the exported site, its content registry, links, and public assets."""
import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'out'
SITE = 'https://nivalis-nights.github.io/'
SLUGS = ['', 'guide-wiki', 'liquid-nitrogen', 'fishing', 'mods', 'seafaring']
LEGAL = ['about', 'contact', 'privacy', 'terms', 'copyright']
FAILURES = []

def check(condition, message):
    if not condition:
        FAILURES.append(message)

class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.nodes = []
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        node = dict(tag=tag, attrs=dict(attrs), text='', parents=list(self.stack))
        self.nodes.append(node)
        if tag not in ['area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr']:
            self.stack.append(node)
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)
    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i]['tag'] == tag:
                del self.stack[i:]
                break
    def handle_data(self, data):
        for node in self.stack:
            node['text'] += data + ' '
    def select(self, tag=None, **attrs):
        return [n for n in self.nodes if (not tag or n['tag'] == tag) and all(n['attrs'].get(k) == v for k, v in attrs.items())]

def clean(text):
    return re.sub(r'\s+', ' ', text).strip()

def visible_content(doc):
    # Counts the hero and article, excluding navigation, related cards, and source labels.
    chunks = []
    for n in doc.nodes:
        containers = n['parents'] + [n]
        if n['tag'] not in ['h1', 'h2', 'h3', 'p', 'li', 'td', 'th', 'caption', 'strong', 'span']:
            continue
        if any(p['tag'] in ['script', 'style', 'nav', 'aside', 'footer'] for p in containers):
            continue
        if any(p['attrs'].get('aria-hidden') == 'true' for p in containers):
            continue
        if any(p['attrs'].get('id') in ['sources', 'related-guides'] for p in containers):
            continue
        if not any('data-editorial-content' in p['attrs'] or 'data-editorial-hero' in p['attrs'] for p in containers):
            continue
        # Count leaf text-bearing blocks once, including linked-card descriptions.
        if any(c is not n and n in c['parents'] and c['tag'] in ['h1', 'h2', 'h3', 'p', 'li', 'td', 'th', 'caption', 'strong', 'span'] for c in doc.nodes):
            continue
        if n['attrs'].get('class') in ['eyebrow', 'editorial-reviewed']:
            continue
        if any('editorial-actions' in p['attrs'].get('class', '') for p in containers):
            continue
        chunks.append(n['text'])
    return clean(' '.join(chunks))

def nested_texts(page):
    for sec in page['sections']:
        yield sec['heading']
        yield sec.get('intro','')
        yield from sec.get('paragraphs',[])
        yield from sec.get('bullets',[])
        for sub in sec.get('subsections',[]):
            yield sub['heading']
            yield from sub['paragraphs']
            yield from sub.get('bullets',[])
            for l in sub.get('links',[]):
                yield l['label']
                yield l.get('description','')
        for step in sec.get('steps',[]):
            yield step['heading']; yield step['description']
        for l in sec.get('links',[]):
            yield l['label']; yield l.get('description','')
        for table in [sec.get('table')] + [s.get('table') for s in sec.get('subsections',[])]:
            if table:
                yield table['caption']; yield from table['columns']
                for row in table['rows']: yield from row

parser = argparse.ArgumentParser()
parser.add_argument('--prelaunch', action='store_true')
args = parser.parse_args()
site_config = json.loads((ROOT/'content/generated/site.json').read_text())
home = json.loads((ROOT/'content/generated/home.json').read_text())
pages = [home] + json.loads((ROOT/'content/generated/pages.json').read_text())
check([p['slug'] for p in pages] == SLUGS, 'Exactly six core pages in the locked order')
check(site_config['hosting']['siteUrl'].rstrip('/')+'/' == SITE and not site_config['hosting']['basePath'], 'Root-site hosting config')
check(site_config['readyForLaunch'] == (not args.prelaunch), 'Launch state must match the selected QA mode')
check((OUT/'.nojekyll').exists(), 'Missing .nojekyll')
rows=[]
titles=set(); descriptions=set()
for page in pages:
    slug=page['slug']; route=('/'+slug+'/' if slug else '/')
    canonical=SITE+(slug+'/' if slug else '')
    path=OUT/slug/'index.html'
    check(path.exists(), f'{route}: exported HTML missing')
    if not path.exists(): continue
    doc=Document(path.read_text())
    title_nodes=doc.select('title'); title=clean(title_nodes[0]['text']) if title_nodes else ''
    desc_nodes=doc.select('meta',name='description'); desc=desc_nodes[0]['attrs'].get('content','') if desc_nodes else ''
    check(len(title_nodes)==1 and title==page['title'], f'{route}: exact title')
    check(len(desc_nodes)==1 and desc==page['description'], f'{route}: exact description')
    check(title.isascii() and len(title)<=60, f'{route}: title length/ASCII')
    check(len(desc)<=160, f'{route}: description length')
    check(title not in titles and desc not in descriptions, f'{route}: duplicate metadata')
    titles.add(title); descriptions.add(desc)
    h1=doc.select('h1'); check(len(h1)==1 and clean(h1[0]['text'])==page['hero']['heading'],f'{route}: one matching H1')
    headings=[n for n in doc.nodes if n['tag'] in ['h1','h2','h3']]
    level=0
    for n in headings:
        nxt=int(n['tag'][1]);check(nxt<=level+1, f'{route}: skipped heading level at {clean(n["text"])}');level=nxt
    check(len(doc.select('h2'))>=6, f'{route}: heading coverage')
    check(all(s['id'] in {n['attrs'].get('id') for n in doc.nodes} for s in page['sections']),f'{route}: section anchors')
    check(len(page.get('faq',[])) in [4,5,6],f'{route}: FAQ count')
    check(len(page.get('sources',[]))>=2, f'{route}: source coverage')
    hero=next((n for n in doc.nodes if 'data-editorial-hero' in n['attrs']),None)
    check(hero and clean(page['hero']['lead']) in clean(hero['text']), f'{route}: static above-fold answer')
    check(60<=len(re.findall(r"[A-Za-z0-9]+(?:['-][A-Za-z0-9]+)*",page['hero']['lead']))<=120, f'{route}: hero answer length')
    article=next((n for n in doc.nodes if 'data-editorial-content' in n['attrs']),None)
    article_text=clean(article['text']) if article else ''
    for text in nested_texts(page):
        if text: check(clean(text) in article_text,f'{route}: missing content block {text[:45]}')
    canonical_nodes=doc.select('link',rel='canonical')
    check(len(canonical_nodes)==1 and canonical_nodes[0]['attrs'].get('href')==canonical, f'{route}: canonical')
    expected_robots='noindex, nofollow' if args.prelaunch else 'index, follow'
    check(doc.select('meta',name='robots')[0]['attrs'].get('content')==expected_robots, f'{route}: robots metadata')
    for name, value in [('og:title',page['title']),('og:description',page['description']),('og:url',canonical)]:
        check(any(n['attrs'].get('content')==value for n in doc.select('meta',property=name)), f'{route}: {name}')
    check(any(n['attrs'].get('content')=='summary_large_image' for n in doc.select('meta',name='twitter:card')),f'{route}: Twitter card')
    primary=doc.select('nav',**{'aria-label':'Primary navigation'})
    footer=doc.select('footer')
    check(len(primary)==1 and len(footer)==1,f'{route}: one primary nav and one footer')
    for container in primary+footer:
        hrefs={n['attrs'].get('href') for n in doc.select('a') if container in n['parents']}
        check(all(('/'+s+'/' if s else '/') in hrefs for s in SLUGS),f'{route}: complete nav/footer')
    if slug:
        check(bool(doc.select('nav',**{'aria-label':'Breadcrumb'})),f'{route}: breadcrumb')
        contextual={n['attrs'].get('href') for n in doc.select('a') if article in n['parents'] and n['attrs'].get('href','').startswith('/')}
        check('/' in contextual and len(contextual)>=2,f'{route}: contextual links')
    schemas=[]
    for n in doc.select('script',type='application/ld+json'):
        try:
            data=json.loads(n['text']); schemas.extend(data if isinstance(data,list) else [data])
        except json.JSONDecodeError: check(False,f'{route}: invalid JSON-LD')
    types=[s.get('@type') for s in schemas]
    check(len(types)==len(set(types)),f'{route}: duplicate schema types')
    check('WebPage' in types and 'FAQPage' in types,f'{route}: page and FAQ schema')
    fs=next((s for s in schemas if s.get('@type')=='FAQPage'),{})
    expected=[(f['question'],f['answer']) for f in page['faq']]
    got=[(f.get('name'),f.get('acceptedAnswer',{}).get('text')) for f in fs.get('mainEntity',[])]
    check(got==expected, f'{route}: FAQ schema matches content')
    for q,a in expected: check(clean(q) in article_text and clean(a) in article_text,f'{route}: visible FAQ')
    if slug: check('BreadcrumbList' in types,f'{route}: breadcrumb schema')
    if page.get('howToSectionId'):
        steps=next(s['steps'] for s in page['sections'] if s['id']==page['howToSectionId'])
        hs=next((s for s in schemas if s.get('@type')=='HowTo'),{})
        check([(s.get('name'),s.get('text')) for s in hs.get('step',[])]==[(s['heading'],s['description']) for s in steps],f'{route}: exact HowTo steps')
    else: check('HowTo' not in types,f'{route}: unnecessary HowTo')
    serialized=json.dumps(schemas)
    check(not re.search(r'aggregateRating|reviewRating|"price"',serialized),f'{route}: unsupported schema fields')
    check(len([n for n in doc.select('script') if 'googletagmanager.com/gtag/js?id=G-74EDZXS288' in n['attrs'].get('src','')])==1,f'{route}: GA loader once')
    analytics_scripts=[n for n in doc.select('script') if re.match(r'\s*window\.dataLayer',n['text'])]
    check(len(analytics_scripts)==1 and len(re.findall(r"gtag\('config',\s*'G-74EDZXS288'",analytics_scripts[0]['text']))==1,f'{route}: GA config once')
    text=visible_content(doc); words=len(re.findall(r"[A-Za-z0-9]+(?:['-][A-Za-z0-9]+)*",text))
    check(words >= (1200 if not slug else 800),f'{route}: substantive word count {words}')
    check('nivalis nights' in text.lower(),f'{route}: core phrase')
    rows.append(dict(url=canonical,words=words,title=title,titleLength=len(title),descriptionLength=len(desc),h1=len(h1),h2=len(doc.select('h2')),schemaTypes=types))

# Every published route, anchor, and local image/font/stylesheet/script must resolve.
for path in OUT.rglob('*.html'):
    # The isolated official banner documents are ad resources, not site pages.
    if path.parent == OUT/'adsterra': continue
    doc=Document(path.read_text())
    check(len(doc.select('main'))==1,f'{path.relative_to(OUT)}: one main landmark')
    check(len(doc.select('footer'))==1,f'{path.relative_to(OUT)}: footer present')
    ids=[n['attrs']['id'] for n in doc.nodes if 'id' in n['attrs']]
    check(len(ids)==len(set(ids)),f'{path.relative_to(OUT)}: duplicate IDs')
    for n in doc.nodes:
        target=n['attrs'].get('href') if n['tag'] in ['a','link'] else n['attrs'].get('src') if n['tag'] in ['img','script'] else None
        if not target: continue
        url=urlsplit(target)
        if url.scheme or url.netloc: continue
        if not url.path:
            if url.fragment: check(unquote(url.fragment) in ids,f'{path.relative_to(OUT)}: broken anchor {target}')
            continue
        resolved=OUT/url.path.lstrip('/') if url.path.startswith('/') else path.parent/url.path
        if resolved.is_dir(): resolved=resolved/'index.html'
        check(resolved.exists(), f'{path.relative_to(OUT)}: missing local resource {target}')
        if resolved.exists() and url.fragment and resolved.suffix=='.html':
            target_doc=Document(resolved.read_text())
            check(any(x['attrs'].get('id')==unquote(url.fragment) for x in target_doc.nodes),f'{path.relative_to(OUT)}: missing destination anchor')
        if n['tag']=='img': check('alt' in n['attrs'],f'{path.relative_to(OUT)}: image alt missing')

sitemap=(OUT/'sitemap.xml').read_text()
check(re.findall(r'<loc>(.*?)</loc>',sitemap)==[SITE+(s+'/' if s else '') for s in SLUGS], 'Sitemap must contain precisely the six core URLs')
robots=(OUT/'robots.txt').read_text()
check(('Disallow: /' in robots) if args.prelaunch else ('Allow: /' in robots and 'Disallow: /' not in robots),'Robots launch gate')
check(f'Sitemap: {SITE}sitemap.xml' in robots,'Robots sitemap address')
for slug in LEGAL: check((OUT/slug/'index.html').exists(),f'Missing retained legal page: {slug}')
check((OUT/'404.html').exists(),'Missing static 404')
if (OUT/'404.html').exists(): check('noindex' in (OUT/'404.html').read_text(),'404 must remain noindex')
manifest=json.loads((OUT/'manifest.webmanifest').read_text())
check(manifest['icons'][0]['type']=='image/jpeg','Manifest icon MIME')
check(manifest['icons'][0]['sizes']=='256x256','Manifest icon dimensions')
check(manifest['start_url']=='/','Manifest root URL')
check('codes' not in (OUT/'images/nivalis-nights-og.svg').read_text().lower(),'OG subtitle residue')

# Scan full first-party source and all exported textual assets without printing matched values.
secret_patterns={
 'private key':r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
 'GitHub credential':r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,})\b',
 'API credential':r'\bsk-(?:proj-)?[A-Za-z0-9_-]{30,}\b',
 'AWS credential':r'\bAKIA[A-Z0-9]{16}\b',
 'assigned credential':r'(?i)(?:api[_-]?key|client[_-]?secret|password|access[_-]?token)\s*[=:]\s*["\x27][A-Za-z0-9_+/=-]{20,}["\x27]'
}
public_residue=re.compile(r"Yorich|Fact Pack|Evidence ID|Generated by|Codex|Claude|ChatGPT|OpenAI|SEO audit|SERP|keyword volume|Drag.?n.?Wash|lorem ipsum|sample data|test@example|owner/repo|\bTODO\b|\bTBD\b",re.I)
public_locations=re.compile(r'localhost|127\.0\.0\.1|/Users/|/private/tmp|[A-Z]:\\\\Users\\\\',re.I)
text_extensions={'.html','.js','.css','.json','.svg','.txt','.xml','.webmanifest','.tsx','.ts','.mjs','.md','.yml','.yaml'}
for base in [ROOT,OUT]:
    for file in base.rglob('*'):
        rel=file.relative_to(base)
        if not file.is_file(): continue
        if base==ROOT and any(p in ['node_modules','.next','out','.git','output'] for p in rel.parts): continue
        if file.name.startswith('.env') and file.name!='.env.example': check(False,f'Unpublished environment file requires review: {rel}')
        if file==Path(__file__).resolve(): continue
        text=file.read_text(errors='ignore')
        for label,pattern in secret_patterns.items(): check(not re.search(pattern,text),f'Secret scan: {label} in {rel}')
        if file.suffix not in text_extensions: continue
        if base==OUT:
            check(not public_residue.search(text),f'Public residue in {rel}')
            # The standard URL polyfill normalizes a file URL's localhost host to empty.
            # It is a parser rule, not an endpoint. No other development locations pass.
            location_text=text
            if str(rel).startswith('_next/static/chunks/polyfills-'):
                location_text=location_text.replace('"localhost"===s.host&&(s.host="")','')
            check(not public_locations.search(location_text),f'Public development location in {rel}')
        elif file.suffix in ['.json','.tsx','.ts','.svg','.md']:
            check(not public_residue.search(text),f'First-party source residue in {rel}')
check(json.loads((ROOT/'content/generated/integrations.json').read_text())['gaMeasurementId']=='G-74EDZXS288','Original GA4 ID retained')

report=dict(mode='prelaunch' if args.prelaunch else 'launch',status='FAIL' if FAILURES else 'PASS',pages=rows,failures=FAILURES,security='No credential patterns detected' if not any('Secret scan' in x for x in FAILURES) else 'Review required')
(ROOT/'output').mkdir(exist_ok=True)
(ROOT/'output/qa-report.json').write_text(json.dumps(report,indent=2)+'\n')
for row in rows: print(f"{row['url']} | words={row['words']} | title={row['titleLength']} | description={row['descriptionLength']}")
for failure in FAILURES: print('FAIL:',failure)
print(f"Static QA: {report['status']} ({len(FAILURES)} failures)")
raise SystemExit(bool(FAILURES))
