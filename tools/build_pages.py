# -*- coding: utf-8 -*-
"""
Genera las paginas HTML estaticas de arqtwan.com a partir de data/content.js.

Uso (desde la raiz del proyecto):
    python tools/build_pages.py

Genera:
    index.html
    servicios/<slug>.html   (una por servicio)
    proyectos.html
    contacto.html
    privacidad.html
    404.html

Cualquier cambio manual en esos HTML se pierde al volver a ejecutar el
script: edita data/content.js o este generador.
"""

import argparse
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "content.js"
OUT_DIR = None

BRAND_FALLBACK = "Arqtwan"


def seo_override(data, key, slug=None):
    """Devuelve (titulo, descripcion) definidos en data['seo'], o (None, None)."""
    seo = data.get("seo") or {}
    node = seo.get(key) or {}
    if slug is not None:
        node = (node or {}).get(slug) or {}
    if not isinstance(node, dict):
        return None, None
    return (node.get("title") or None), (node.get("description") or None)


def seo_for(data, key, title, description, slug=None):
    """Aplica los textos SEO editables sobre los valores por defecto."""
    custom_title, custom_description = seo_override(data, key, slug)
    return (custom_title or title), (custom_description or description)


def load_content():
    raw = DATA_FILE.read_text(encoding="utf-8")
    raw = re.sub(r"^[\s\S]*?window\.ARQTWAN\s*=\s*", "", raw)
    raw = re.sub(r";\s*$", "", raw.strip())
    return json.loads(raw)


def esc(value):
    return html.escape(str(value), quote=True)


def abs_url(site, path=""):
    base = (site.get("url") or "https://arqtwan.com").rstrip("/")
    if path and re.match(r"^https?://", path):
        return path
    return base + "/" + path.lstrip("/") if path else base + "/"


def wa_link(site, message=""):
    phone = re.sub(r"[^\d]", "", site.get("whatsapp", ""))
    from urllib.parse import quote

    return "https://wa.me/%s?text=%s" % (phone, quote(message))


def jsonld_block(data):
    return (
        '<script type="application/ld+json">\n'
        + json.dumps(data, ensure_ascii=False, indent=2)
        + "\n</script>"
    )


def head(ctx):
    """ctx: dict con title, description, path, rel, jsonld, og_type, image"""
    site = ctx["site"]
    rel = ctx["rel"]
    url = abs_url(site, ctx["path"])
    image = abs_url(site, ctx.get("image") or site.get("ogImage", "assets/img/og-arqtwan.jpg"))
    title = ctx["title"]
    desc = ctx["description"]

    return """<!DOCTYPE html>
<html lang="es" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta name="google-site-verification" content="o0HdO8HkEtZiGqGIS2KYd91j7IE8fGOWgMSSIqJjJbg">
<meta name="robots" content="{robots}">
<meta name="theme-color" content="#071C27">
<meta name="author" content="Arqtwan">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Arqtwan">
<meta property="og:locale" content="es_CO">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{image}">
<meta property="og:image:alt" content="Arqtwan · arquitectura, ingeniería y construcción">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{image}">
<link rel="icon" href="{rel}favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="{rel}assets/icons/favicon-32.png">
<link rel="apple-touch-icon" href="{rel}assets/icons/apple-touch-icon.png">
<link rel="manifest" href="{rel}site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Montserrat:wght@500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{rel}styles.css">
{jsonld}
</head>
""".format(
        title=esc(title),
        desc=esc(desc),
        url=esc(url),
        image=esc(image),
        og_type=ctx.get("og_type", "website"),
        robots=ctx.get("robots", "index, follow, max-image-preview:large"),
        rel=rel,
        jsonld=jsonld_block(ctx["jsonld"]) if ctx.get("jsonld") else "",
    )

def brand_mark(rel, size=38):
    return (
        '<img class="brand-mark" src="{rel}assets/icons/icon-512.png" alt="" '
        'width="{s}" height="{s}" decoding="async">'
    ).format(rel=rel, s=size)


def header(ctx):
    rel = ctx["rel"]
    services = ctx["services"]
    current = ctx.get("current", "")

    def curr(key):
        return ' aria-current="page"' if current == key else ""

    submenu = "\n".join(
        '          <li><a href="{rel}servicios/{slug}.html">{name}<small>{short}</small></a></li>'.format(
            rel=rel,
            slug=s["slug"],
            name=esc(s["name"]),
            short=esc(shorten(s.get("short", ""), 62)),
        )
        for s in services
    )

    return """<header class="site-header" data-header>
  <div class="header-inner">
    <a class="brand" href="{rel}index.html" aria-label="Arqtwan · inicio">
      {mark}
      <span class="brand-text"><strong>Arqtwan</strong><span>Arquitectura · Ingeniería</span></span>
    </a>
    <button class="nav-toggle" type="button" data-nav-toggle aria-expanded="false" aria-controls="site-nav" aria-label="Abrir menú de navegación"><span></span></button>
    <nav class="nav" id="site-nav" data-nav aria-label="Navegación principal">
      <ul class="nav-list">
        <li><a class="nav-link" href="{rel}index.html"{c_home}>Inicio</a></li>
        <li class="nav-item--menu" data-submenu>
          <button class="nav-link nav-toggle-menu" type="button" aria-expanded="false" aria-controls="menu-servicios">Servicios</button>
          <ul class="nav-submenu" id="menu-servicios">
{submenu}
          </ul>
        </li>
        <li><a class="nav-link" href="{rel}proyectos.html"{c_proy}>Proyectos</a></li>
        <li><a class="nav-link" href="{rel}contacto.html"{c_cont}>Contacto</a></li>
      </ul>
    </nav>
    <div class="header-actions">
      <a class="btn btn--primary btn--sm header-cta" href="{rel}contacto.html">Cotizar proyecto</a>
    </div>
  </div>
</header>
""".format(
        rel=rel,
        mark=brand_mark(rel),
        submenu=submenu,
        c_home=curr("home"),
        c_proy=curr("proyectos"),
        c_cont=curr("contacto"),
    )



