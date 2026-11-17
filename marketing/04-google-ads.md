# Google Ads · Estrategia preparada (sin activar)

Estado: **documento de trabajo**. No hay campañas creadas, no hay método de pago
cargado y no se ha gastado dinero. Todo requiere autorización expresa antes de
publicarse.

## Estructura de cuenta propuesta

- 1 campaña de **Búsqueda** con segmentación geográfica: Bogotá D.C. + Soacha
  (radio de 15 km alrededor de Bosa), idioma español, ubicación "presencia".
- Presupuesto diario de referencia: 20.000–30.000 COP (ajustable; no ejecutar sin
  aprobación).
- Estrategia de puja inicial: maximizar clics con CPC máximo de 1.500 COP, y pasar
  a CPA objetivo cuando haya 15-30 conversiones registradas.
- Extensiones: vínculos a sitios (Licencias, Zonas Bosa y Soacha), llamada
  (+57 304 301 8508) y extractos de servicio.

## Grupos de anuncios, palabras clave y página de destino

### Grupo 1 · Licencias Bosa
- `licencia de construcción bosa`
- `licencias de construcción bosa bogota`
- `tramite licencia construccion bosa`
- `curaduria urbana bosa licencia`
- Destino: `https://arqtwan.com/zonas/bosa.html`

### Grupo 2 · Licencias Soacha
- `licencia de construccion soacha`
- `licencias de construccion soacha cundinamarca`
- `tramitar licencia soacha`
- `curaduria urbana soacha`
- Destino: `https://arqtwan.com/zonas/soacha.html`

### Grupo 3 · Legalización y reconocimiento
- `legalizar vivienda soacha`
- `reconocimiento de edificacion bogota`
- `legalizacion de vivienda bosa`
- `regularizar casa sin licencia`
- Destino: `https://arqtwan.com/zonas/soacha.html` y `/servicios/licencias.html`

### Grupo 4 · Planos y diseño
- `planos arquitectonicos bogota`
- `planos para licencia de construccion`
- `diseno arquitectonico bogota`
- `arquitecto bosa`
- Destino: `https://arqtwan.com/servicios/arquitectura.html`

### Grupo 5 · Diseño estructural
- `diseno estructural bogota`
- `calculo estructural vivienda`
- `planos estructurales bogota`
- `ingeniero estructural soacha`
- Destino: `https://arqtwan.com/servicios/estructural.html`

### Grupo 6 · Segundos pisos y ampliaciones
- `segundo piso soacha`
- `construccion segundo piso bogota`
- `ampliacion casa bosa`
- `levantar segundo piso precio`
- Destino: `https://arqtwan.com/servicios/ampliacion.html`

### Grupo 7 · Remodelación
- `remodelacion de vivienda bogota`
- `remodelar casa bosa`
- `remodelacion soacha`
- Destino: `https://arqtwan.com/servicios/remodelacion.html`

## Concordancia

Usar concordancia de frase (`"…"`) en las palabras con intención local y
concordancia amplia solo en las genéricas (grupos 4 y 7). Revisar el informe de
términos de búsqueda a la semana 2 antes de ampliar.

## Palabras clave negativas iniciales

`gratis`, `curso`, `carrera`, `universidad`, `empleo`, `trabajo`, `vacante`,
`salario`, `software`, `app`, `descargar`, `pdf`, `ejemplo`, `tesis`, `norma
gratis`, `que es`, `significado`, `alquiler`, `arriendo`, `venta de casa`,
`apartamento`, `propiedad raiz`, `credito`, `hipoteca`, `seguro`, `abogado`,
`contador`, `ferreteria`, `cemento`, `ladrillo`, `maqueta`, `render gratis`.

Revisar el informe de términos de búsqueda cada 14 días y trasladar a negativas
todo lo que sea informativo puro, empleo, formación o compra de materiales.

## Anuncios (textos listos para cargar)

### Anuncio A · Licencias Bosa (`/zonas/bosa.html`)

Títulos (máx. 30 caracteres):
1. Licencias en Bosa, Bogotá
2. Arquitecto en Bosa
3. Revisión normativa previa
4. Planos y expediente
5. Cotiza por WhatsApp hoy
6. Un solo equipo técnico
7. Visita al predio en Bosa
8. 10 años de experiencia

Descripciones (máx. 90 caracteres):
1. Revisamos norma y predio antes de dibujar. Cotización clara por WhatsApp.
2. Licencias, planos y obra con un solo equipo. Atención en Bosa y Bogotá.
3. Expediente completo para reducir requerimientos. Pide tu diagnóstico.

### Anuncio B · Licencias y legalización Soacha (`/zonas/soacha.html`)

Títulos:
1. Licencias en Soacha
2. Arquitecto en Soacha
3. Reconocimiento de edificio
4. Norma municipal revisada
5. Cotiza por WhatsApp
6. Trámites y planos
7. Visita a tu predio
8. 10 años de experiencia

Descripciones:
1. Licencias, reconocimiento y obra nueva en Soacha. Diagnóstico sin costo.
2. Revisamos la norma del municipio antes de proyectar. Respuesta por WhatsApp.
3. Ampliaciones, segundos pisos y legalización. Pide tu cotización hoy.

### Anuncio C · Diseño estructural (`/servicios/estructural.html`)

Títulos:
1. Diseño estructural Bogotá
2. Cálculo para segundos pisos
3. Revisión de lo existente
4. Planos de cimentación
5. Coordinado con arquitectura
6. Cotiza por WhatsApp
7. Memoria de cálculo
8. Visita técnica al predio

Descripciones:
1. Cálculo y planos estructurales coordinados con la arquitectura del proyecto.
2. Revisamos la estructura existente antes de ampliar. Cotización por WhatsApp.
3. Diseño, memoria de cálculo y acompañamiento en obra. Atención en Bogotá.

## Segmentación geográfica

- Bogotá D.C. (todas las localidades), con ajuste de puja +20 % en Bosa, Kennedy y
  Ciudad Bolívar.
- Soacha, Cundinamarca (+15 %).
- Excluir el resto del país en la campaña local; si se abre cobertura nacional,
  crear una campaña aparte con presupuesto propio y otro texto.

## Estrategia de conversiones

1. **Dependencia previa:** sin GA4 o sin etiqueta de conversión no hay medición
   fiable. Ver `02-analytics-ga4.md`; la activación exige aviso de cookies.
2. Conversión principal: `form_submit` (solicitud de cotización).
3. Conversión secundaria: `whatsapp_click` con `origen` = `hero`, `zona-bosa`,
   `zona-soacha`, `servicio-*`.
4. Importar ambas desde GA4 a Google Ads y pujar por la principal.
5. No usar "clic en el sitio" ni "página vista" como conversión: infla el CPA y
   no refleja negocio.

## Página de destino: lista de control

- El H1 coincide con la intención del anuncio (Bosa, Soacha, estructural…).
- Botón de WhatsApp visible sin desplazarse, con mensaje precargado por zona.
- Formulario de cotización con servicio preseleccionado cuando aplique.
- Tiempo de carga móvil por debajo de 2,5 s en LCP.
- Sin promesas de aprobación de trámites: además de ser honesto, evita rechazos
  por políticas de contenido engañoso.

## Antes de activar

1. Confirmar presupuesto máximo mensual y método de pago con el propietario.
2. Confirmar que la cuenta de Ads será la del propietario del negocio.
3. Verificar el dominio en Ads y revisar que no haya suspensiones previas.
4. Publicar primero el sitio actualizado (las páginas de zona deben estar en vivo).

