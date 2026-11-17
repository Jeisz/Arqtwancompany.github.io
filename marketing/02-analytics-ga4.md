# Google Analytics 4

## Estado: preparado, no activado

- El sitio **no carga ningún script de Google** ni tiene identificador de medición.
- `script.js` ya emite los eventos de negocio mediante una función interna
  `track(nombre, params)` que:
  1. dispara un `CustomEvent("arqtwan:track")` en `document`, y
  2. llama a `window.gtag("event", nombre, params)` **solo si `gtag` existe**.
- Por tanto, el día que se añada GA4 los eventos empiezan a viajar sin tocar el
  código de comportamiento.

## Eventos ya implementados

| Evento | Parámetros | Cuándo se dispara |
|---|---|---|
| `whatsapp_click` | `origen` | Clic en cualquier enlace `data-wa` |
| `form_submit` | `servicio` | Envío válido del formulario de cotización |
| `form_error` | `motivo: validacion` | Envío con datos incompletos |

Valores de `origen` que ya existen en el HTML: `hero`, `footer`, `flotante`,
`cta`, `servicio-<slug>` (ocho servicios), `zona-bosa`, `zona-soacha`.

## Cómo activarlo (cuando el administrador lo decida)

1. Crear la propiedad GA4 en <https://analytics.google.com> con la zona horaria
   de Colombia y moneda COP.
2. Copiar el identificador `G-XXXXXXXXXX` (no inventar: el real lo entrega Google).
3. Insertar **antes** de `script.js` en `tools/build_pages.py`, función `page()`:

```html
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX', { anonymize_ip: true });
</script>
```

4. En GA4 → Administrar → Eventos, marcar `whatsapp_click` y `form_submit` como
   **eventos clave** (conversiones).
5. Crear públicos: visitantes de `/zonas/bosa.html`, de `/zonas/soacha.html` y de
   `/servicios/licencias.html`.
6. Vincular GA4 con Google Ads para importar conversiones (ver `04-google-ads.md`).

## Privacidad y consentimiento (obligatorio antes de activar)

- La política actual afirma que el formulario no guarda datos en el sitio, lo cual
  sigue siendo cierto porque todo se envía por WhatsApp.
- GA4 sí instala cookies e identificadores. Antes de activarlo hay que:
  1. Añadir a `privacidad.html` un apartado de **medición con Google Analytics**
     indicando finalidad, base legal, duración y forma de desactivar la medición.
  2. Implementar un aviso de cookies con opción de rechazo (Consent Mode v2:
     `ad_storage`, `analytics_storage` por defecto en `denied` hasta aceptar).
  3. No cargar `gtag.js` antes de la decisión del usuario.
- Sin esos tres pasos, la activación sería técnicamente posible pero no conforme.

## Qué se podrá medir al activarlo

Visitantes y sesiones, procedencia orgánica, páginas más vistas, clics a WhatsApp
por origen (hero, servicios, zonas, flotante), envíos del formulario de cotización
y tasa de conversión visita → consulta comercial.