def footer(ctx):
    site = ctx["site"]
    rel = ctx["rel"]
    phone = site.get("whatsappDisplay", "")
    href = wa_link(site, "Hola Arqtwan, quiero información sobre un proyecto.")

    service_links = "\n".join(
        '          <li><a href="{rel}servicios/{slug}.html">{name}</a></li>'.format(
            rel=rel, slug=s["slug"], name=esc(s["name"])
        )
        for s in ctx["services"]
    )

    return """<footer class="site-footer">
  <div class="container">
    <div class="footer-top">
      <div class="footer-brand">
        <a class="brand" href="{rel}index.html" aria-label="Arqtwan · inicio">
          {mark}
          <span class="brand-text"><strong>Arqtwan</strong><span>Arquitectura · Ingeniería</span></span>
        </a>
        <p>Diseño arquitectónico, ingeniería y construcción con criterio técnico. Acompañamos proyectos de vivienda, comercio y obra en Colombia.</p>
      </div>
      <div>
        <h2 class="footer-title">Servicios</h2>
        <ul class="footer-links">
{services}
        </ul>
      </div>
      <div>
        <h2 class="footer-title">Sitio</h2>
        <ul class="footer-links">
          <li><a href="{rel}index.html">Inicio</a></li>
          <li><a href="{rel}proyectos.html">Proyectos</a></li>
          <li><a href="{rel}contacto.html">Contacto</a></li>
          <li><a href="{rel}privacidad.html">Política de privacidad</a></li>
        </ul>
      </div>
      <div>
        <h2 class="footer-title">Contacto</h2>
        <ul class="footer-contact">
          <li><strong>WhatsApp</strong><a href="{wa}" data-wa="Hola Arqtwan, quiero información sobre un proyecto." data-wa-origen="footer" target="_blank" rel="noopener">{phone}</a></li>
          <li><strong>Horario</strong>{hours}</li>
          <li><strong>Cobertura</strong>{area}</li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <p>© <span data-year>2026</span> Arqtwan. Todos los derechos reservados.</p>
      <div class="footer-legal">
        <a href="{rel}privacidad.html">Privacidad</a>
        <span>Proyectos en Colombia</span>
      </div>
    </div>
  </div>
</footer>
""".format(
        rel=rel,
        mark=brand_mark(rel, 40),
        services=service_links,
        wa=esc(href),
        phone=esc(phone),
        hours=esc(site.get("hours", "")),
        area=esc(site.get("serviceArea", "")),
    )


def floats(ctx):
    wa_href = wa_link(ctx["site"], "Hola Arqtwan, quiero cotizar un proyecto.")
    return """
<a class="wa-float" data-wa="Hola Arqtwan, quiero cotizar un proyecto." data-wa-origen="flotante" href="{wa}" target="_blank" rel="noopener" aria-label="Escribir a Arqtwan por WhatsApp">
  <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2 22l5.25-1.38c1.45.79 3.08 1.21 4.79 1.21 5.46 0 9.91-4.45 9.91-9.91C21.95 6.45 17.5 2 12.04 2zm0 18.15c-1.48 0-2.93-.4-4.2-1.15l-.3-.18-3.12.82.83-3.04-.2-.31a8.26 8.26 0 0 1-1.26-4.38c0-4.54 3.7-8.24 8.25-8.24 4.54 0 8.24 3.7 8.24 8.24 0 4.55-3.7 8.24-8.24 8.24zm4.52-6.16c-.25-.12-1.47-.72-1.7-.8-.23-.09-.4-.13-.56.12-.17.25-.64.8-.79.97-.15.17-.29.19-.54.06-.25-.12-1.05-.39-2-1.23-.74-.66-1.24-1.47-1.38-1.72-.15-.25-.02-.39.11-.51.11-.11.25-.29.37-.44.12-.15.17-.25.25-.42.08-.17.04-.31-.02-.44-.06-.12-.56-1.35-.77-1.85-.2-.48-.41-.42-.56-.43h-.48c-.17 0-.44.06-.67.31-.23.25-.87.85-.87 2.07 0 1.22.89 2.4 1.01 2.57.12.17 1.75 2.67 4.23 3.74.59.26 1.05.41 1.41.52.59.19 1.13.16 1.56.1.48-.07 1.47-.6 1.68-1.18.21-.58.21-1.07.15-1.18-.06-.11-.23-.17-.48-.29z"/></svg>
  <span>WhatsApp</span>
</a>
<button class="back-to-top" data-back-top type="button" aria-label="Volver al inicio de la página"></button>
""".format(wa=esc(wa_href))


def page(ctx, body, page_class=""):
    rel = ctx["rel"]
    return (
        head(ctx)
        + '<body class="has-float{pc}">\n'.format(
            pc=(" " + page_class) if page_class else ""
        )
        + '<a class="skip-link" href="#main">Saltar al contenido</a>\n'
        + header(ctx)
        + '<main id="main">\n'
        + body
        + "\n</main>\n"
        + footer(ctx)
        + floats(ctx)
        + '\n<script src="{rel}data/content.js" defer></script>\n'.format(rel=rel)
        + '<script src="{rel}script.js" defer></script>\n'.format(rel=rel)
        + "</body>\n</html>\n"
    )


def shorten(text, limit=90):
    text = re.sub(r"\s+", " ", str(text)).strip()
    if len(text) <= limit:
        return text
    cut = text[: limit - 1]
    if " " in cut.strip():
        cut = cut[: cut.rstrip().rfind(" ")]
    return cut.rstrip(" ,;:.-") + "…"


def stats_block(site):
    years = site.get("experienceYears", "10")
    items = [
        (years + " años", "de experiencia acumulada entre diseño, trámites y obra."),
        ("7 servicios", "integrados: del expediente de licencia a la entrega de obra."),
        ("1 solo equipo", "arquitectura, ingeniería y construcción coordinadas."),
        ("Colombia", "atención de proyectos residenciales y comerciales."),
    ]
    cells = "\n".join(
        '        <div class="reveal"><span class="stat__value">{v}</span>'
        '<span class="stat__label">{l}</span></div>'.format(v=esc(v), l=esc(l))
        for v, l in items
    )
    return (
        '<section class="stat-strip" aria-label="Arqtwan en cifras">\n'
        '  <div class="container">\n'
        '    <div class="stat-strip__inner">\n'
        + cells
        + "\n    </div>\n  </div>\n</section>"
    )


def service_cards(rel, services, limit=None, wide_first=False):
    cards = []
    for i, s in enumerate(services if limit is None else services[:limit], start=1):
        cls = "service-card reveal" + (" service-card--wide" if wide_first and i == 1 else "")
        url = "{rel}servicios/{slug}.html".format(rel=rel, slug=s["slug"])
        cards.append(
            """      <article class="{cls}" style="--reveal-delay:{delay}ms">
        <a class="service-card__media" href="{url}" tabindex="-1" aria-hidden="true">
          <span class="service-card__index">{idx:02d}</span>
          <img src="{rel}{plate}" alt="" loading="lazy" width="800" height="500" decoding="async">
        </a>
        <div class="service-card__body">
          <h3><a href="{url}">{name}</a></h3>
          <p class="service-card__text">{short}</p>
          <a class="link-arrow service-card__link" href="{url}">Ver servicio</a>
        </div>
      </article>""".format(
                cls=cls,
                delay=min(i - 1, 5) * 60,
                url=url,
                idx=i,
                rel=rel,
                plate=esc(s.get("plate", "")),
                name=esc(s["name"]),
                short=esc(s.get("short", "")),
            )
        )
    return "\n".join(cards)


