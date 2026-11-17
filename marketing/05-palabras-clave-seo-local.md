# Palabras clave prioritarias y SEO local

## Las diez prioridades

| # | Palabra clave | Intención | URL que debe posicionar | Estado |
|---|---|---|---|---|
| 1 | licencias de construcción en Bosa | Comercial local | `/zonas/bosa.html` + `/servicios/licencias.html` | Página local creada |
| 2 | licencias de construcción en Soacha | Comercial local | `/zonas/soacha.html` + `/servicios/licencias.html` | Página local creada |
| 3 | arquitecto en Bosa Bogotá | Comercial local | `/zonas/bosa.html` | Página local creada |
| 4 | planos arquitectónicos en Soacha | Comercial | `/servicios/arquitectura.html` + zona | Servicio creado |
| 5 | diseño estructural Bogotá | Comercial | `/servicios/estructural.html` | Servicio creado |
| 6 | legalización de viviendas en Soacha | Informativa-comercial | `/zonas/soacha.html` | Contenido creado |
| 7 | construcción de segundos pisos en Soacha | Comercial | `/servicios/ampliacion.html` + zona | Servicio creado |
| 8 | reconocimiento de edificación Bogotá | Comercial | `/servicios/licencias.html` + zona | Contenido creado |
| 9 | remodelación de vivienda en Bosa | Comercial | `/servicios/remodelacion.html` | Servicio creado |
| 10 | empresas de construcción en Bosa | Comercial | `/zonas/bosa.html` + inicio | Página local creada |

## Cómo se tradujo cada intención en el sitio

- **Título local, H1 local y contenido local**: las páginas de Bosa y Soacha
  explican normativa, trámites, riesgos y documentos. No son copias entre sí ni
  variaciones de la página de servicios.
- **Enlazado interno**: inicio → zonas, cada servicio → ambas zonas, cada zona →
  cuatro servicios y a la zona vecina, footer → zonas en todas las páginas.
- **Datos estructurados**: `areaServed` incluye Bogotá, Bosa, Soacha y
  Cundinamarca; cada zona publica `WebPage`, `BreadcrumbList` y `FAQPage`.
- **Sin datos inventados**: no hay dirección, ni mapa, ni afirmación de obras
  ejecutadas en la zona. La imagen de cada página local se declara como lámina
  ilustrativa.

## Recomendaciones de SEO local que faltan (requieren datos del propietario)

1. **Dirección real de atención**, si existe: permitiría `PostalAddress` completa,
   mapa embebido y perfil de empresa con ubicación. Sin ella, no debe publicarse.
2. **Zonas adicionales con contenido propio** solo si hay cobertura real:
   Kennedy, Ciudad Bolívar, Funza o Mosquera serían los siguientes candidatos por
   cercanía, pero cada una necesita contenido diferencial y verificable.
3. **Fotografías propias de obra**: hoy todas las imágenes de servicio son láminas
   SVG. Una foto real por servicio mejora CTR y confianza, y habilita
   `ImageObject` con `contentUrl` propio.
4. **Reseñas en Google**: sin reseñas, la ficha no compite en el paquete local.

## Plan de contenidos (guías que atraen consultas)

Publicar una cada 3-4 semanas, enlazando a la página de servicio o zona:

1. Qué documentos necesito para una licencia de construcción en Bogotá.
2. Reconocimiento de edificación: cuándo sirve y cuándo no.
3. Cómo saber si mi casa en Bosa puede recibir un segundo piso.
4. Legalización vs. reconocimiento: qué hacer si el barrio está en proceso.
5. Cuánto cuesta construir un segundo piso en Soacha (con rangos y variables, sin
   prometer precios cerrados).
6. Errores que devuelven un expediente de licencia en la curaduría.

Cada guía debe incluir: respuesta directa en el primer párrafo, ejemplos con
variables reales, enlaces a la zona y al servicio, y tres preguntas frecuentes con
su `FAQPage`. Nada de texto genérico reutilizado entre guías.
