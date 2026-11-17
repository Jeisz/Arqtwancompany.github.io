# Posicionamiento observado en buscadores

## Método y fecha

Consulta realizada el **17 de noviembre de 2026** mediante peticiones HTTP
automatizadas a los buscadores. No se usó ninguna cuenta ni API de pago.

## Qué ocurrió con cada intento

| Buscador | Consulta | Resultado real obtenido |
|---|---|---|
| Google | `site:arqtwan.com` | Página intersticial de verificación ("Haz clic aquí si no se te redirecciona"). **Sin resultados consultables.** |
| Bing | `site:arqtwan.com` | Devolvió resultados no relacionados con la consulta (contenido genérico sobre Twitter). **Dato no fiable, descartado.** |
| DuckDuckGo (html y lite) | `site:arqtwan.com` | Reto anti-bots con selección de imágenes. **Bloqueado.** |
| Mojeek | `site:arqtwan.com` | Reto JavaScript. **Bloqueado.** |
| Brave Search | `site:arqtwan.com` | Respuesta: *"Too few matches were found"* y *"search operators were not applied"*. **Sin resultados.** |
| Ecosia | `site:arqtwan.com` | HTTP 403. **Bloqueado.** |
| SearXNG (searx.be) | `site:arqtwan.com` | Verificación de navegador. **Bloqueado.** |

## Conclusión honesta

1. **No se pudo observar ninguna posición en Google.** Cualquier número de
   posición en este informe sería inventado, y no se va a inventar.
2. La ausencia de resultados en Brave **no** demuestra que Google no tenga indexado
   el sitio: Brave usa su propio índice, independiente del de Google.
3. Lo único verificable de forma directa fue el comportamiento del servidor:
   `https://arqtwan.com/` respondía 200 sirviendo la **versión anterior** del sitio
   (7 servicios, sin página de diseño estructural ni páginas de zona),
   `robots.txt` respondía 200 con `Allow: /` y `Disallow: /admin/`, y el dominio
   operaba por HTTPS.
4. Por tanto, a la fecha de la consulta, el estado comprobado es: **publicado y
   rastreable**, con **indexación no verificada** (requiere Search Console).

## Protocolo manual para el propietario (10 minutos)

1. Abrir una ventana de incógnito (sin sesión de Google) o cerrar sesión.
2. En Google, revisar que la ubicación detectada sea Bogotá y que la búsqueda no
   esté personalizada.
3. Ejecutar cada consulta de la tabla siguiente y anotar: aparece sí/no, posición
   del bloque orgánico, URL mostrada, título mostrado y si el resultado es
   orgánico, anuncio o mapa.
4. Repetir la medición el mismo día de cada mes para poder comparar.

| Consulta | ¿Aparece? | Posición orgánica | URL | Título | Tipo |
|---|---|---|---|---|---|
| `site:arqtwan.com` | | | | | orgánico |
| licencias de construcción en Bosa | | | | | |
| licencias de construcción en Soacha | | | | | |
| planos arquitectónicos en Soacha | | | | | |
| arquitectos en Bosa Bogotá | | | | | |
| diseño estructural Bogotá | | | | | |
| legalización de viviendas Soacha | | | | | |
| construcción de segundos pisos en Soacha | | | | | |
| empresas de construcción en Bosa | | | | | |

## Competidores esperables (a confirmar en la medición manual)

En estas consultas suelen aparecer curadurías, portales inmobiliarios, directorios
de profesionales y constructoras locales. Es un supuesto de trabajo, no un dato
medido: no se ha verificado ninguno en esta sesión.

## Regla de interpretación

Una búsqueda puntual no es un dato de rendimiento. Solo Search Console (Fase 5 de
`01-search-console.md`) permite afirmar impresiones, clics, CTR y posición media con
fundamento.