def hero_home(ctx):
    site = ctx["site"]
    rel = ctx["rel"]
    years = esc(site.get("experienceYears", "10"))
    hero = site.get("hero") or {}
    kicker = esc(hero.get("kicker") or "Arquitectura · Ingeniería · Construcción")
    title = esc(hero.get("title") or "Proyectos que se construyen con criterio técnico")
    em = esc(hero.get("titleEm") or "criterio técnico")
    if em and em in title:
        title = title.replace(em, "<em>" + em + "</em>", 1)
    lede = esc(
        hero.get("lede")
        or "Diseñamos, tramitamos y construimos con un solo equipo. Revisamos la norma "
        "antes de dibujar, calculamos antes de comprar material y documentamos cada "
        "decisión para que tu obra avance sin sorpresas evitables."
    )
    return """<section class="hero" aria-labelledby="hero-title">
  <div class="hero__media">
    <video autoplay muted loop playsinline preload="metadata" poster="{rel}assets/img/hero-poster.jpg" aria-hidden="true" tabindex="-1">
      <source src="{rel}assets/video/hero.mp4" type="video/mp4">
    </video>
  </div>
  <div class="hero__scrim"></div>
  <div class="hero__grain"></div>
  <div class="hero__inner">
    <p class="hero__kicker"><span></span>{kicker}</p>
    <h1 class="hero__title" id="hero-title">{title}</h1>
    <p class="hero__lede">{lede}</p>
    <div class="hero__actions">
      <a class="btn btn--primary" href="{rel}contacto.html">Cotizar mi proyecto</a>
      <a class="btn btn--ghost" data-wa="Hola Arqtwan, quiero cotizar un proyecto." data-wa-origen="hero" href="#">Escribir por WhatsApp</a>
    </div>
    <div class="hero__meta">
      <span>{years} años de experiencia</span>
      <span>{area}</span>
      <span>{hours}</span>
    </div>
  </div>
</section>

{stats}""".format(
        rel=rel,
        kicker=kicker,
        title=title,
        lede=lede,
        years=years,
        area=esc(site.get("serviceArea", "Atención en Colombia")),
        hours=esc(site.get("hours", "")),
        stats=stats_block(site),
    )


def services_section(ctx, title=None, lede=None):
    rel = ctx["rel"]
    title = title or "Servicios para cada etapa del proyecto"
    lede = lede or (
        "Desde la consulta de viabilidad hasta la entrega de obra. Puedes contratar un "
        "servicio puntual o el acompañamiento completo."
    )
    return """<section class="section" id="servicios" aria-labelledby="servicios-title">
  <div class="container">
    <div class="section-head">
      <p class="eyebrow">Servicios</p>
      <h2 id="servicios-title">{title}</h2>
      <p class="section-lede">{lede}</p>
    </div>
    <div class="service-grid">
{cards}
    </div>
    <p class="mt-2"><a class="link-arrow" href="{rel}proyectos.html">Ver proyectos y alcances</a></p>
  </div>
</section>""".format(
        title=esc(title), lede=esc(lede), cards=service_cards(rel, ctx["services"]), rel=rel
    )


def split_section(ctx):
    rel = ctx["rel"]
    return """<section class="section section--paper" aria-labelledby="porque-title">
  <div class="container">
    <div class="split">
      <div class="reveal">
        <p class="eyebrow">Por qué Arqtwan</p>
        <h2 id="porque-title">Un interlocutor técnico, no tres proveedores sueltos</h2>
        <p class="section-lede">Cuando el arquitecto, el ingeniero y el constructor no hablan entre sí, los errores aparecen en obra: cambios de última hora, sobrecostos y trámites que se devuelven. En Arqtwan coordinamos las tres partes sobre el mismo expediente.</p>
        <ul class="checklist mt-2">
          <li>Revisión normativa antes de invertir en diseño.</li>
          <li>Planos, memorias y presupuesto con el mismo criterio.</li>
          <li>Documentación ordenada para la autoridad y para la obra.</li>
          <li>Decisiones explicadas en lenguaje claro, sin tecnicismos innecesarios.</li>
        </ul>
        <p class="plate-note">Trabajamos con contratistas aliados y profesionales habilitados según el alcance de cada proyecto.</p>
      </div>
      <div class="split__media reveal">
        <figure class="figure mb-0">
          <img src="{rel}assets/img/plate-arquitectura.svg" alt="Lámina técnica ilustrativa de Arqtwan con plantas y detalles constructivos" width="1200" height="900" loading="lazy" decoding="async">
          <figcaption class="figure__caption"><span>Imagen ilustrativa</span><span>No corresponde a un proyecto ejecutado</span></figcaption>
        </figure>
      </div>
    </div>
  </div>
</section>""".format(rel=rel)


def process_section(ctx, steps=None, title="Cómo trabajamos"):
    steps = steps or [
        {
            "title": "Diagnóstico",
            "text": "Revisamos el predio, la norma aplicable y tu objetivo real de inversión.",
        },
        {
            "title": "Propuesta",
            "text": "Definimos alcance, entregables, tiempos y costo antes de empezar.",
        },
        {
            "title": "Desarrollo",
            "text": "Producimos planos, memorias, presupuesto y el expediente que haga falta.",
        },
        {
            "title": "Obra y cierre",
            "text": "Acompañamos la ejecución, resolvemos imprevistos y documentamos la entrega.",
        },
    ]
    cells = "\n".join(
        '      <div class="process__step reveal"><h3>{t}</h3><p>{x}</p></div>'.format(
            t=esc(s["title"]), x=esc(s["text"])
        )
        for s in steps
    )
    return """<section class="section section--ink" aria-labelledby="proceso-title">
  <div class="container">
    <div class="section-head">
      <p class="eyebrow">Proceso</p>
      <h2 id="proceso-title">{title}</h2>
      <p class="section-lede">Un método de trabajo simple, con hitos verificables y sin promesas que no podamos sostener.</p>
    </div>
    <div class="process">
{cells}
    </div>
  </div>
</section>""".format(title=esc(title), cells=cells)


def faq_section(ctx, items, title="Preguntas frecuentes", lede=None, section_class="section"):
    lede = lede or "Respuestas directas a lo que más nos preguntan antes de contratar."
    rows = "\n".join(
        """      <details class="faq__item">
        <summary>{q}</summary>
        <div class="faq__answer"><p>{a}</p></div>
      </details>""".format(q=esc(item["q"]), a=esc(item["a"]))
        for item in items
    )
    return """<section class="{sc}" aria-labelledby="faq-title">
  <div class="container container--narrow">
    <div class="section-head">
      <p class="eyebrow">Dudas frecuentes</p>
      <h2 id="faq-title">{title}</h2>
      <p class="section-lede">{lede}</p>
    </div>
    <div class="faq" data-faq>
{rows}
    </div>
    <p class="mt-2"><a class="link-arrow" href="{rel}contacto.html">Hacer otra pregunta</a></p>
  </div>
</section>""".format(
        sc=section_class, title=esc(title), lede=esc(lede), rows=rows, rel=ctx["rel"]
    )


