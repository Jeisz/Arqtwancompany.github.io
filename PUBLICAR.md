# Publicar ARQTWAN

Guía para administrar el sitio **sin programar** y publicarlo en GitHub Pages con el dominio `arqtwan.com`.

---

## 1. Cómo está armado el proyecto

| Ruta | Para qué sirve | ¿Se toca a mano? |
|---|---|---|
| `data/content.js` | Todo el contenido: textos, servicios, proyectos, contacto, SEO | **No**: lo edita el panel |
| `assets/img/`, `assets/video/` | Fotos, láminas, video de portada | **No**: se suben desde el panel |
| `admin/` | Panel visual (se abre en tu equipo, no se publica) | No |
| `tools/editor.py` | Servidor local que guarda y regenera | No |
| `tools/build_pages.py` | Genera los HTML, `sitemap.xml` y `robots.txt` | No |
| `styles.css`, `script.js` | Diseño y comportamiento del sitio | No |
| `.github/workflows/deploy.yml` | Reconstruye y publica en GitHub Pages | No |

Los archivos `index.html`, `servicios/*.html`, `proyectos.html`, `contacto.html`, `privacidad.html`, `404.html`, `sitemap.xml` y `robots.txt` **se generan solos**. No se editan ni se suben.

---

## 2. Uso diario (5 minutos)

1. Abre **`Editor ARQTWAN.bat`** (doble clic). Se abre el panel en `http://127.0.0.1:8765/`.
2. Edita lo que necesites:
   - **Portada**: antetítulo, título, párrafo, imagen de fondo y video.
   - **Servicios**: textos, alcance, entregables, pasos, preguntas e imagen.
   - **Proyectos**: añadir, ordenar, borrar, foto y descripción.
   - **Contacto**: WhatsApp, correo, ciudad, horario, años de experiencia, imagen para redes.
   - **SEO**: título y descripción de cada página (con aviso si te pasas de largo).
3. Pulsa **Guardar y regenerar**. Se escriben `data/content.js` y las fotos, y se reconstruyen los HTML.
4. Pulsa **Vista previa**: abre el sitio real en el navegador (local). Si algo no te gusta, corriges y vuelves a guardar.
5. Ve a **Publicar** → escribe tu `usuario/repositorio` una sola vez → **Preparar carpeta _publicar** → arrastra la carpeta `_publicar` completa a GitHub → **Commit changes**.

En 1–2 minutos la Action reconstruye el sitio y lo publica. Si el generador falla, **el sitio anterior sigue en línea**.

> Copias de seguridad: cada vez que guardas, el panel copia la versión anterior en `backup/content/<fecha>/`. Nada se pierde.

---

## 3. Primera puesta en marcha en GitHub (una sola vez)

### 3.1 Crear el repositorio
1. Entra en [github.com/new](https://github.com/new).
2. Nombre: `arqtwan-web` (o el que prefieras). Visibilidad: **Public** (Pages gratis; el sitio es público de todas formas).
3. No marques "Add a README". Crea el repositorio.

### 3.2 Subir el proyecto (sin programas)
En el repositorio vacío: **Add file → Upload files** y arrastra **solo esto**:

```
assets/          (carpeta completa)
data/            (carpeta completa)
admin/           (carpeta completa)
tools/           (carpeta completa)
.github/         (carpeta completa; contiene la Action)
styles.css
script.js
favicon.ico
site.webmanifest
CNAME
.gitignore
PUBLICAR.md
Editor ARQTWAN.bat
```

**No subas**: `_publicar`, `_site`, `backup`, `.tmp_*`, `index.html`, `proyectos.html`, `contacto.html`, `privacidad.html`, `404.html`, `servicios/`, `sitemap.xml`, `robots.txt` (todo eso se genera).

Pulsa **Commit changes**.

### 3.3 Activar GitHub Pages con la Action
1. **Settings → Pages**.
2. En *Build and deployment → Source*, elige **GitHub Actions**.
3. Ve a la pestaña **Actions**: debe estar corriendo (o pulsa *Run workflow*) el flujo **Publicar sitio**.
4. Cuando termine en verde, tu sitio está en `https://usuario.github.io/arqtwan-web/` (provisional).

### 3.4 Dominio `arqtwan.com`
1. **Settings → Pages → Custom domain**: escribe `arqtwan.com` y guarda. El archivo `CNAME` ya está incluido.
2. En **Namecheap → Domain List → arqtwan.com → Advanced DNS**, borra los registros que apunten a un parking y crea:

| Tipo | Host | Valor | TTL |
|---|---|---|---|
| A Record | `@` | `185.199.108.153` | Automatic |
| A Record | `@` | `185.199.109.153` | Automatic |
| A Record | `@` | `185.199.110.153` | Automatic |
| A Record | `@` | `185.199.111.153` | Automatic |
| CNAME Record | `www` | `usuario.github.io` | Automatic |

3. Espera entre 30 minutos y 24 horas (la propagación DNS no es inmediata).
4. Vuelve a **Settings → Pages** y activa **Enforce HTTPS** cuando GitHub lo permita.

> Verifica siempre los valores de DNS en la documentación oficial de GitHub Pages antes de guardar: GitHub puede actualizar las IP.

---

## 4. Si algo falla

| Síntoma | Qué hacer |
|---|---|
| El panel dice "Sin conexión con el editor" | Abre el `.bat` (o `python tools/editor.py`) y entra a `http://127.0.0.1:8765/` |
| "El generador falló" al guardar | Revisa el mensaje del panel; casi siempre es un campo vacío obligatorio (título de proyecto o nombre de servicio). La copia de seguridad permite volver atrás |
| La Action sale en rojo | **Actions → Publicar sitio →** lee el paso que falló. Mientras tanto, la web sigue mostrando la versión anterior |
| Cambié cosas y la web no cambia | Comprueba que el commit llegó a `main` y que la Action terminó en verde. Luego recarga con Ctrl+F5 |
| La foto se ve borrosa | Sube una imagen de al menos 1600 px de ancho; el panel recorta a 4:3 y optimiza |

---

## 5. Seguridad

- Este proyecto **no usa tokens, ni contraseñas, ni bases de datos, ni servidores**.
- El panel corre solo en `127.0.0.1` (tu equipo) y la carpeta `admin/` no se publica.
- Publicar siempre requiere tu acción manual en GitHub: el panel nunca publica por su cuenta.

---

## 6. Comandos útiles (opcionales)

```powershell
python tools\editor.py          # abre el panel visual
python tools\build_pages.py     # regenera el sitio en la carpeta del proyecto
python tools\check_links.py     # revisa enlaces, canonical y JSON-LD
```
