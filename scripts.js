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

    /* ── Sticky mobile call / estimate bar ── */
    var cta = document.createElement('div');
    cta.id = 'mobile-cta';
    cta.className = 'mobile-cta';
    cta.setAttribute('role', 'region');
    cta.setAttribute('aria-label', 'Call or request an estimate');
    cta.innerHTML = ''
        + '<a class="mobile-cta-call" href="tel:+13045793872" aria-label="Call A+ Paving & Landscaping at (304) 579-3872">'
        + '<span class="mobile-cta-kicker">Call</span>'
        + '<span class="mobile-cta-number">(304) 579-3872</span>'
        + '</a>'
        + '<a class="mobile-cta-estimate" href="/contact" aria-label="Request a free estimate">Free estimate</a>';
    document.body.appendChild(cta);
    document.body.classList.add('has-mobile-cta');

    var footer = document.querySelector('footer');
    if (footer && 'IntersectionObserver' in window) {
        var footerWatcher = new IntersectionObserver(function (entries) {
            document.body.classList.toggle('footer-in-view', entries[0].isIntersecting);
        }, { threshold: 0.01 });
        footerWatcher.observe(footer);
    }

    /* ── Estimate forms (same /api/contact payload as before) ── */
    document.querySelectorAll('form.estimate-form').forEach(function (form) {
        var successBanner = form.parentElement.querySelector('.form-success');
        var errorBanner = form.parentElement.querySelector('.form-error');

        function fieldError(input) {
            return input.parentElement.querySelector('.field-error');
        }

        function clearField(input) {
            var err = fieldError(input);
            if (err) err.textContent = '';
            input.removeAttribute('aria-invalid');
        }

        function setFieldError(input, msg) {
            var err = fieldError(input);
            if (err) err.textContent = msg;
            input.setAttribute('aria-invalid', 'true');
        }

        form.addEventListener('submit', function (e) {
            e.preventDefault();
            if (errorBanner) {
                errorBanner.textContent = '';
                errorBanner.classList.add('hidden');
            }
            form.querySelectorAll('[name="name"], [name="email"], [name="message"]').forEach(clearField);

            var honeypot = form.querySelector('[name="company_website"]');
            if (honeypot && honeypot.value.trim()) {
                form.reset();
                form.classList.add('hidden');
                if (successBanner) successBanner.classList.remove('hidden');
                return;
            }

            var nameEl = form.querySelector('[name="name"]');
            var emailEl = form.querySelector('[name="email"]');
            var phoneEl = form.querySelector('[name="phone"]');
            var messageEl = form.querySelector('[name="message"]');
            var valid = true;

            if (!nameEl.value.trim()) {
                setFieldError(nameEl, 'Name is required.');
                valid = false;
            }
            if (!emailEl.value.trim() || !emailEl.validity.valid) {
                setFieldError(emailEl, 'A valid email is required.');
                valid = false;
            }
            if (!messageEl.value.trim()) {
                setFieldError(messageEl, 'Message is required.');
                valid = false;
            }
            if (!valid) return;

            var submitBtn = form.querySelector('[type="submit"]');
            var submitLabel = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.textContent = 'Sending...';

            fetch('/api/contact', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: nameEl.value.trim(),
                    email: emailEl.value.trim(),
                    phone: phoneEl ? phoneEl.value.trim() : '',
                    message: messageEl.value.trim()
                })
            }).then(function (response) {
                if (!response.ok) throw new Error('Submission failed');
                form.reset();
                form.classList.add('hidden');
                if (successBanner) successBanner.classList.remove('hidden');
            }).catch(function () {
                if (errorBanner) {
                    errorBanner.textContent = 'Something went wrong. Please try again or call us at (304) 579-3872.';
                    errorBanner.classList.remove('hidden');
                }
            }).finally(function () {
                submitBtn.disabled = false;
                submitBtn.textContent = submitLabel;
            });
        });
    });
})();