def cta_band(ctx, title="¿Tienes un predio, un plano o una idea?", text=None):
    rel = ctx["rel"]
    text = text or (
        "Cuéntanos en qué etapa estás y te decimos qué conviene revisar primero, "
        "sin compromiso y sin tecnicismos innecesarios."
    )
    return """<section class="cta-band" aria-labelledby="cta-title">
  <div class="container">
    <div class="cta-band__inner">
      <div class="reveal">
        <h2 id="cta-title">{title}</h2>
        <p>{text}</p>
      </div>
      <div class="cta-band__actions reveal">
        <a class="btn btn--primary" href="{rel}contacto.html">Cotizar proyecto</a>
        <a class="btn btn--light" data-wa="Hola Arqtwan, quiero cotizar un proyecto." data-wa-origen="cta" href="#">WhatsApp</a>
      </div>
    </div>
  </div>
</section>""".format(title=esc(title), text=esc(text), rel=rel)


def quote_form(ctx, dark=False):
    rel = ctx["rel"]
    options = "\n".join(
        '            <option value="{n}">{n}</option>'.format(n=esc(s["name"]))
        for s in ctx["services"]
    )
    card_cls = "form-card form-card--dark" if dark else "form-card"
    return """<form class="{card}" data-quote-form>
  <div class="form">
    <div class="form__row">
      <div class="field">
        <label for="qf-nombre">Nombre <span class="req">*</span></label>
        <input class="input" id="qf-nombre" name="nombre" type="text" autocomplete="name" required>
      </div>
      <div class="field">
        <label for="qf-telefono">Teléfono / WhatsApp <span class="req">*</span></label>
        <input class="input" id="qf-telefono" name="telefono" type="tel" inputmode="tel" autocomplete="tel" required>
      </div>
    </div>
    <div class="form__row">
      <div class="field">
        <label for="qf-ciudad">Ciudad o municipio</label>
        <input class="input" id="qf-ciudad" name="ciudad" type="text" autocomplete="address-level2">
      </div>
      <div class="field">
        <label for="qf-servicio">Servicio de interés</label>
        <select class="select" id="qf-servicio" name="servicio">
          <option value="">Aún no lo sé</option>
{options}
        </select>
      </div>
    </div>
    <div class="field">
      <label for="qf-mensaje">Cuéntanos del proyecto</label>
      <textarea class="textarea" id="qf-mensaje" name="mensaje" placeholder="Tipo de proyecto, área aproximada, etapa actual, ubicación…"></textarea>
    </div>
    <div class="field">
      <label for="qf-acepto" style="text-transform:none;letter-spacing:0;font-family:var(--font-body);font-size:0.82rem;font-weight:400;color:var(--text-soft)">
        <input type="checkbox" id="qf-acepto" name="acepto" required>
        Acepto que mis datos se usen únicamente para responder esta solicitud. <a href="{rel}privacidad.html">Política de privacidad</a>.
      </label>
    </div>
    <button class="btn btn--primary btn--block" type="submit">Enviar por WhatsApp</button>
    <p class="form__status" data-form-status role="status" aria-live="polite"></p>
    <a class="link-arrow" data-form-fallback href="#" hidden>Abrir WhatsApp manualmente</a>
    <p class="form__note">Al enviar se abre WhatsApp con tu solicitud escrita. No guardamos tus datos en este sitio ni usamos el formulario para enviar correos automáticos.</p>
  </div>
</form>""".format(
        card=card_cls, options=options, rel=rel
    )


HOME_FAQ = [
    {
        "q": "¿Trabajan en cualquier ciudad de Colombia?",
        "a": "Atendemos proyectos en distintas regiones del país y coordinamos visitas según la ubicación. Cuéntanos dónde está el predio y confirmamos la viabilidad de acompañarte antes de cualquier compromiso.",
    },
    {
        "q": "¿Puedo contratar solo el diseño y construir por mi cuenta?",
        "a": "Sí. Puedes contratar el alcance que necesites: diseño, trámite, presupuesto o acompañamiento de obra. Si decides construir con otro equipo, entregamos la documentación ordenada para que la obra pueda ejecutarse sin interpretaciones.",
    },
    {
        "q": "¿Cuánto cuesta un proyecto?",
        "a": "Depende del alcance, el área, la complejidad estructural y el estado del expediente. Después de revisar tu caso entregamos una propuesta con entregables y valores definidos, sin costos escondidos.",
    },
    {
        "q": "¿Garantizan la aprobación de una licencia?",
        "a": "No. La decisión es de la autoridad competente y depende de la norma, del predio y del expediente. Nuestro trabajo es reducir el riesgo técnico y documental, responder requerimientos y acompañarte hasta la decisión.",
    },
    {
        "q": "¿Cómo se manejan los pagos y los tiempos?",
        "a": "Trabajamos con pagos por etapas asociados a entregables verificables. Los tiempos se definen en la propuesta según el alcance y los plazos de las autoridades cuando hay trámite de por medio.",
    },
]


def form_section(ctx):
    return """<section class="section section--paper" id="cotizar" aria-labelledby="cotiza-title">
  <div class="container">
    <div class="split">
      <div class="reveal">
        <p class="eyebrow">Cotización</p>
        <h2 id="cotiza-title">Cuéntanos qué tienes en mente</h2>
        <p class="section-lede">Con unos datos básicos podemos decirte qué revisar primero y qué tipo de acompañamiento necesita tu proyecto.</p>
        <ul class="checklist mt-2">
          <li>Respuesta por WhatsApp, sin formularios eternos.</li>
          <li>Un primer diagnóstico honesto: si no somos la mejor opción, lo decimos.</li>
          <li>Propuesta con alcance, entregables y valores por escrito.</li>
        </ul>
      </div>
      <div class="reveal">
        {form}
      </div>
    </div>
  </div>
</section>""".format(form=quote_form(ctx))


def home_body(ctx):
    parts = [
        hero_home(ctx),
        services_section(ctx),
        split_section(ctx),
        process_section(ctx),
        faq_section(ctx, HOME_FAQ),
        cta_band(ctx),
        form_section(ctx),
    ]
    return "\n\n".join(parts)


