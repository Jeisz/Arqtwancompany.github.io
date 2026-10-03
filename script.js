/* ==========================================================
   ARQTWAN V2
   JavaScript principal
========================================================== */


document.addEventListener("DOMContentLoaded", () => {


    /* ========================================================
       ELEMENTOS
    ======================================================== */

    const header =
        document.getElementById("site-header");

    const menuToggle =
        document.getElementById("menu-toggle");

    const menu =
        document.getElementById("main-menu");

    const form =
        document.getElementById("form-tramite");

    const year =
        document.getElementById("current-year");



    /* ========================================================
       AÑO AUTOMÁTICO
    ======================================================== */

    if (year) {

        year.textContent =
            new Date().getFullYear();

    }



    /* ========================================================
       HEADER AL HACER SCROLL
    ======================================================== */

    function updateHeader() {

        if (!header) {
            return;
        }


        if (window.scrollY > 20) {

            header.classList.add("scrolled");

        } else {

            header.classList.remove("scrolled");

        }

    }


    window.addEventListener(
        "scroll",
        updateHeader,
        {
            passive: true
        }
    );


    updateHeader();



    /* ========================================================
       MENÚ MOBILE
    ======================================================== */

    if (menuToggle && menu) {

        menuToggle.addEventListener(
            "click",
            () => {

                const isOpen =
                    menu.classList.toggle("active");


                menuToggle.classList.toggle(
                    "active",
                    isOpen
                );


                menuToggle.setAttribute(
                    "aria-expanded",
                    String(isOpen)
                );


                if (isOpen) {

                    document.body.style.overflow =
                        "hidden";

                } else {

                    document.body.style.overflow =
                        "";

                }

            }
        );



        const menuLinks =
            menu.querySelectorAll("a");


        menuLinks.forEach(link => {

            link.addEventListener(
                "click",
                () => {

                    menu.classList.remove("active");

                    menuToggle.classList.remove(
                        "active"
                    );

                    menuToggle.setAttribute(
                        "aria-expanded",
                        "false"
                    );

                    document.body.style.overflow =
                        "";

                }
            );

        });

    }



    /* ========================================================
       SCROLL SUAVE
    ======================================================== */

    const anchorLinks =
        document.querySelectorAll(
            'a[href^="#"]'
        );


    anchorLinks.forEach(link => {

        link.addEventListener(
            "click",
            event => {

                const href =
                    link.getAttribute("href");


                if (!href || href === "#") {

                    return;

                }


                const target =
                    document.querySelector(href);


                if (!target) {

                    return;

                }


                event.preventDefault();


                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });

            }
        );

    });



    /* ========================================================
       FORMULARIO
    ======================================================== */

    if (form) {

        const fields =
            form.querySelectorAll(
                "input, textarea, select"
            );



        /* ======================================================
           QUITAR ERROR AL ESCRIBIR
        ====================================================== */

        fields.forEach(field => {

            const removeError = () => {

                const fieldContainer =
                    field.closest(".field");


                if (fieldContainer) {

                    fieldContainer.classList.remove(
                        "invalid"
                    );

                }

            };


            field.addEventListener(
                "input",
                removeError
            );


            field.addEventListener(
                "change",
                removeError
            );

        });



        /* ======================================================
           SUBMIT
        ====================================================== */

        form.addEventListener(
            "submit",
            event => {

                event.preventDefault();


                let isValid =
                    true;


                const requiredFields =
                    form.querySelectorAll(
                        "[required]"
                    );



                requiredFields.forEach(field => {

                    const fieldContainer =
                        field.closest(".field");


                    if (!field.checkValidity()) {

                        isValid =
                            false;


                        if (fieldContainer) {

                            fieldContainer.classList.add(
                                "invalid"
                            );

                        }

                    } else {

                        if (fieldContainer) {

                            fieldContainer.classList.remove(
                                "invalid"
                            );

                        }

                    }

                });



                /* ==================================================
                   SI HAY ERRORES
                ================================================== */

                if (!isValid) {

                    const firstInvalid =
                        form.querySelector(
                            ":invalid"
                        );


                    if (firstInvalid) {

                        firstInvalid.focus();

                    }


                    return;

                }



                /* ==================================================
                   DATOS
                ================================================== */

                const name =
                    document
                        .getElementById("name")
                        .value
                        .trim();


                const phone =
                    document
                        .getElementById("phone")
                        .value
                        .trim();


                const email =
                    document
                        .getElementById("email")
                        .value
                        .trim();


                const service =
                    document
                        .getElementById("service")
                        .value
                        .trim();


                const message =
                    document
                        .getElementById("message")
                        .value
                        .trim();



                /* ==================================================
                   MENSAJE WHATSAPP
                ================================================== */

                const whatsappMessage =
                    `Hola Arqtwan,

Quiero recibir orientación sobre un proyecto.

Nombre: ${name}
Teléfono: ${phone}
Correo: ${email}
Servicio: ${service}

Descripción del proyecto:
${message}

Enviado desde arqtwan.com`;



                /* ==================================================
                   URL WHATSAPP
                ================================================== */

                const whatsappNumber =
                    "573043018508";


                const encodedMessage =
                    encodeURIComponent(
                        whatsappMessage
                    );


                const whatsappUrl =
                    `https://wa.me/${whatsappNumber}?text=${encodedMessage}`;



                /* ==================================================
                   ABRIR WHATSAPP
                ================================================== */

                window.open(
                    whatsappUrl,
                    "_blank",
                    "noopener,noreferrer"
                );

            }
        );

    }



    /* ========================================================
       FAQ
       Solo una pregunta abierta a la vez
    ======================================================== */

    const faqItems =
        document.querySelectorAll(
            ".faq-item"
        );


    faqItems.forEach(item => {

        item.addEventListener(
            "toggle",
            () => {

                if (!item.open) {

                    return;

                }


                faqItems.forEach(otherItem => {

                    if (otherItem !== item) {

                        otherItem.removeAttribute(
                            "open"
                        );

                    }

                });

            }
        );

    });


});