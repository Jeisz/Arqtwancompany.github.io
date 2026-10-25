/* Editor ARQTWAN · panel local (sin dependencias externas) */
(function () {
  "use strict";

  var $ = function (selector, root) { return (root || document).querySelector(selector); };
  var CACHE_BUST = 0;

  var state = {
    content: null,
    seo: [],
    meta: {},
    pending: {},
    changed: [],
    dirty: false,
    serviceIndex: 0
  };

  /* ------------------------------------------------------------------ */
  /* Utilidades                                                          */
  /* ------------------------------------------------------------------ */
  var toastTimer = null;

  function toast(message, kind) {
    var box = $("#toast");
    box.textContent = message;
    box.className = "toast" + (kind ? " is-" + kind : "");
    box.hidden = false;
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(function () { box.hidden = true; }, kind === "error" ? 9000 : 4200);
  }

  function setStatus(text, detail) {
    $("#status").textContent = text || "";
    $("#status-detail").textContent = detail || "";
  }

  function setDirty(value) {
    state.dirty = !!value;
    var label = $("#dirty-label");
    label.textContent = state.dirty ? "Cambios sin guardar" : "Todo guardado";
    label.className = "pill " + (state.dirty ? "pill--dirty" : "pill--clean");
  }

  function markChanged(path) {
    if (!path) return;
    if (state.changed.indexOf(path) === -1) {
      state.changed.push(path);
      renderChanged();
    }
  }

  function renderChanged() {
    var list = $("#changed-list");
    list.innerHTML = "";
    var files = state.changed.slice();
    if (!files.length) files = ["data/content.js"];
    files.forEach(function (path) {
      var item = document.createElement("li");
      item.textContent = path;
      list.appendChild(item);
    });
  }

  function slugify(value) {
    var text = String(value || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "");
    return text.slice(0, 42) || "proyecto";
  }

  function previewSrc(path) {
    if (state.pending[path]) return state.pending[path];
    return "/preview/" + path + "?v=" + CACHE_BUST;
  }

  function updateCounters() {
    var hints = document.querySelectorAll("[data-counter-for]");
    Array.prototype.forEach.call(hints, function (hint) {
      var input = document.getElementById(hint.getAttribute("data-counter-for"));
      if (!input) return;
      var max = Number(input.getAttribute("maxlength") || 0);
      var length = input.value.length;
      hint.textContent = max
        ? length + " de " + max + " caracteres"
        : length + " caracteres";
      hint.className = "hint" + (max && length > max * 0.95 ? " is-over" : "");
    });
  }

  /* ------------------------------------------------------------------ */
  /* Imagenes                                                            */
  /* ------------------------------------------------------------------ */
  function dataURLFromFile(file) {
    return new Promise(function (resolve, reject) {
      var reader = new FileReader();
      reader.onload = function () { resolve(String(reader.result)); };
      reader.onerror = function () { reject(new Error("No se pudo leer el archivo.")); };
      reader.readAsDataURL(file);
    });
  }

  function resizeToJpeg(file, width, height, quality) {
    return new Promise(function (resolve, reject) {
      var url = URL.createObjectURL(file);
      var image = new Image();
      image.onload = function () {
        var scale = Math.max(width / image.width, height / image.height);
        var sw = width / scale;
        var sh = height / scale;
        var sx = Math.max(0, (image.width - sw) / 2);
        var sy = Math.max(0, (image.height - sh) / 2);
        var canvas = document.createElement("canvas");
        canvas.width = width;
        canvas.height = height;
        var ctx = canvas.getContext("2d");
        ctx.imageSmoothingEnabled = true;
        ctx.imageSmoothingQuality = "high";
        ctx.drawImage(image, sx, sy, sw, sh, 0, 0, width, height);
        URL.revokeObjectURL(url);
        resolve(canvas.toDataURL("image/jpeg", quality || 0.82));
      };
      image.onerror = function () {
        URL.revokeObjectURL(url);
        reject(new Error("El archivo no es una imagen válida."));
      };
      image.src = url;
    });
  }

  function pickImage(options) {
    var input = options.el || $(options.input);
    if (!input) return;
    input.addEventListener("change", function () {
      var file = input.files && input.files[0];
      if (!file) return;
      var target = typeof options.path === "function" ? options.path() : options.path;
      if (!target) return;
      setStatus("Procesando imagen…", file.name);
      resizeToJpeg(file, options.width, options.height, options.quality)
        .then(function (dataUrl) {
          state.pending[target] = dataUrl;
          markChanged(target);
          if (options.preview) $(options.preview).src = dataUrl;
          else if (options.previewEl) options.previewEl.src = dataUrl;
          if (options.onPath) options.onPath(target);
          setDirty(true);
          var kb = Math.round(dataUrl.length * 0.75 / 1024);
          setStatus("Imagen lista para guardar", target + " · " + kb + " KB");
          input.value = "";
        })
        .catch(function (error) { toast(error.message, "error"); });
    });
  }

  /* ------------------------------------------------------------------ */
  /* Portada, contacto y datos del sitio                                 */
  /* ------------------------------------------------------------------ */
  function bindValue(input, obj, key) {
    input.value = obj[key] == null ? "" : obj[key];
    input.addEventListener("input", function () {
      obj[key] = input.value;
      setDirty(true);
    });
  }

  function fillPortada() {
    var site = state.content.site;
    site.hero = site.hero || { kicker: "", title: "", titleEm: "", lede: "" };
    bindValue($("#hero-kicker"), site.hero, "kicker");
    bindValue($("#hero-title"), site.hero, "title");
    bindValue($("#hero-em"), site.hero, "titleEm");
    bindValue($("#hero-lede"), site.hero, "lede");

    $("#poster-preview").src = previewSrc("assets/img/hero-poster.jpg");
    pickImage({
      input: "#poster-file",
      preview: "#poster-preview",
      path: "assets/img/hero-poster.jpg",
      width: 1920,
      height: 1080,
      quality: 0.85
    });

    $("#video-file").addEventListener("change", function () {
      var input = $("#video-file");
      var file = input.files && input.files[0];
      if (!file) return;
      if (file.size > 15 * 1024 * 1024) {
        toast("El video pesa " + Math.round(file.size / 1048576) + " MB. El máximo es 15 MB.", "error");
        input.value = "";
        return;
      }
      dataURLFromFile(file).then(function (dataUrl) {
        state.pending["assets/video/hero.mp4"] = dataUrl;
        markChanged("assets/video/hero.mp4");
        $("#video-status").textContent =
          "Video nuevo listo para guardar: " + file.name + " · " +
          Math.round((file.size / 1048576) * 10) / 10 + " MB";
        setDirty(true);
        input.value = "";
      }).catch(function (error) { toast(error.message, "error"); });
    });
  }

  function fillContacto() {
    var site = state.content.site;
    ["email", "city", "serviceArea", "hours", "experienceYears", "whatsapp", "whatsappDisplay"].forEach(
      function (key) {
        if (site[key] == null) site[key] = "";
      }
    );
    bindValue($("#site-whatsapp"), site, "whatsapp");
    bindValue($("#site-whatsapp-display"), site, "whatsappDisplay");
    bindValue($("#site-email"), site, "email");
    bindValue($("#site-city"), site, "city");
    bindValue($("#site-service-area"), site, "serviceArea");
    bindValue($("#site-hours"), site, "hours");
    bindValue($("#site-years"), site, "experienceYears");

    $("#site-whatsapp").addEventListener("input", function () {
      var clean = $("#site-whatsapp").value.replace(/[^0-9]/g, "");
      if (clean !== $("#site-whatsapp").value) $("#site-whatsapp").value = clean;
      site.whatsapp = clean;
      setDirty(true);
    });

    var ogPath = site.ogImage || "assets/img/og-arqtwan.jpg";
    site.ogImage = ogPath;
    $("#og-preview").src = previewSrc(ogPath);
    pickImage({
      input: "#og-file",
      preview: "#og-preview",
      path: ogPath,
      width: 1200,
      height: 630,
      quality: 0.86,
      onPath: function (path) { site.ogImage = path; }
    });
  }

  /* ------------------------------------------------------------------ */
  /* Servicios                                                           */
  /* ------------------------------------------------------------------ */
  function currentService() {
    return state.content.services[state.serviceIndex] || state.content.services[0];
  }

  function bindServiceField(selector, key) {
    var input = $(selector);
    input.addEventListener("input", function () {
      var service = currentService();
      service[key] = input.value;
      if (key === "name") {
        var option = $("#service-select").options[state.serviceIndex];
        if (option) option.textContent = input.value;
      }
      setDirty(true);
    });
  }

  function bindServiceList(selector, key) {
    var input = $(selector);
    input.addEventListener("input", function () {
      currentService()[key] = input.value
        .split("\n")
        .map(function (line) { return line.trim(); })
        .filter(Boolean);
      setDirty(true);
    });
  }

  function renderServicio() {
    var service = currentService();
    $("#service-select").value = String(state.serviceIndex);

    $("#svc-name").value = service.name || "";
    $("#svc-short").value = service.short || "";
    $("#svc-summary").value = service.summary || "";
    $("#svc-bullets").value = (service.bullets || []).join("\n");
    $("#svc-deliverables").value = (service.deliverables || []).join("\n");
    $("#svc-real").checked = !!service.realPhoto;

    var plate = service.plate || "assets/img/plate-arquitectura.svg";
    $("#svc-plate-preview").src = previewSrc(plate);

    renderSteps();
    renderFaq();
    updateCounters();
  }


  function renderSteps() {
    var service = currentService();
    service.steps = Array.isArray(service.steps) ? service.steps : [];
    var box = $("#svc-steps");
    box.innerHTML = "";

    service.steps.forEach(function (step, index) {
      var row = document.createElement("div");
      row.className = "grid grid--2";

      var titleField = document.createElement("div");
      titleField.className = "field";
      var titleLabel = document.createElement("label");
      titleLabel.textContent = "Paso " + (index + 1) + " · título";
      var titleInput = document.createElement("input");
      titleInput.type = "text";
      titleInput.value = step.title || "";
      titleInput.addEventListener("input", function () {
        step.title = titleInput.value;
        setDirty(true);
      });
      titleField.appendChild(titleLabel);
      titleField.appendChild(titleInput);

      var textField = document.createElement("div");
      textField.className = "field";
      var textLabel = document.createElement("label");
      textLabel.textContent = "Descripción";
      var textInput = document.createElement("input");
      textInput.type = "text";
      textInput.value = step.text || "";
      textInput.addEventListener("input", function () {
        step.text = textInput.value;
        setDirty(true);
      });
      var remove = document.createElement("button");
      remove.type = "button";
      remove.className = "btn btn--ghost btn--sm";
      remove.style.marginTop = "0.35rem";
      remove.textContent = "Quitar paso";
      remove.addEventListener("click", function () {
        service.steps.splice(index, 1);
        renderSteps();
        setDirty(true);
      });
      textField.appendChild(textLabel);
      textField.appendChild(textInput);
      textField.appendChild(remove);

      row.appendChild(titleField);
      row.appendChild(textField);
      box.appendChild(row);
    });
  }

  function renderFaq() {
    var service = currentService();
    service.faq = Array.isArray(service.faq) ? service.faq : [];
    var box = $("#svc-faq");
    box.innerHTML = "";

    service.faq.forEach(function (item, index) {
      var row = document.createElement("div");
      row.className = "grid grid--2";

      var qField = document.createElement("div");
      qField.className = "field";
      var qLabel = document.createElement("label");
      qLabel.textContent = "Pregunta " + (index + 1);
      var qInput = document.createElement("input");
      qInput.type = "text";
      qInput.value = item.q || "";
      qInput.addEventListener("input", function () {
        item.q = qInput.value;
        setDirty(true);
      });
      qField.appendChild(qLabel);
      qField.appendChild(qInput);

      var aField = document.createElement("div");
      aField.className = "field";
      var aLabel = document.createElement("label");
      aLabel.textContent = "Respuesta";
      var aInput = document.createElement("textarea");
      aInput.rows = 2;
      aInput.value = item.a || "";
      aInput.addEventListener("input", function () {
        item.a = aInput.value;
        setDirty(true);
      });
      var remove = document.createElement("button");
      remove.type = "button";
      remove.className = "btn btn--ghost btn--sm";
      remove.style.marginTop = "0.35rem";
      remove.textContent = "Quitar pregunta";
      remove.addEventListener("click", function () {
        service.faq.splice(index, 1);
        renderFaq();
        setDirty(true);
      });
      aField.appendChild(aLabel);
      aField.appendChild(aInput);
      aField.appendChild(remove);

      row.appendChild(qField);
      row.appendChild(aField);
      box.appendChild(row);
    });
  }

  function fillServicios() {
    var select = $("#service-select");
    state.content.services.forEach(function (service, index) {
      var option = document.createElement("option");
      option.value = String(index);
      option.textContent = service.name;
      select.appendChild(option);
    });

    select.addEventListener("change", function () {
      state.serviceIndex = Number(select.value) || 0;
      renderServicio();
    });

    bindServiceField("#svc-name", "name");
    bindServiceField("#svc-short", "short");
    bindServiceField("#svc-summary", "summary");
    bindServiceList("#svc-bullets", "bullets");
    bindServiceList("#svc-deliverables", "deliverables");

    $("#svc-real").addEventListener("change", function () {
      currentService().realPhoto = $("#svc-real").checked;
      setDirty(true);
    });

    pickImage({
      input: "#svc-plate-file",
      preview: "#svc-plate-preview",
      path: function () { return "assets/img/servicios/" + currentService().slug + ".jpg"; },
      width: 1200,
      height: 900,
      quality: 0.82,
      onPath: function (path) {
        currentService().plate = path;
        setDirty(true);
      }
    });

    $("#svc-add-step").addEventListener("click", function () {
      var service = currentService();
      service.steps = Array.isArray(service.steps) ? service.steps : [];
      service.steps.push({ title: "", text: "" });
      renderSteps();
      setDirty(true);
    });

    $("#svc-add-faq").addEventListener("click", function () {
      var service = currentService();
      service.faq = Array.isArray(service.faq) ? service.faq : [];
      service.faq.push({ q: "", a: "" });
      renderFaq();
      setDirty(true);
    });

    renderServicio();
  }


  /* ------------------------------------------------------------------ */
  /* Proyectos                                                           */
  /* ------------------------------------------------------------------ */
  function fieldWrap(labelText, control, hintText) {
    var wrap = document.createElement("div");
    wrap.className = "field";
    var label = document.createElement("label");
    label.textContent = labelText;
    wrap.appendChild(label);
    wrap.appendChild(control);
    if (hintText) {
      var hint = document.createElement("p");
      hint.className = "hint";
      hint.textContent = hintText;
      wrap.appendChild(hint);
    }
    return wrap;
  }

  function textInput(value, onInput, placeholder) {
    var input = document.createElement("input");
    input.type = "text";
    input.value = value || "";
    if (placeholder) input.placeholder = placeholder;
    input.addEventListener("input", function () { onInput(input.value); });
    return input;
  }

  function projectImagePath(project, index) {
    if (project.image && project.image.indexOf("assets/img/projects/") === 0) return project.image;
    return "assets/img/projects/" + slugify(project.title || "proyecto-" + (index + 1)) + ".jpg";
  }

  function projectCard(project, index) {
    var card = document.createElement("div");
    card.className = "card";

    var head = document.createElement("div");
    head.className = "row row--between";
    var title = document.createElement("h2");
    title.style.margin = "0";
    title.textContent = "Proyecto " + (index + 1) + (project.title ? " · " + project.title : "");
    var actions = document.createElement("div");
    actions.className = "row";
    actions.style.marginTop = "0";

    function button(label, handler) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "btn btn--ghost btn--sm";
      btn.textContent = label;
      btn.addEventListener("click", handler);
      return btn;
    }

    actions.appendChild(button("Subir", function () {
      if (index === 0) return;
      var projects = state.content.projects;
      projects.splice(index - 1, 0, projects.splice(index, 1)[0]);
      renderProjects();
      setDirty(true);
    }));
    actions.appendChild(button("Bajar", function () {
      var projects = state.content.projects;
      if (index >= projects.length - 1) return;
      projects.splice(index + 1, 0, projects.splice(index, 1)[0]);
      renderProjects();
      setDirty(true);
    }));
    actions.appendChild(button("Eliminar", function () {
      if (!window.confirm("¿Eliminar el proyecto “" + (project.title || "sin título") + "” del sitio?\nLa foto no se borra del disco.")) return;
      state.content.projects.splice(index, 1);
      renderProjects();
      setDirty(true);
    }));

    head.appendChild(title);
    head.appendChild(actions);
    card.appendChild(head);

    var media = document.createElement("div");
    media.className = "media";
    media.style.marginTop = "0.9rem";

    var preview = document.createElement("img");
    preview.className = "media__preview media__preview--wide";
    preview.alt = "Vista previa del proyecto " + (index + 1);
    preview.src = previewSrc(project.image || "assets/img/plate-arquitectura.svg");

    var body = document.createElement("div");
    body.className = "media__body";

    var fileLabel = document.createElement("label");
    fileLabel.className = "file";
    var fileInput = document.createElement("input");
    fileInput.type = "file";
    fileInput.accept = "image/*";
    var fileText = document.createElement("span");
    fileText.textContent = "Elegir foto…";
    fileLabel.appendChild(fileInput);
    fileLabel.appendChild(fileText);
    body.appendChild(fileLabel);

    var note = document.createElement("p");
    note.className = "hint";
    note.textContent = "Se recorta a 1600×1200 (4:3) y se guarda como JPG optimizado en assets/img/projects/.";
    body.appendChild(note);

    if (project.image) {
      var pathNote = document.createElement("p");
      pathNote.className = "hint";
      pathNote.textContent = "Archivo actual: " + project.image;
      body.appendChild(pathNote);
    }

    pickImage({
      el: fileInput,
      previewEl: preview,
      path: function () { return projectImagePath(project, index); },
      width: 1600,
      height: 1200,
      quality: 0.82,
      onPath: function (path) {
        project.image = path;
        if (!project.alt) project.alt = project.title || "";
        setDirty(true);
      }
    });

    media.appendChild(preview);
    media.appendChild(body);
    card.appendChild(media);

    var grid = document.createElement("div");
    grid.className = "grid grid--2";
    grid.style.marginTop = "0.9rem";

    grid.appendChild(fieldWrap("Título", textInput(project.title, function (value) {
      project.title = value;
      setDirty(true);
    }, "Casa Patio"), "Es el nombre visible de la ficha."));

    grid.appendChild(fieldWrap("Tipo de proyecto", textInput(project.type, function (value) {
      project.type = value;
      setDirty(true);
    }, "Vivienda unifamiliar")));

    grid.appendChild(fieldWrap("Ubicación", textInput(project.location, function (value) {
      project.location = value;
      setDirty(true);
    }, "Pereira, Risaralda")));

    grid.appendChild(fieldWrap("Año", textInput(project.year, function (value) {
      project.year = value;
      setDirty(true);
    }, "2025")));

    card.appendChild(grid);

    var alt = textInput(project.alt, function (value) {
      project.alt = value;
      setDirty(true);
    }, "Fachada de la vivienda con patio central");
    card.appendChild(fieldWrap("Texto alternativo de la foto", alt,
      "Describe la foto en una frase. Importante para accesibilidad y para Google."));

    var description = document.createElement("textarea");
    description.rows = 3;
    description.value = project.description || "";
    description.addEventListener("input", function () {
      project.description = description.value;
      setDirty(true);
    });
    card.appendChild(fieldWrap("Descripción breve", description,
      "Una o dos frases sobre el alcance real. Se muestra en la ficha y en Google."));

    return card;
  }

  function renderProjects() {
    var list = $("#projects-list");
    list.innerHTML = "";
    var projects = state.content.projects;
    $("#projects-count").textContent = projects.length
      ? projects.length + " proyecto(s) en el sitio"
      : "Ningún proyecto todavía";
    $("#projects-empty").hidden = projects.length > 0;
    projects.forEach(function (project, index) {
      list.appendChild(projectCard(project, index));
    });
  }

  function fillProjects() {
    $("#btn-add-project").addEventListener("click", function () {
      state.content.projects.push({
        title: "",
        type: "",
        location: "",
        year: "",
        image: "",
        alt: "",
        description: ""
      });
      renderProjects();
      setDirty(true);
      var cards = $("#projects-list").children;
      var last = cards[cards.length - 1];
      if (last) last.scrollIntoView({ behavior: "smooth", block: "center" });
    });
    renderProjects();
  }


  /* ------------------------------------------------------------------ */
  /* SEO                                                                 */
  /* ------------------------------------------------------------------ */
  function setSeo(page, field, value) {
    var seo = state.content.seo || (state.content.seo = {});
    var node = seo[page.key] || (seo[page.key] = {});
    var target = page.slug ? node[page.slug] || (node[page.slug] = {}) : node;
    target[field] = value;
    page[field] = value;
    setDirty(true);
  }

  function seoMeter(control, recommended, warnAt) {
    var meter = document.createElement("p");
    meter.className = "hint";
    function update() {
      var length = control.value.length;
      meter.textContent = length + " caracteres · recomendado hasta " + recommended;
      meter.className = "hint" + (length > warnAt ? " is-over" : length > recommended ? " is-warn" : "");
    }
    control.addEventListener("input", update);
    update();
    return meter;
  }

  function fillSeo() {
    var list = $("#seo-list");
    list.innerHTML = "";

    state.seo.forEach(function (page) {
      var card = document.createElement("div");
      card.className = "card";

      var head = document.createElement("div");
      head.className = "row row--between";
      var title = document.createElement("h2");
      title.style.margin = "0";
      title.textContent = page.label;
      var path = document.createElement("code");
      path.textContent = page.path;
      head.appendChild(title);
      head.appendChild(path);
      card.appendChild(head);

      var titleInput = document.createElement("input");
      titleInput.type = "text";
      titleInput.value = page.title || "";
      titleInput.maxLength = 90;
      titleInput.addEventListener("input", function () {
        setSeo(page, "title", titleInput.value);
      });
      card.appendChild(fieldWrap("Título para Google", titleInput));
      card.appendChild(seoMeter(titleInput, 60, 70));

      var description = document.createElement("textarea");
      description.rows = 3;
      description.value = page.description || "";
      description.maxLength = 220;
      description.addEventListener("input", function () {
        setSeo(page, "description", description.value);
      });
      var wrap = fieldWrap("Descripción para Google", description);
      wrap.style.marginTop = "0.7rem";
      card.appendChild(wrap);
      card.appendChild(seoMeter(description, 160, 180));

      var url = document.createElement("p");
      url.className = "hint";
      url.textContent = page.url;
      card.appendChild(url);

      list.appendChild(card);
    });
  }

  /* ------------------------------------------------------------------ */
  /* Publicar                                                            */
  /* ------------------------------------------------------------------ */
  function repoSlug() {
    return String((state.content.site.repo || ""))
      .trim()
      .replace(/^https?:\/\/github\.com\//i, "")
      .replace(/\.git$/i, "")
      .replace(/\/+$/, "");
  }

  function updateUploadLink() {
    var link = $("#upload-link");
    var slug = repoSlug();
    if (!slug || slug.indexOf("/") === -1) {
      link.removeAttribute("href");
      link.textContent = "Escribe arriba usuario/repositorio para obtener el enlace";
      return;
    }
    link.href = "https://github.com/" + slug + "/upload/main";
    link.textContent = "Abrir " + slug + " · Upload files";
  }

  function fillPublicar() {
    var site = state.content.site;
    if (site.repo == null) site.repo = "";
    var repo = $("#repo-input");
    repo.value = site.repo;
    repo.addEventListener("input", function () {
      site.repo = repo.value.trim();
      updateUploadLink();
      setDirty(true);
    });

    $("#btn-reset-changes").addEventListener("click", function () {
      state.changed = [];
      renderChanged();
      toast("Lista vacía: se subirá solo data/content.js.");
    });

    $("#btn-export").addEventListener("click", exportFiles);

    renderChanged();
    updateUploadLink();
  }

  function exportFiles() {
    if (state.dirty) {
      toast("Primero guarda los cambios: la carpeta se arma con lo que hay en disco.", "error");
      return;
    }
    setStatus("Preparando carpeta _publicar…");
    fetch("/api/export", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ files: state.changed })
    })
      .then(function (response) { return response.json(); })
      .then(function (result) {
        if (!result.ok) throw new Error(result.error || "No se pudo exportar.");
        var out = $("#export-result");
        out.hidden = false;
        out.textContent =
          "Carpeta lista: " + result.folder + " · " + result.files.length +
          " archivo(s). Arrástrala completa a la página de carga de GitHub.";
        setStatus("Carpeta _publicar lista", result.files.join(" · "));
        toast("Carpeta _publicar creada. Ábrela en el explorador y arrástrala a GitHub.", "ok");
      })
      .catch(function (error) { toast(error.message, "error"); });
  }


  /* ------------------------------------------------------------------ */
  /* Guardar, regenerar y vista previa                                   */
  /* ------------------------------------------------------------------ */
  function imagesPayload() {
    var payload = [];
    Object.keys(state.pending).forEach(function (path) {
      payload.push({ path: path, dataUrl: state.pending[path] });
    });
    return payload;
  }

  function save(options) {
    options = options || {};
    var button = $("#btn-save");
    button.disabled = true;
    setStatus("Guardando contenido y fotos…");

    fetch("/api/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: state.content, images: imagesPayload() })
    })
      .then(function (response) { return response.json(); })
      .then(function (result) {
        if (!result.ok) throw new Error(result.error || "No se pudo guardar.");
        result.files.forEach(markChanged);
        state.pending = {};
        CACHE_BUST += 1;
        setStatus("Regenerando páginas…");
        return fetch("/api/build", { method: "POST" });
      })
      .then(function (response) { return response.json(); })
      .then(function (result) {
        if (!result.ok) {
          throw new Error("El generador falló. Revisa el texto y vuelve a intentar.\n" + String(result.log || "").slice(-900));
        }
        setDirty(false);
        var lines = String(result.log || "").trim().split("\n");
        setStatus("Guardado · sitio regenerado", lines[lines.length - 1] || "");
        toast("Guardado y regenerado. Revisa la vista previa antes de publicar.", "ok");
        if (options.then) options.then();
      })
      .catch(function (error) {
        setStatus("Error al guardar");
        toast(error.message, "error");
      })
      .then(function () {
        button.disabled = false;
      });
  }

  function openPreview() {
    window.open("/preview/index.html?v=" + Date.now(), "_blank", "noopener");
  }

  function initTabs() {
    var tabs = document.querySelectorAll(".tab");

    function activate(name) {
      Array.prototype.forEach.call(tabs, function (tab) {
        var active = tab.getAttribute("data-tab") === name;
        tab.classList.toggle("is-active", active);
        tab.setAttribute("aria-selected", active ? "true" : "false");
      });
      Array.prototype.forEach.call(document.querySelectorAll(".panel"), function (panel) {
        panel.classList.toggle("is-active", panel.id === "tab-" + name);
      });
    }

    Array.prototype.forEach.call(tabs, function (tab) {
      tab.addEventListener("click", function () {
        activate(tab.getAttribute("data-tab"));
        if (window.history && window.history.replaceState) {
          window.history.replaceState(null, "", "?tab=" + tab.getAttribute("data-tab"));
        }
      });
    });

    var requested = new URLSearchParams(window.location.search).get("tab");
    if (requested && document.getElementById("tab-" + requested)) activate(requested);
  }

  function init() {
    initTabs();
    document.addEventListener("input", updateCounters);

    $("#btn-save").addEventListener("click", function () { save(); });
    $("#btn-preview").addEventListener("click", function () {
      if (state.dirty) save({ then: openPreview });
      else openPreview();
    });

    window.addEventListener("beforeunload", function (event) {
      if (!state.dirty) return undefined;
      event.preventDefault();
      event.returnValue = "";
      return "";
    });

    fetch("/api/state")
      .then(function (response) { return response.json(); })
      .then(function (data) {
        if (!data.ok) throw new Error(data.error || "El servidor no devolvió el contenido.");
        state.content = data.content;
        state.seo = data.seo;
        state.meta = data.meta;

        fillPortada();
        fillContacto();
        fillServicios();
        fillProjects();
        fillSeo();
        fillPublicar();

        setDirty(false);
        updateCounters();
        setStatus("Listo · " + (data.meta.git ? "repositorio git detectado" : "sin repositorio git todavía"),
          data.meta.root);
      })
      .catch(function (error) {
        setStatus("Sin conexión con el editor");
        toast(
          "No se pudo cargar el contenido: " + error.message +
          "\n\nAbre el panel con: python tools/editor.py",
          "error"
        );
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