def page_hero(ctx, crumbs, eyebrow, title, lede, media=None, actions=""):
    rel = ctx["rel"]
    crumb_html = "\n".join(
        '          <li><a href="{url}">{label}</a></li>'.format(url=c[1], label=esc(c[0]))
        for c in crumbs[:-1]
    )
    crumb_html += '\n          <li aria-current="page">{label}</li>'.format(
        label=esc(crumbs[-1][0])
    )
    media_html = (
        '        <div class="page-hero__media reveal">\n'
        '          <img src="{rel}{src}" alt="{alt}" width="1200" height="900" decoding="async">\n'
        "        </div>".format(rel=rel, src=esc(media["src"]), alt=esc(media["alt"]))
        if media
        else ""
    )
    return """<section class="page-hero" aria-labelledby="page-title">
  <div class="container">
    <nav aria-label="Ruta de navegación">
      <ol class="breadcrumbs">
{crumb_block}
      </ol>
    </nav>
    <div class="page-hero__grid">
      <div>
        <p class="eyebrow">{eyebrow}</p>
        <h1 id="page-title">{title}</h1>
        <p class="page-hero__lede">{lede}</p>
        <div class="page-hero__actions">
{actions}
        </div>
      </div>
{media}
    </div>
  </div>
</section>""".format(
        crumb_block=crumb_html,
        eyebrow=esc(eyebrow),
        title=esc(title),
        lede=esc(lede),
        actions=actions.strip(),
        media=media_html,
    )


def service_index(ctx, current=None, title="Servicios relacionados"):
    rows = []
    for i, s in enumerate(ctx["services"], start=1):
        if current and s["slug"] == current:
            continue
        rows.append(
            '      <a class="service-index__row" href="{rel}servicios/{slug}.html">'
            "<span>{idx:02d}</span><div><strong>{name}</strong>"
            "<small>{short}</small></div></a>".format(
                rel=ctx["rel"],
                slug=s["slug"],
                idx=i,
                name=esc(s["name"]),
                short=esc(shorten(s.get("short", ""), 92)),
            )
        )
    return """<section class="section" aria-labelledby="otros-title">
  <div class="container">
    <div class="section-head">
      <p class="eyebrow">Seguir explorando</p>
      <h2 id="otros-title">{title}</h2>
    </div>
    <div class="service-index">
{rows}
    </div>
  </div>
</section>""".format(title=esc(title), rows="\n".join(rows))


def service_body(ctx, s):
    rel = ctx["rel"]
    name = s["name"]
    actions = (
        '          <a class="btn btn--primary" href="{rel}contacto.html">Cotizar este servicio</a>\n'
        '          <a class="btn btn--ghost" data-wa="Hola Arqtwan, quiero información sobre {name}." '
        'data-wa-origen="servicio-{slug}" href="#">Preguntar por WhatsApp</a>'
    ).format(rel=rel, name=esc(name), slug=esc(s["slug"]))

    bullets = "\n".join(
        "          <li>{}</li>".format(esc(b)) for b in s.get("bullets", [])
    )
    deliverables = "\n".join(
        "            <li>{}</li>".format(esc(d)) for d in s.get("deliverables", [])
    )

    faq_items = service_faq(s)
    real_photo = bool(s.get("realPhoto"))
    media_alt = (
        "Fotografía de {0} realizada por Arqtwan".format(name)
        if real_photo
        else "Lámina técnica ilustrativa de " + name.lower()
    )
    plate_note = (
        "Fotografía propia de un trabajo ejecutado por Arqtwan."
        if real_photo
        else "La imagen de esta página es una lámina ilustrativa de Arqtwan y no corresponde a un proyecto ejecutado."
    )

    hero = page_hero(
        ctx,
        [
            ("Inicio", rel + "index.html"),
            ("Servicios", rel + "index.html#servicios"),
            (name, ""),
        ],
        "Servicio",
        name,
        s.get("summary", ""),
        media={"src": s.get("plate", ""), "alt": media_alt},
        actions=actions,
    )

    includes = """<section class="section" aria-labelledby="incluye-title">
  <div class="container">
    <div class="split">
      <div class="prose reveal">
        <p class="eyebrow">Alcance</p>
        <h2 id="incluye-title">Qué incluye {name}</h2>
        <p>{short}</p>
        <ul class="checklist mt-2">
{bullets}
        </ul>
        <div class="callout"><strong>Importante:</strong> ningún trámite ni aprobación está garantizado por adelantado. La decisión depende de la autoridad competente; nuestro compromiso es técnico y documental.</div>
        <p class="plate-note">{plate_note}</p>
      </div>
      <div class="reveal">
        <div class="form-card">
          <p class="eyebrow">Entregables</p>
          <h3 class="mt-0">Qué recibes</h3>
          <ul class="checklist">
{deliverables}
          </ul>
          <p class="form__note mt-2">Los entregables finales se ajustan al alcance acordado en la propuesta.</p>
          <a class="btn btn--primary btn--block mt-2" href="{rel}contacto.html">Solicitar cotización</a>
        </div>
      </div>
    </div>
  </div>
</section>""".format(
        name=esc(name),
        short=esc(s.get("short", "")),
        bullets=bullets,
        deliverables=deliverables,
        rel=rel,
        plate_note=esc(plate_note),

    )

    return "\n\n".join(
        [
            hero,
            includes,
            process_section(ctx, s.get("steps", []), "Cómo se desarrolla"),
            faq_section(ctx, faq_items, "Preguntas sobre " + name.lower().rstrip(".")),
            service_index(ctx, current=s["slug"]),
            cta_band(
                ctx,
                "¿Necesitas {}?".format(name.lower()),
                "Escríbenos con la ubicación del predio y el estado actual del proyecto. "
                "Te decimos con claridad qué se puede hacer y qué hace falta.",
            ),
        ]
    )


def project_cards(rel, projects):
    cards = []
    for i, p in enumerate(projects):
        image = p.get("image") or "assets/img/plate-arquitectura.svg"
        title = esc(p.get("title") or "Proyecto")
        sub = esc(" · ".join([str(x) for x in (p.get("type"), p.get("location"), p.get("year")) if x]))
        alt = esc(p.get("alt") or p.get("title") or "Proyecto de Arqtwan")
        desc = p.get("description") or ""
        desc_html = (
            '\n          <p class="work-card__desc">{0}</p>'.format(esc(desc)) if desc else ""
        )
        cards.append(
            '      <article class="work-card reveal" style="--reveal-delay:{delay}ms">\n'
            '        <img class="work-card__img" src="{rel}{img}" alt="{alt}" loading="lazy" '
            'width="640" height="480" decoding="async">\n'
            '        <div class="work-card__meta">\n'
            '          <h3 class="work-card__title">{title}</h3>\n'
            '          <p class="work-card__sub">{sub}</p>{desc}\n'
            "        </div>\n"
            "      </article>".format(
                delay=min(i, 5) * 60,
                rel=rel,
                img=esc(image),
                alt=alt,
                title=title,
                sub=sub,
                desc=desc_html,
            )
        )
    return "\n".join(cards)


