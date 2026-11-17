# Google Search Console

## Estado comprobado el 17/11/2026

- El sitio incluye en todas las páginas la etiqueta
  `<meta name="google-site-verification" content="o0HdO8HkEtZiGqGIS2KYd91j7IE8fGOWgMSSIqJjJbg">`.
  Esa etiqueta indica que en algún momento se verificó una propiedad con ese
  código, pero **no confirma que la propiedad siga activa ni que el sitemap esté
  enviado**.
- `https://arqtwan.com/robots.txt` responde 200 y permite el rastreo (solo bloquea
  `/admin/`).
- `https://arqtwan.com/sitemap.xml` responde 200 con 14 URLs válidas.
- El agente **no tiene acceso** a Search Console: no hay credenciales ni sesión
  autorizada. Ningún dato de impresiones, clics, CTR o posición de este informe
  proviene de Search Console.

## Acciones del administrador (en orden)

1. Entrar en <https://search.google.com/search-console> con la cuenta de Google
   propietaria del sitio.
2. Si la propiedad no aparece: crear **Propiedad de dominio** para `arqtwan.com`
   (verificación por registro TXT en el DNS del proveedor) o **Propiedad de
   prefijo de URL** `https://arqtwan.com/` (verificación por etiqueta HTML, que ya
   existe en el sitio: basta pulsar *Verificar*).
3. Ir a **Sitemaps** y enviar `sitemap.xml`. El archivo ya está publicado y
   referenciado en robots.txt.
4. Ir a **Inspección de URL** y pedir indexación, una por una, de:
   - `https://arqtwan.com/zonas/bosa.html`
   - `https://arqtwan.com/zonas/soacha.html`
   - `https://arqtwan.com/servicios/estructural.html`
   - `https://arqtwan.com/` (si cambió el título)
5. En **Configuración → Rastreo** revisar que no haya bloqueos por robots,
   acciones manuales ni problemas de seguridad.
6. Comprobar en **Páginas** (Indexación) que las 14 URLs del sitemap figuren como
   *Indexada* y no como *Rastreada, no indexada*.

## Qué revisar cada mes

| Métrica | Dónde | Para qué sirve |
|---|---|---|
| Páginas indexadas | Indexación → Páginas | Saber si las páginas locales entran |
| Impresiones y clics | Rendimiento | Demanda real por consulta |
| CTR | Rendimiento | Si el título convence en la SERP |
| Posición media | Rendimiento | Evolución, nunca valor absoluto |
| Consultas con impresiones y 0 clics | Rendimiento → Consultas | Oportunidades de reescritura |
| Errores de rastreo | Indexación | Enlaces rotos y respuestas 5xx |
| Core Web Vitals | Experiencia | Validar el trabajo de LCP y video |

## Consultas a vigilar (crear un filtro por cada una)

`licencias de construcción bosa`, `licencias de construcción soacha`,
`arquitecto bosa`, `planos arquitectónicos soacha`, `legalización de vivienda
soacha`, `diseño estructural bogotá`, `segundos pisos soacha`, `reconocimiento de
edificación bogotá`, `remodelación bosa`, `ampliación segundo piso bogotá`.

Guardar una captura mensual del informe de Rendimiento: es la única fuente válida
para afirmar posiciones.
