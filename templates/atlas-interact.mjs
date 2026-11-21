/**
 * Atlas v7.2 — Small interactions that make a page feel alive without getting in the way.
 * Plain DOM, no dependencies. Everything is optional, opt-in by data attribute, and skipped under
 * prefers-reduced-motion or on touch pointers where it would be wrong.
 *
 *   data-magnetic        a button leans a few pixels toward the pointer
 *   data-tilt            a card tilts up to 3.5deg toward the pointer
 *   data-spotlight       sets --mx / --my on the element (pairs with .atlas-bg-spotlight)
 *   data-count="48"      counts up to the number when it scrolls into view (markup keeps the real value)
 *   data-cta-primary     hero action; with [data-mobile-bar] a phone action bar appears once it scrolls away
 */

const reduced = () => typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches;
const finePointer = () => typeof matchMedia === 'function' && matchMedia('(hover: hover) and (pointer: fine)').matches;

export function initAtlasInteract(options = {}) {
  const root = options.root || document;
  const cleanups = [];
  const on = (target, type, fn, opts) => {
    target.addEventListener(type, fn, opts);
    cleanups.push(() => target.removeEventListener(type, fn, opts));
  };

  // Spotlight works for any pointer, motion-safe because it only recolours a gradient.
  for (const el of root.querySelectorAll('[data-spotlight]')) {
    on(el, 'pointermove', (e) => {
      const r = el.getBoundingClientRect();
      el.style.setProperty('--mx', `${((e.clientX - r.left) / r.width) * 100}%`);
      el.style.setProperty('--my', `${((e.clientY - r.top) / r.height) * 100}%`);
    });
  }

  if (!reduced() && finePointer()) {
    for (const el of root.querySelectorAll('[data-magnetic]')) {
      const reach = Number(el.dataset.magnetic) || 8;
      on(el, 'pointermove', (e) => {
        const r = el.getBoundingClientRect();
        const dx = (e.clientX - (r.left + r.width / 2)) / (r.width / 2);
        const dy = (e.clientY - (r.top + r.height / 2)) / (r.height / 2);
        el.style.transform = `translate(${(dx * reach).toFixed(1)}px, ${(dy * reach).toFixed(1)}px)`;
      });
      on(el, 'pointerleave', () => { el.style.transform = ''; });
    }
    for (const el of root.querySelectorAll('[data-tilt]')) {
      on(el, 'pointermove', (e) => {
        const r = el.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width - 0.5;
        const y = (e.clientY - r.top) / r.height - 0.5;
        el.style.transform = `perspective(900px) rotateX(${(-y * 7).toFixed(2)}deg) rotateY(${(x * 7).toFixed(2)}deg)`;
      });
      on(el, 'pointerleave', () => { el.style.transform = ''; });
    }
  }

  // Count-up: the real value is already in the markup, so no-JS and reduced motion show the truth.
  const counters = [...root.querySelectorAll('[data-count]')];
  if (counters.length && !reduced() && typeof IntersectionObserver === 'function') {
    const locale = document.documentElement.lang || undefined;
    const fmt = new Intl.NumberFormat(locale);
    const io = new IntersectionObserver((entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        io.unobserve(entry.target);
        const el = entry.target;
        const end = Number(el.dataset.count);
        if (!Number.isFinite(end)) continue;
        const final = el.textContent;
        const started = performance.now();
        const duration = 1100;
        const tick = (now) => {
          const t = Math.min(1, (now - started) / duration);
          el.textContent = t < 1 ? fmt.format(Math.round(end * (1 - Math.pow(1 - t, 3)))) : final;
          if (t < 1) requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
      }
    }, { threshold: 0.6 });
    counters.forEach((el) => io.observe(el));
    cleanups.push(() => io.disconnect());
  }

  // Phone action bar: appears once the hero's primary action is no longer on screen.
  const bar = root.querySelector('[data-mobile-bar]');
  const hero = root.querySelector('[data-cta-primary]');
  if (bar && hero && typeof IntersectionObserver === 'function') {
    const io = new IntersectionObserver(([entry]) => { bar.hidden = entry.isIntersecting || entry.boundingClientRect.top > 0; });
    io.observe(hero);
    cleanups.push(() => io.disconnect());
  }

  return { destroy: () => cleanups.splice(0).forEach((fn) => fn()) };
}