def projects_body(ctx):
    rel = ctx["rel"]
    projects = ctx.get("projects") or []
    cards = project_cards(rel, projects)
    empty_hidden = " hidden" if projects else ""
    note_hidden = "" if projects else " hidden"
    lede = (
        "Trabajos propios, con ubicación, año y el alcance realmente contratado."
        if projects
        else "Cada ficha incluirá tipo de proyecto, ubicación, año y el alcance real contratado."
    )
    hero = page_hero(
        ctx,
        [("Inicio", rel + "index.html"), ("Proyectos", "")],
        "Portafolio",
        "Proyectos",
        "Publicamos únicamente trabajos propios y con autorización. Mientras documentamos los primeros, aquí explicamos qué puedes esperar del acompañamiento de Arqtwan.",
        actions=(
            '          <a class="btn btn--primary" href="{rel}contacto.html">Contar mi proyecto</a>\n'
            '          <a class="btn btn--ghost" href="{rel}index.html#servicios">Ver servicios</a>'
        ).format(rel=rel),
    )

    grid = """<section class="section" aria-labelledby="portafolio-title">
  <div class="container">
    <div class="section-head">
      <p class="eyebrow">Trabajo</p>
      <h2 id="portafolio-title">Proyectos y alcances</h2>
      <p class="section-lede">{lede}</p>
    </div>
    <div class="work-grid" data-projects>
{cards}
    </div>
    <div class="empty-state" data-projects-empty{empty_hidden}>
      <p class="eyebrow">Portafolio en construcción</p>
      <h2 class="mt-0">Todavía no publicamos proyectos</h2>
      <p>Estamos documentando los primeros trabajos con fotos propias, datos verificables y autorización de cada cliente. Preferimos un portafolio vacío a uno con obras que no ejecutamos.</p>
      <p class="mt-2"><a class="btn btn--primary" href="{rel}contacto.html">Hablar de tu proyecto</a></p>
    </div>
    <p class="plate-note" data-projects-note{note_hidden}>Las imágenes y fichas publicadas aquí corresponden a trabajos propios de Arqtwan y se actualizan desde el panel del sitio.</p>
  </div>
</section>""".format(rel=rel, lede=esc(lede), cards=cards, empty_hidden=empty_hidden, note_hidden=note_hidden)

    return "\n\n".join(
        [
            hero,
            grid,
            services_section(
                ctx,
                "Mientras tanto, esto es lo que hacemos",
                "Los servicios que hoy podemos ejecutar y documentar con nuestro equipo y aliados.",
            ),
            cta_band(
                ctx,
                "Tu proyecto puede ser el primero de esta lista",
                "Si estás en etapa de idea, predio o planos, conversemos antes de invertir en decisiones difíciles de revertir.",
            ),
        ]
    )


def contact_body(ctx):
    site = ctx["site"]
    rel = ctx["rel"]
    hero = page_hero(
        ctx,
        [("Inicio", rel + "index.html"), ("Contacto", "")],
        "Contacto",
        "Hablemos de tu proyecto",
        "Cuéntanos en qué etapa estás: idea, predio, planos, licencia o obra en curso. Te respondemos con un diagnóstico inicial y los siguientes pasos concretos.",
        actions=(
            '          <a class="btn btn--primary" data-wa="Hola Arqtwan, quiero información sobre un proyecto." '
            'data-wa-origen="contacto-hero" href="#">Escribir por WhatsApp</a>\n'
            '          <a class="btn btn--ghost" href="#formulario">Usar el formulario</a>'
        ),
    )

    info = """<section class="section" id="formulario" aria-labelledby="contacto-title">
  <div class="container">
    <div class="split">
      <div class="reveal">
        <p class="eyebrow">Datos de contacto</p>
        <h2 id="contacto-title">Atención directa, sin intermediarios</h2>
        <p class="section-lede">El canal más rápido es WhatsApp. Si prefieres escribir con calma, usa el formulario y llegará la misma información.</p>
        <div class="form-card mt-2">
          <p class="eyebrow">WhatsApp</p>
          <p class="mb-0"><a class="btn btn--wa btn--block" data-wa="Hola Arqtwan, quiero información sobre un proyecto." data-wa-origen="contacto" href="#">{phone}</a></p>
          <ul class="checklist mt-2">
            <li><strong>Horario:</strong> {hours}</li>
            <li><strong>Cobertura:</strong> {area}</li>
            <li><strong>Respuesta:</strong> en horario hábil, normalmente el mismo día.</li>
          </ul>
        </div>
        <div class="callout"><strong>Qué ayuda a responder más rápido:</strong> ubicación del predio, área aproximada, uso que quieres darle y si ya tienes planos, escrituras o un trámite radicado.</div>
      </div>
      <div class="reveal">
        {form}
      </div>
    </div>
  </div>
</section>""".format(
        phone=esc(site.get("whatsappDisplay", "")),
        hours=esc(site.get("hours", "")),
        area=esc(site.get("serviceArea", "")),
        form=quote_form(ctx),
    )

    return "\n\n".join(
        [
            hero,
            info,
            cta_band(
                ctx,
                "¿Prefieres que te escribamos nosotros?",
                "Déjanos tu número en el formulario y te contactamos por WhatsApp en horario hábil.",
            ),
        ]
    )


PRIVACY_SECTIONS = [
    (
        "Quién es el responsable",
        "Este sitio es operado por Arqtwan, estudio de arquitectura, ingeniería y construcción con atención de proyectos en Colombia. Para cualquier asunto relacionado con tus datos puedes escribirnos por WhatsApp al número publicado en el sitio.",
    ),
    (
        "Qué datos tratamos",
        "El formulario de cotización pide nombre, teléfono, ciudad, servicio de interés y una descripción del proyecto. Esos datos no se almacenan en este sitio: al enviar el formulario se genera un mensaje y se abre WhatsApp para que tú decidas enviarlo.",
    ),
    (
        "Para qué los usamos",
        "Usamos la información únicamente para responder tu solicitud, entender el alcance del proyecto y preparar una propuesta. No enviamos publicidad ni boletines a partir de estos datos.",
    ),
    (
        "Con quién se comparten",
        "No vendemos ni cedemos datos personales. El envío del mensaje ocurre dentro de WhatsApp, un servicio de Meta con sus propias políticas. El sitio se aloja en GitHub Pages y utiliza Google Fonts, proveedores que pueden registrar datos técnicos como la dirección IP al servir los archivos.",
    ),
    (
        "Cookies y medición",
        "Este sitio no instala cookies propias de publicidad ni de perfilamiento. Si en el futuro se activa una herramienta de analítica, se actualizará esta política y se informará en el sitio antes de recolectar datos.",
    ),
    (
        "Tus derechos",
        "Puedes solicitar el acceso, la corrección o la eliminación de la información que nos hayas compartido, así como retirar tu autorización. Escríbenos por WhatsApp indicando tu solicitud y la atenderemos en horario hábil.",
    ),
    (
        "Seguridad y conservación",
        "Conservamos la información solo durante el tiempo necesario para atender la solicitud o el proyecto contratado. Los canales de mensajería y el alojamiento aplican sus propias medidas de seguridad.",
    ),
]


