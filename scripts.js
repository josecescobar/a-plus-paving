(function () {
    'use strict';

    /* ── Mobile menu toggle ── */
    const toggle = document.getElementById('menu-toggle');
    const menu = document.getElementById('nav-menu');

    if (toggle && menu) {
        toggle.addEventListener('click', function (e) {
            e.stopPropagation();
            menu.classList.toggle('hidden');
            this.setAttribute('aria-expanded', String(!menu.classList.contains('hidden')));
        });

        document.addEventListener('click', function (e) {
            if (!menu.classList.contains('hidden') && !menu.contains(e.target) && e.target !== toggle) {
                menu.classList.add('hidden');
                toggle.setAttribute('aria-expanded', 'false');
            }
        });

        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && !menu.classList.contains('hidden')) {
                menu.classList.add('hidden');
                toggle.setAttribute('aria-expanded', 'false');
                toggle.focus();
            }
        });
    }

    /* ── Scroll-to-top button (throttled with rAF) ── */
    const scrollBtn = document.getElementById('scroll-top');

    if (scrollBtn) {
        let ticking = false;
        window.addEventListener('scroll', function () {
            if (!ticking) {
                window.requestAnimationFrame(function () {
                    scrollBtn.classList.toggle('visible', window.scrollY > 300);
                    ticking = false;
                });
                ticking = true;
            }
        });

        scrollBtn.addEventListener('click', function () {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
})();
