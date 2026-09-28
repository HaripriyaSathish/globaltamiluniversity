/* =====================================================================
   Global Tamil University – main script
   ===================================================================== */
(function () {
    'use strict';

    const navbar = document.getElementById('navbar');
    if (!navbar) return;

    const toggle = navbar.querySelector('.navbar__toggle');
    const links = Array.from(navbar.querySelectorAll('.navbar__link'));

    /* ---------- Mobile menu ---------- */
    function setMenu(open) {
        navbar.classList.toggle('is-open', open);
        toggle.setAttribute('aria-expanded', String(open));
        toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    }

    if (toggle) {
        toggle.addEventListener('click', () => setMenu(!navbar.classList.contains('is-open')));
        navbar.querySelectorAll('.navbar__nav a').forEach(a => a.addEventListener('click', () => setMenu(false)));
        document.addEventListener('keydown', e => { if (e.key === 'Escape') setMenu(false); });
        document.addEventListener('click', e => { if (!navbar.contains(e.target)) setMenu(false); });
    }

    /* ---------- Shadow once the page scrolls ---------- */
    const onScroll = () => navbar.classList.toggle('is-scrolled', window.scrollY > 10);
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();

    /* ---------- Highlight the menu item of the section in view ----------
       Sections without their own menu link (e.g. Course Openings, Research Areas)
       count as part of the closest menu section above them. */
    const linkFor = {};
    links.forEach(link => {
        const hash = link.getAttribute('href') || '';
        if (hash.startsWith('#') && hash.length > 1) linkFor[hash.slice(1)] = link;
    });

    let current = null;
    const sections = Array.from(document.querySelectorAll('section[id]'))
        .map(target => {
            current = linkFor[target.id] || current;
            return current ? { link: current, target } : null;
        })
        .filter(Boolean);

    if ('IntersectionObserver' in window && sections.length) {
        const setActive = (link) => links.forEach(l => l.classList.toggle('is-active', l === link));
        const observer = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const match = sections.find(s => s.target === entry.target);
                    if (match) setActive(match.link);
                }
            });
        }, { rootMargin: '-45% 0px -50% 0px' });
        sections.forEach(s => observer.observe(s.target));
    }
})();

/* =====================================================================
   Gallery: category filter + full-size photo viewer
   ===================================================================== */
(function () {
    'use strict';

    const gallery = document.getElementById('gallery');
    if (!gallery) return;

    /* ---------- Filter ---------- */
    const buttons = gallery.querySelectorAll('.gallery__filter');
    const items = gallery.querySelectorAll('.gallery__item');

    buttons.forEach(btn => btn.addEventListener('click', () => {
        const filter = btn.dataset.filter;
        buttons.forEach(b => {
            const on = b === btn;
            b.classList.toggle('is-active', on);
            b.setAttribute('aria-pressed', String(on));
        });
        items.forEach(item => {
            const show = filter === 'all' || item.dataset.category === filter;
            item.classList.toggle('is-hidden', !show);
            if (show) {
                item.classList.add('is-entering');
                requestAnimationFrame(() => requestAnimationFrame(() => item.classList.remove('is-entering')));
            }
        });
    }));

    /* ---------- Lightbox ---------- */
    const box = document.getElementById('lightbox');
    if (!box) return;
    const img = box.querySelector('.lightbox__img');
    const label = box.querySelector('.lightbox__label');
    const title = box.querySelector('.lightbox__title');
    const text = box.querySelector('.lightbox__text');
    const closeBtn = box.querySelector('.lightbox__close');
    let lastFocus = null;

    function open(trigger) {
        if (!trigger.dataset.src) return;
        lastFocus = trigger;
        img.src = trigger.dataset.src;
        img.alt = trigger.querySelector('img') ? trigger.querySelector('img').alt : '';
        label.textContent = trigger.dataset.label || '';
        title.textContent = trigger.dataset.title || '';
        text.textContent = trigger.dataset.description || '';
        box.hidden = false;
        document.body.style.overflow = 'hidden';
        closeBtn.focus();
    }

    function close() {
        box.hidden = true;
        img.removeAttribute('src');
        document.body.style.overflow = '';
        if (lastFocus) lastFocus.focus();
    }

    gallery.querySelectorAll('.gallery__open').forEach(t => t.addEventListener('click', () => open(t)));
    closeBtn.addEventListener('click', close);
    box.addEventListener('click', e => { if (e.target === box) close(); });
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && !box.hidden) close(); });
})();

/* =====================================================================
   Forms (Apply + Contact): live validation + submit without page reload.
   Rules mirror website/forms.py (the server checks everything again).
   ===================================================================== */