def privacy_body(ctx):
    rel = ctx["rel"]
    hero = page_hero(
        ctx,
        [("Inicio", rel + "index.html"), ("Política de privacidad", "")],
        "Legal",
        "Política de privacidad",
        "Qué datos recibe Arqtwan a través de este sitio, para qué los usa y cómo puedes ejercer tus derechos.",
    )

    blocks = "\n".join(
        "      <h2>{t}</h2>\n      <p>{b}</p>".format(t=esc(t), b=esc(b))
        for t, b in PRIVACY_SECTIONS
    )

    body = """<section class="section">
  <div class="container container--narrow">
    <div class="prose">
      <p class="text-mute">Última actualización: {updated}</p>
{blocks}
      <h2>Contacto</h2>
      <p>Si tienes dudas sobre esta política o sobre el tratamiento de tu información, escríbenos por WhatsApp al <a href="{rel}contacto.html">canal de contacto</a> del sitio.</p>
      <div class="callout"><strong>Nota:</strong> esta política describe el funcionamiento actual del sitio. Si se agregan formularios, analítica o pasarelas de pago, se actualizará antes de entrar en operación.</div>
      <p class="mt-2"><a class="link-arrow" href="{rel}index.html">Volver al inicio</a></p>
    </div>
  </div>
</section>""".format(updated=esc(ctx["updated"]), blocks=blocks, rel=rel)

    return hero + "\n\n" + body


def notfound_body(ctx):
    rel = ctx["rel"]
    return """<section class="page-hero" aria-labelledby="page-title">
  <div class="container">
    <nav aria-label="Ruta de navegación">
      <ol class="breadcrumbs">
        <li><a href="{rel}index.html">Inicio</a></li>
        <li aria-current="page">Página no encontrada</li>
      </ol>
    </nav>
    <div class="page-hero__grid">
      <div>
        <p class="eyebrow">Error 404</p>
        <h1 id="page-title">Esta página no existe</h1>
        <p class="page-hero__lede">Puede que el enlace esté mal escrito o que la página se haya movido. Desde aquí puedes volver a lo importante.</p>
        <div class="page-hero__actions">
          <a class="btn btn--primary" href="{rel}index.html">Ir al inicio</a>
          <a class="btn btn--ghost" href="{rel}index.html#servicios">Ver servicios</a>
          <a class="btn btn--ghost" href="{rel}contacto.html">Contacto</a>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head">
      <p class="eyebrow">Atajos</p>
      <h2>Servicios disponibles</h2>
    </div>
    <div class="service-grid">
{cards}
    </div>
  </div>
</section>""".format(
        rel=rel, cards=service_cards(rel, ctx["services"], limit=3)
    )


def service_faq(s):
    items = list(s.get("faq", []))
    items.append(
        {
            "q": "¿Cómo se define el valor de este servicio?",
            "a": "Después de revisar el predio, el área, el estado de la documentación y el nivel de detalle que necesitas, entregamos una propuesta con alcance, entregables, tiempos y valores. No cotizamos por teléfono un proyecto que todavía no conocemos.",
        }
    )
    return items


def org_node(site):
    base = (site.get("url") or "https://arqtwan.com").rstrip("/")
    return {
        "@type": ["ProfessionalService", "LocalBusiness"],
        "@id": base + "/#organization",
        "name": site.get("name", "Arqtwan"),
        "url": base + "/",
        "logo": base + "/assets/icons/icon-512.png",
        "image": base + "/" + site.get("ogImage", "assets/img/og-arqtwan.jpg"),
        "telephone": site.get("whatsappDisplay", ""),
        "description": (
            "Estudio de arquitectura e ingeniería en Colombia: licencias de construcción, "
            "diseño arquitectónico, diseño estructural, remodelaciones, ampliaciones, "
            "locales comerciales y administración de obra."
        ),
        "areaServed": {"@type": "Country", "name": "Colombia"},
        "address": {"@type": "PostalAddress", "addressCountry": "CO"},
        "openingHoursSpecification": [
            {
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                ],
                "opens": "08:00",
                "closes": "18:00",
            }
        ],
        "priceRange": "$$",
        "knowsLanguage": "es-CO",
    }


def website_node(site):
    base = (site.get("url") or "https://arqtwan.com").rstrip("/")
    return {
        "@type": "WebSite",
        "@id": base + "/#website",
        "url": base + "/",
        "name": site.get("name", "Arqtwan"),
        "inLanguage": "es-CO",
        "publisher": {"@id": base + "/#organization"},
    }


def faq_node(items):
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": item["q"],
                "acceptedAnswer": {"@type": "Answer", "text": item["a"]},
            }
            for item in items
        ],
    }


def breadcrumb_node(site, pairs):
    base = (site.get("url") or "https://arqtwan.com").rstrip("/")
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i,
                "name": label,
                "item": base + "/" + url.lstrip("/") if url else base + "/",
            }
            for i, (label, url) in enumerate(pairs, start=1)
        ],
    }


def service_node(site, s):
    base = (site.get("url") or "https://arqtwan.com").rstrip("/")
    return {
        "@type": "Service",
        "@id": base + "/servicios/" + s["slug"] + ".html#service",
        "name": s["name"],
        "serviceType": s["name"],
        "description": s.get("summary", s.get("short", "")),
        "url": base + "/servicios/" + s["slug"] + ".html",
        "areaServed": {"@type": "Country", "name": "Colombia"},
        "provider": {"@id": base + "/#organization"},
        "inLanguage": "es-CO",
    }


MESES = [
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
]


def fecha_larga(d):
    return "{d} de {m} de {y}".format(d=d.day, m=MESES[d.month - 1], y=d.year)


def make_ctx(data, path, current, title, description, jsonld=None, image=None,
             og_type="website", robots=None):
    import datetime

    today = datetime.date.today()
    return {
        "site": data["site"],
        "services": data["services"],
        "projects": data.get("projects", []),
        "path": path,
        "rel": "../" * path.count("/"),
        "current": current,
        "title": title,
        "description": description,
        "jsonld": jsonld,
        "image": image,
        "og_type": og_type,
        "robots": robots or "index, follow, max-image-preview:large",
        "updated": fecha_larga(today),
        "updated_iso": today.isoformat(),
    }


