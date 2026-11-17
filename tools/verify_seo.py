import glob, json, os, re, sys

root = sys.argv[1]
files = sorted(glob.glob(os.path.join(root, '**', '*.html'), recursive=True))
problems = []
pages = [f for f in files if not f.endswith('404.html')]

for f in files:
    h = open(f, encoding='utf-8').read()
    rel = os.path.relpath(f, root)
    if h.count('<link rel="canonical"') != 1:
        problems.append(rel + ': canonical != 1')
    if h.count('<h1') != 1:
        problems.append(rel + ': h1 != 1')
    if 'lang="es-CO"' not in h:
        problems.append(rel + ': lang')
    if 'property="og:image"' not in h or 'og:image:width' not in h:
        problems.append(rel + ': og:image incompleta')
    if not re.search(r'<meta name="description" content=".{70,162}">', h):
        problems.append(rel + ': meta description fuera de rango')
    tm = re.search(r'<title>(.*?)</title>', h)
    if not tm or not (20 <= len(tm.group(1)) <= 63):
        problems.append(rel + ': title fuera de rango')
    for m in re.finditer(r'<img[^>]*>', h):
        tag = m.group(0)
        if 'alt=' not in tag:
            problems.append(rel + ': img sin alt')
        if 'width=' not in tag or 'height=' not in tag:
            problems.append(rel + ': img sin dimensiones -> ' + tag[:60])
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
        try:
            json.loads(m.group(1))
        except Exception as e:
            problems.append(rel + ': JSON-LD invalido (' + str(e) + ')')

sm = open(os.path.join(root, 'sitemap.xml'), encoding='utf-8').read()
locs = re.findall(r'<loc>(.*?)</loc>', sm)
if len(locs) != len(pages):
    problems.append('sitemap: %d urls vs %d paginas' % (len(locs), len(pages)))
if 'servicios/estructural.html' not in sm:
    problems.append('sitemap: falta estructural')
if '404' in sm:
    problems.append('sitemap: incluye 404')

home = open(os.path.join(root, 'index.html'), encoding='utf-8').read()
for token in ['brand-mark-96.png', 'preload" as="image"', 'fetchpriority="high"',
              'preload="none"', 'hasOfferCatalog', 'knowsAbout', 'contactPoint',
              '8 servicios', 'servicios/estructural.html',
              'zonas/bosa.html', 'zonas/soacha.html', 'localidad 7']:
    if token not in home:
        problems.append('index.html: falta ' + token)

# --- indexabilidad, Open Graph, breadcrumbs y titulos unicos ---
titles = {}
for f in files:
    h = open(f, encoding='utf-8').read()
    rel = os.path.relpath(f, root)
    tm = re.search(r'<title>(.*?)</title>', h)
    t = tm.group(1).strip() if tm else ''
    if not t:
        problems.append(rel + ': sin title')
    elif t in titles:
        problems.append('title duplicado: %s (%s y %s)' % (t, titles[t], rel))
    else:
        titles[t] = rel
    if 'property="og:title"' not in h or 'property="og:url"' not in h:
        problems.append(rel + ': falta og:title u og:url')
    if f.endswith('404.html'):
        if 'noindex' not in h:
            problems.append(rel + ': 404 sin noindex')
    elif 'noindex' in h:
        problems.append(rel + ': no deberia ser noindex')
    if rel.replace(os.sep, '/') not in ('index.html', '404.html'):
        if 'BreadcrumbList' not in h:
            problems.append(rel + ': sin BreadcrumbList')

if os.path.isdir(os.path.join(root, 'admin')):
    problems.append('admin/ no debe publicarse')

# --- paginas locales: contenido propio y presencia en sitemap ---
zonas = {
    'zonas/bosa.html': ['localidad 7', 'reconocimiento de edificaci', 'segundos pisos', 'bogot'],
    'zonas/soacha.html': ['cundinamarca', 'legalizaci', 'la norma que aplica es la de soacha'],
}
for page, tokens in zonas.items():
    p = os.path.join(root, *page.split('/'))
    if not os.path.exists(p):
        problems.append('falta la pagina local ' + page)
        continue
    zone_html = open(p, encoding='utf-8').read().lower()
    for tok in tokens:
        if tok not in zone_html:
            problems.append(page + ': falta contenido sobre "' + tok + '"')
    if page not in sm:
        problems.append('sitemap: falta ' + page)

print('HTML pages: %d | sitemap urls: %d' % (len(files), len(locs)))
print('Service pages: %d' % len(glob.glob(os.path.join(root, 'servicios', '*.html'))))
print('Problems: %d' % len(problems))
for p in problems:
    print(' - ' + p)