(function () {
    'use strict';

    const MAX_YEAR = new Date().getFullYear() + 1;

    // Characters allowed while typing (anything else is removed instantly)
    const FILTERS = {
        name: /[^\p{L} .'\-]/gu,                     // letters, space, . ' -
        mobile: /\D/g,                                // digits only
        'mobile-optional': /\D/g,
        year: /\D/g,
        qualification: /[^A-Za-z0-9 .,()+\-/&']/g,
    };

    // Returns an error message, or '' when valid
    const RULES = {
        required: (v, el) => v ? '' : (el.dataset.msg || 'Please select an option.'),
        name: (v) => {
            if (!v) return 'Please enter your name.';
            if (!/^\p{L}+(?:(?:\. |[ .'\-])\p{L}+)*\.?$/u.test(v)) return 'Name can contain letters only (no numbers or symbols).';
            if (v.length < 2 || v.length > 60) return 'Name must be between 2 and 60 characters.';
            return '';
        },
        email: (v) => {
            if (!v) return 'Please enter your email address.';
            return /^[^\s@]+@[^\s@]+\.[A-Za-z]{2,}$/.test(v) ? '' : 'Please enter a valid email address.';
        },
        mobile: (v) => {
            if (!v) return 'Please enter your mobile number.';
            return /^[6-9]\d{9}$/.test(v) ? '' : 'Enter a valid 10-digit mobile number starting with 6, 7, 8 or 9.';
        },
        'mobile-optional': (v) => (!v || /^[6-9]\d{9}$/.test(v)) ? '' : 'Enter a valid 10-digit mobile number starting with 6, 7, 8 or 9.',
        qualification: (v) => {
            if (!v) return 'Please enter your highest qualification.';
            if (!/[A-Za-z]/.test(v)) return 'Use letters and numbers only, e.g. Higher Secondary or B.Sc.';
            if (v.length < 2) return 'Qualification must be at least 2 characters.';
            return '';
        },
        year: (v) => {
            if (!v) return 'Please enter your year of passing.';
            if (!/^\d{4}$/.test(v)) return 'Year must be 4 digits, e.g. 2026.';
            const y = Number(v);
            return (y >= 1950 && y <= MAX_YEAR) ? '' : 'Enter a year between 1950 and ' + MAX_YEAR + '.';
        },
        goals: (v) => v.length > 1000 ? 'Please keep this under 1000 characters.' : '',
        message: (v) => {
            if (!v) return 'Please enter your message.';
            if (v.length < 10) return 'Please write at least 10 characters.';
            return v.length > 1000 ? 'Please keep your message under 1000 characters.' : '';
        },
        checked: (v, el) => el.checked ? '' : 'Please agree to be contacted by the admissions team.',
    };

    function wrapperOf(el) { return el.closest('.form-field, .form-consent'); }

    function showError(el, msg) {
        const wrap = wrapperOf(el);
        const box = document.getElementById(el.id + '-error');
        if (wrap) wrap.classList.toggle('has-error', !!msg);
        el.setAttribute('aria-invalid', msg ? 'true' : 'false');
        if (box) {
            box.textContent = msg || '';
            box.hidden = !msg;
            if (msg) el.setAttribute('aria-describedby', box.id);
        }
    }

    function validate(el) {
        const rule = RULES[el.dataset.rule];
        if (!rule) return true;
        const value = el.type === 'checkbox' ? '' : el.value.trim().replace(/\s+/g, ' ');
        const msg = rule(value, el);
        showError(el, msg);
        return !msg;
    }

    function setAlert(form, type, text) {
        form.querySelectorAll('.form-alert').forEach(a => { a.hidden = true; a.textContent = ''; });
        if (!text) return;
        const box = form.querySelector('.form-alert--' + type);
        if (box) { box.textContent = text; box.hidden = false; box.scrollIntoView({ block: 'nearest', behavior: 'smooth' }); }
    }

    document.querySelectorAll('form.js-validate').forEach(form => {
        const fields = Array.from(form.querySelectorAll('[data-rule]'));
        const button = form.querySelector('[type="submit"]');

        fields.forEach(el => {
            // Block invalid characters as the user types / pastes
            const filter = FILTERS[el.dataset.rule];
            if (filter) {
                el.addEventListener('input', () => {
                    const clean = el.value.replace(filter, '');
                    if (clean !== el.value) {
                        const pos = el.selectionStart - (el.value.length - clean.length);
                        el.value = clean;
                        try { el.setSelectionRange(pos, pos); } catch (e) { /* not a text input */ }
                    }
                });
            }
            // Validate when leaving a field, then live while correcting it
            el.addEventListener('blur', () => { el.dataset.touched = '1'; validate(el); });
            el.addEventListener(el.tagName === 'SELECT' || el.type === 'checkbox' ? 'change' : 'input', () => {
                if (el.dataset.touched) validate(el);
            });
        });

        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            setAlert(form, null);

            const invalid = fields.filter(el => { el.dataset.touched = '1'; return !validate(el); });
            if (invalid.length) {
                invalid[0].focus();
                return;
            }

            button.classList.add('is-loading');
            button.disabled = true;
            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: new FormData(form),
                    headers: { 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json' },
                    credentials: 'same-origin',
                });
                const data = await response.json().catch(() => ({}));

                if (response.ok && data.ok) {
                    form.reset();
                    fields.forEach(el => { delete el.dataset.touched; showError(el, ''); });
                    setAlert(form, 'success', data.message);
                } else if (data.errors) {
                    let first = null;
                    Object.entries(data.errors).forEach(([name, msgs]) => {
                        const el = form.elements[name];
                        if (el && el.id) { showError(el, msgs[0]); first = first || el; }
                        else setAlert(form, 'error', msgs[0]);
                    });
                    if (first) first.focus();
                } else {
                    setAlert(form, 'error', 'Something went wrong. Please try again in a moment.');
                }
            } catch (err) {
                setAlert(form, 'error', 'Could not send. Please check your internet connection and try again.');
            } finally {
                button.classList.remove('is-loading');
                button.disabled = false;
            }
        });
    });

    /* Course "Apply Now" buttons pre-select the program in the Apply form */
    document.querySelectorAll('[data-program]').forEach(btn => btn.addEventListener('click', () => {
        const select = document.querySelector('#apply select[name="program"]');
        if (select && select.querySelector('option[value="' + btn.dataset.program + '"]')) {
            select.value = btn.dataset.program;
            if (select.dataset.touched) select.dispatchEvent(new Event('change'));
        }
    }));
})();
