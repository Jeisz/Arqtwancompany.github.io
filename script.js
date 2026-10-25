/* =========================================================
   ARQTWAN · Comportamiento del sitio
   Sin dependencias. Todo se inicializa de forma defensiva.
   ========================================================= */
(function () {
  "use strict";

  var doc = document;
  var root = doc.documentElement;
  var content = window.ARQTWAN || {};
  var site = content.site || {};
  var reduceMotion =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  root.classList.remove("no-js");

  /* ---------- Utilidades ---------- */
  function $(sel, ctx) {
    return (ctx || doc).querySelector(sel);
  }

  function $$(sel, ctx) {
    return Array.prototype.slice.call((ctx || doc).querySelectorAll(sel));
  }

  function on(el, evt, fn, opts) {
    if (el) el.addEventListener(evt, fn, opts || false);
  }

  function waLink(message) {
    var phone = (site.whatsapp || "").replace(/[^\d]/g, "");
    var base = "https://wa.me/" + phone;
    return message ? base + "?text=" + encodeURIComponent(message) : base;
  }

  function track(name, params) {
    try {
      doc.dispatchEvent(
        new CustomEvent("arqtwan:track", {
          detail: { name: name, params: params || {} }
        })
      );
      if (typeof window.gtag === "function") {
        window.gtag("event", name, params || {});
      }
    } catch (err) {
      /* la analitica nunca debe romper la pagina */
    }
  }

  /* ---------- Cabecera ---------- */
  function initHeader() {
    var header = $("[data-header]");
    if (!header) return;

    var onScroll = function () {
      header.classList.toggle("is-scrolled", window.scrollY > 24);
      var top = $("[data-back-top]");
      if (top) top.classList.toggle("is-visible", window.scrollY > 700);
    };

    onScroll();
    on(window, "scroll", onScroll, { passive: true });
  }

  /* ---------- Navegacion ---------- */
  function initNav() {
    var toggle = $("[data-nav-toggle]");
    var nav = $("[data-nav]");
    if (!toggle || !nav) return;

    function setOpen(open) {
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      nav.classList.toggle("is-open", open);
      doc.body.classList.toggle("is-locked", open);
    }

    on(toggle, "click", function () {
      setOpen(toggle.getAttribute("aria-expanded") !== "true");
    });

    on(doc, "keydown", function (e) {
      if (e.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") {
        setOpen(false);
        toggle.focus();
      }
    });

    on(window, "resize", function () {
      if (window.innerWidth > 980) setOpen(false);
    });

    $$(".nav a", nav).forEach(function (link) {
      on(link, "click", function () {
        if (window.innerWidth <= 980) setOpen(false);
      });
    });
  }

  /* ---------- Submenu de servicios ---------- */
  function initSubmenus() {
    $$("[data-submenu]").forEach(function (wrap) {
      var button = $("button", wrap);
      if (!button) return;

      function close() {
        wrap.classList.remove("is-open");
        button.setAttribute("aria-expanded", "false");
      }

      on(button, "click", function (e) {
        e.preventDefault();
        var open = wrap.classList.toggle("is-open");
        button.setAttribute("aria-expanded", open ? "true" : "false");
      });

      on(wrap, "mouseenter", function () {
        if (window.innerWidth > 980) {
          wrap.classList.add("is-open");
          button.setAttribute("aria-expanded", "true");
        }
      });

      on(wrap, "mouseleave", function () {
        if (window.innerWidth > 980) close();
      });

      on(doc, "click", function (e) {
        if (!wrap.contains(e.target)) close();
      });

      on(doc, "keydown", function (e) {
        if (e.key === "Escape") close();
      });
    });
  }

  /* ---------- Aparicion al hacer scroll ---------- */
  function initReveal() {
    var items = $$(".reveal");
    if (!items.length) return;

    if (!("IntersectionObserver" in window) || reduceMotion) {
      items.forEach(function (el) {
        el.classList.add("is-visible");
      });
      return;
    }

    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.12 }
    );

    items.forEach(function (el, i) {
      if (!el.style.getPropertyValue("--reveal-delay")) {
        el.style.setProperty("--reveal-delay", Math.min(i, 5) * 70 + "ms");
      }
      io.observe(el);
    });
  }

  /* ---------- Preguntas frecuentes ---------- */
  function initFaq() {
    $$("[data-faq]").forEach(function (group) {
      var items = $$("details", group);
      items.forEach(function (item) {
        on(item, "toggle", function () {
          if (!item.open) return;
          items.forEach(function (other) {
            if (other !== item) other.open = false;
          });
          var summary = $("summary", item);
          if (summary) {
            track("faq_open", { question: summary.textContent.trim().slice(0, 80) });
          }
        });
      });
    });
  }

  /* ---------- Volver arriba ---------- */
  function initBackTop() {
    var button = $("[data-back-top]");
    if (!button) return;
    on(button, "click", function () {
      window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
    });
  }

  /* ---------- Enlaces de WhatsApp ---------- */
  function initWhatsApp() {
    $$("[data-wa]").forEach(function (el) {
      var msg = el.getAttribute("data-wa") || "";
      el.setAttribute("href", waLink(msg));
      el.setAttribute("target", "_blank");
      el.setAttribute("rel", "noopener");
      on(el, "click", function () {
        track("whatsapp_click", {
          origen: el.getAttribute("data-wa-origen") || "sitio"
        });
      });
    });
  }

  /* ---------- Footer ---------- */
  function initYear() {
    $$("[data-year]").forEach(function (el) {
      el.textContent = String(new Date().getFullYear());
    });
  }

  /* ---------- Formulario de cotizacion ---------- */
  function initForms() {
    $$("[data-quote-form]").forEach(function (form) {
      var status = $("[data-form-status]", form);

      function setError(field, hasError) {
        if (!field) return;
        var wrap = field.closest(".field");
        if (wrap) wrap.classList.toggle("has-error", hasError);
        field.setAttribute("aria-invalid", hasError ? "true" : "false");
      }

      function show(kind, message) {
        if (!status) return;
        status.className = "form__status form__status--" + kind + " is-visible";
        status.textContent = message;
      }

      on(form, "submit", function (e) {
        e.preventDefault();

        var name = form.elements.namedItem("nombre");
        var phone = form.elements.namedItem("telefono");
        var service = form.elements.namedItem("servicio");
        var city = form.elements.namedItem("ciudad");
        var message = form.elements.namedItem("mensaje");
        var ok = true;

        if (!name || name.value.trim().length < 2) {
          setError(name, true);
          ok = false;
        } else {
          setError(name, false);
        }

        var digits = phone ? phone.value.replace(/[^\d]/g, "") : "";
        if (digits.length < 7) {
          setError(phone, true);
          ok = false;
        } else {
          setError(phone, false);
        }

        if (!ok) {
          show(
            "error",
            "Revisa tu nombre y un número de teléfono válido para poder responderte."
          );
          track("form_error", { motivo: "validacion" });
          return;
        }

        var lines = [
          "Hola Arqtwan, quiero cotizar un proyecto.",
          "",
          "Nombre: " + name.value.trim(),
          "Teléfono: " + phone.value.trim(),
          "Ciudad: " + (city && city.value.trim() ? city.value.trim() : "No indicada"),
          "Servicio: " + (service && service.value ? service.value : "Por definir")
        ];

        if (message && message.value.trim()) {
          lines.push("", "Detalle: " + message.value.trim());
        }

        var url = waLink(lines.join("\n"));
        var link = $("[data-form-fallback]", form);
        if (link) {
          link.href = url;
          link.hidden = false;
        }

        show(
          "ok",
          "Abrimos WhatsApp con tu solicitud lista para enviar. Si no se abre automáticamente, usa el enlace de abajo."
        );

        track("form_submit", {
          servicio: service && service.value ? service.value : "sin_definir"
        });

        window.open(url, "_blank", "noopener");
      });
    });
  }

  /* ---------- Proyectos publicados desde el panel ---------- */
  function initProjects() {
    var grid = $("[data-projects]");
    if (!grid) return;

    var items = Array.isArray(content.projects) ? content.projects.slice() : [];
    var empty = $("[data-projects-empty]");
    var note = $("[data-projects-note]");

    if (!items.length) {
      if (empty) empty.hidden = false;
      return;
    }

    if (empty) empty.hidden = true;
    if (note) note.hidden = false;

    /* Las fichas ya vienen renderizadas en el HTML (SEO). Solo se
       reconstruyen si la pagina no las incluye. */
    if (grid.children.length) return;

    grid.innerHTML = items
      .map(function (p, i) {
        var img = p.image || "assets/img/plate-arquitectura.svg";
        var title = p.title || "Proyecto";
        var sub = [p.type, p.location, p.year].filter(Boolean).join(" · ");
        var alt = String(p.alt || title).replace(/"/g, "&quot;");
        var desc = p.description
          ? '<p class="work-card__desc">' +
            String(p.description).replace(/</g, "&lt;") +
            "</p>"
          : "";
        return (
          '<article class="work-card reveal" style="--reveal-delay:' +
          Math.min(i, 5) * 60 +
          'ms">' +
          '<img class="work-card__img" src="' +
          img +
          '" alt="' +
          alt +
          '" loading="lazy" width="640" height="480">' +
          '<div class="work-card__meta"><h3 class="work-card__title">' +
          title +
          '</h3><p class="work-card__sub">' +
          sub +
          "</p>" +
          desc +
          "</div></article>"
        );
      })
      .join("");
  }

  /* ---------- Arranque ---------- */
  function init() {
    initHeader();
    initNav();
    initSubmenus();
    initReveal();
    initFaq();
    initBackTop();
    initWhatsApp();
    initYear();
    initForms();
    initProjects();
  }

  if (doc.readyState === "loading") {
    doc.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

})();
