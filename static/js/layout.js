console.clear()
const { gsap } = window
const button = document.querySelector("button")
const nav = document.getElementById("mainNav")
let active = false

const openTl = gsap.timeline({ paused: true })
const closeTl = gsap.timeline({ paused: true })

openTl
    .set(".btn", { pointerEvents: "none" })
    .set("nav", { pointerEvents: "all" })
    .to("nav", {
        "clip-path": "circle(200% at 60px 60px)",
        duration: 1.5,
        ease: "power4.out",
    }, 0)
    .to("nav li", {
        x: 0,
        opacity: 1,
        pointerEvents: "all",
        duration: 1.25,
        stagger: 0.1,
        ease: "elastic.out(1.15, .95)",
    }, 0)
    .to(".btn .close", {
        opacity: 1,
        yPercent: -125,
        duration: 1,
        ease: "power4.out",
    }, 0)
    .to(".btn .line", {
        opacity: 0,
        yPercent: -125,
        duration: 1,
        ease: "power4.out",
    }, 0)
    .set(".btn", { pointerEvents: "all" })

closeTl
    .set(".btn", { pointerEvents: "none" })
    .to("nav li", {
        x: -200,
        opacity: 0,
        pointerEvents: "none",
        duration: 1,
        stagger: 0.1,
        ease: "power4.out",
    }, 0)
    .to("nav", {
        "clip-path": "circle(0px at 60px 60px)",
        duration: 1.2,
        ease: "power4.out",
    }, "-=1")
    .set("nav", { pointerEvents: "none" })
    .to(".btn--bg", {
        scale: 0.9,
        duration: 0.25,
        ease: "elastic.out",
    }, "-=.9")
    .to(".btn--bg", {
        scale: 1,
        duration: 0.25,
        ease: "elastic.out",
    }, "-=.5")
    .to(".btn .close", {
        opacity: 0,
        yPercent: 125,
        duration: 1,
        ease: "power4.out",
    }, 0)
    .to(".btn .line", {
        opacity: 1,
        yPercent: 0,
        duration: 1,
        ease: "power4.out",
    }, 0)
    .set(".btn", { pointerEvents: "all" })

button.addEventListener("click", () => {
    if (!active) openTl.seek(0).play()
    else closeTl.seek(0).play()
    active = !active
})


// Mantén todo tu código GSAP anterior y agrega esto al final:

// Toggle del menú de usuario con click (opcional, para móviles)
const userBtn = document.querySelector('.user-btn');
const userMenu = document.querySelector('.user-menu');

if (userBtn && userMenu) {
    userBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        userMenu.classList.toggle('active');
    });

    // Cerrar al hacer click fuera
    document.addEventListener('click', (e) => {
        if (!userMenu.contains(e.target)) {
            userMenu.classList.remove('active');
        }
    });
}


setTimeout(function () {
    const alerts = document.querySelectorAll('.flash-alert');
    alerts.forEach(function (alert) {
        alert.style.transition = 'opacity 0.5s, transform 0.5s';
        alert.style.opacity = '0';
        alert.style.transform = 'translateX(100px)';
        setTimeout(() => alert.remove(), 500);
    });
}, 3000);


// Control de visibilidad del logo y buscador al hacer scroll
const logo = document.querySelector('.logo');
const searchBar = document.querySelector('.top-search-bar');
let lastScrollTop = 0;

window.addEventListener('scroll', () => {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

    if (scrollTop > 50) {
        if (logo) logo.classList.add('hidden');
        if (searchBar) searchBar.classList.add('hidden');
    } else {
        if (logo) logo.classList.remove('hidden');
        if (searchBar) searchBar.classList.remove('hidden');
    }

    lastScrollTop = scrollTop;
});
