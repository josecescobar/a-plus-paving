(function () {
    'use strict';

    /* ── Mobile menu toggle ── */
    const toggle = document.getElementById('menu-toggle');
    const menu = document.getElementById('nav-menu');

    if (toggle && menu) {
        function openMenu() {
            menu.classList.remove('hidden');
            menu.classList.add('flex');
            toggle.setAttribute('aria-expanded', 'true');
        }

        function closeMenu() {
            menu.classList.add('hidden');
            menu.classList.remove('flex');
            toggle.setAttribute('aria-expanded', 'false');
        }

        toggle.addEventListener('click', function (e) {
            e.stopPropagation();
            if (menu.classList.contains('hidden')) {
                openMenu();
            } else {
                closeMenu();
            }
        });

        /* Close when clicking outside */
        document.addEventListener('click', function (e) {
            if (!menu.classList.contains('hidden') && !menu.contains(e.target) && !toggle.contains(e.target)) {
                closeMenu();
            }
        });

        /* Close on Escape key */
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && !menu.classList.contains('hidden')) {
                closeMenu();
                toggle.focus();
            }
        });

        /* Close when a nav link is tapped on mobile */
        menu.querySelectorAll('a').forEach(function (link) {
            link.addEventListener('click', function () {
                if (window.innerWidth < 768) {
                    closeMenu();
                }
            });
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