def write(path, content):
    target = (OUT_DIR or ROOT) / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8", newline="\n")
    print("  ok  {0}  ({1} KB)".format(path, round(len(content.encode("utf-8")) / 1024, 1)))


def build():
    data = load_content()
    site = data["site"]
    services = data["services"]
    base = (site.get("url") or "https://arqtwan.com").rstrip("/")

    print("Generando paginas…")

    home_jsonld = {
        "@context": "https://schema.org",
        "@graph": [org_node(site), website_node(site), faq_node(HOME_FAQ)],
    }
    home_title, home_description = seo_for(
        data,
        "home",
        "Arqtwan | Licencias, arquitectura y construcción en Colombia",
        "Diseño arquitectónico, licencias de construcción, ingeniería y obra en Colombia. "
        "Un solo equipo para tramitar, diseñar y construir con criterio técnico.",
    )
    ctx = make_ctx(
        data,
        "",
        "home",
        home_title,
        home_description,
        jsonld=home_jsonld,
    )
    write("index.html", page(ctx, home_body(ctx)))

    for s in services:
        path = "servicios/" + s["slug"] + ".html"
        crumbs = [
            ("Inicio", base + "/"),
            ("Servicios", base + "/#servicios"),
            (s["name"], base + "/" + path),
        ]
        jsonld = {
            "@context": "https://schema.org",
            "@graph": [
                service_node(site, s),
                breadcrumb_node(site, crumbs),
                faq_node(service_faq(s)),
            ],
        }
        default_description = shorten(
            (s.get("short", "") + " " + s.get("summary", "")).strip()
            if s.get("short")
            else s.get("summary", ""),
            157,
        )
        service_title, service_description = seo_for(
            data,
            "servicios",
            "{0} en Colombia | Arqtwan".format(s["name"]),
            default_description,
            slug=s["slug"],
        )
        ctx = make_ctx(
            data,
            path,
            "servicios",
            service_title,
            service_description,
            jsonld=jsonld,
        )
        write(path, page(ctx, service_body(ctx, s)))

    proyectos_title, proyectos_description = seo_for(
        data,
        "proyectos",
        "Proyectos | Arqtwan arquitectura e ingeniería",
        "Portafolio de Arqtwan: proyectos de arquitectura, ingeniería y construcción "
        "documentados con datos verificables e imágenes propias.",
    )
    ctx = make_ctx(
        data,
        "proyectos.html",
        "proyectos",
        proyectos_title,
        proyectos_description,
        jsonld={
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "CollectionPage",
                    "@id": base + "/proyectos.html#page",
                    "url": base + "/proyectos.html",
                    "name": "Proyectos | Arqtwan",
                    "inLanguage": "es-CO",
                    "isPartOf": {"@id": base + "/#website"},
                },
                breadcrumb_node(
                    site, [("Inicio", base + "/"), ("Proyectos", base + "/proyectos.html")]
                ),
            ],
        },
    )
    write("proyectos.html", page(ctx, projects_body(ctx)))


    contacto_title, contacto_description = seo_for(
        data,
        "contacto",
        "Contacto y cotización | Arqtwan",
        "Escríbenos por WhatsApp o usa el formulario para cotizar tu proyecto de "
        "arquitectura, licencias, ingeniería o construcción en Colombia.",
    )
    ctx = make_ctx(
        data,
        "contacto.html",
        "contacto",
        contacto_title,
        contacto_description,
        jsonld={
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "ContactPage",
                    "@id": base + "/contacto.html#page",
                    "url": base + "/contacto.html",
                    "name": "Contacto y cotización | Arqtwan",
                    "inLanguage": "es-CO",
                    "about": {"@id": base + "/#organization"},
                },
                breadcrumb_node(
                    site, [("Inicio", base + "/"), ("Contacto", base + "/contacto.html")]
                ),
            ],
        },
    )
    write("contacto.html", page(ctx, contact_body(ctx)))

    privacidad_title, privacidad_description = seo_for(
        data,
        "privacidad",
        "Política de privacidad | Arqtwan",
        "Cómo trata Arqtwan los datos que recibe a través de este sitio: formulario de "
        "cotización, WhatsApp, alojamiento y derechos del titular.",
    )
    ctx = make_ctx(
        data,
        "privacidad.html",
        "privacidad",
        privacidad_title,
        privacidad_description,
        jsonld={
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "WebPage",
                    "@id": base + "/privacidad.html#page",
                    "url": base + "/privacidad.html",
                    "name": "Política de privacidad | Arqtwan",
                    "inLanguage": "es-CO",
                },
                breadcrumb_node(
                    site, [("Inicio", base + "/"), ("Privacidad", base + "/privacidad.html")]
                ),
            ],
        },
    )
    write("privacidad.html", page(ctx, privacy_body(ctx)))

    ctx = make_ctx(
        data,
        "404.html",
        "",
        "Página no encontrada | Arqtwan",
        "La página que buscas no existe. Vuelve al inicio o revisa los servicios de Arqtwan.",
        jsonld=None,
        robots="noindex, follow",
    )
    write("404.html", page(ctx, notfound_body(ctx)))

    write(
        "robots.txt",
        "User-agent: *\nAllow: /\nDisallow: /admin/\n\nSitemap: {0}/sitemap.xml\n".format(base),
    )

    urls = ["", "proyectos.html", "contacto.html", "privacidad.html"] + [
        "servicios/" + s["slug"] + ".html" for s in services
    ]
    entries = "\n".join(
        "  <url>\n    <loc>{0}/{1}</loc>\n    <lastmod>{2}</lastmod>\n"
        "    <changefreq>{3}</changefreq>\n    <priority>{4}</priority>\n  </url>".format(
            base,
            u,
            ctx["updated_iso"],
            "weekly" if u in ("", "proyectos.html") else "monthly",
            "1.0" if u == "" else ("0.9" if u.startswith("servicios/") else "0.7"),
        )
        for u in urls
    )
    write(
        "sitemap.xml",
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + entries
        + "\n</urlset>\n",
    )

    print("Listo.")


def main():
    global OUT_DIR
    parser = argparse.ArgumentParser(description="Genera las paginas HTML del sitio.")
    parser.add_argument(
        "--out",
        metavar="CARPETA",
        help="Carpeta de salida (por defecto, la raiz del proyecto). Se crea si no existe.",
    )
    args = parser.parse_args()
    if args.out:
        OUT_DIR = pathlib.Path(args.out).resolve()
        if not str(OUT_DIR).startswith(str(ROOT)):
            raise SystemExit("La carpeta de salida debe estar dentro del proyecto.")
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        print("Salida: {0}".format(OUT_DIR))
    build()


if __name__ == "__main__":
    main()

