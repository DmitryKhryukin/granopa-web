/* Минимум ванильного JS. Без него сайт полностью работает —
   просто без анимации появления и без сворачивания меню. */

// ── Мобильное меню ───────────────────────────────────────────────────
const toggle = document.querySelector('.nav-toggle');
const mobileNav = document.getElementById('mobile-nav');

if (toggle && mobileNav) {
  toggle.addEventListener('click', () => {
    const open = mobileNav.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(open));
  });
  // Закрываем меню после перехода по ссылке
  mobileNav.querySelectorAll('a').forEach((a) =>
    a.addEventListener('click', () => {
      mobileNav.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
    })
  );
}

// ── Плавное появление блоков при скролле ─────────────────────────────
const revealables = document.querySelectorAll('[data-reveal]');

if ('IntersectionObserver' in window && revealables.length) {
  const io = new IntersectionObserver(
    (entries, obs) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          obs.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12, rootMargin: '0px 0px -8% 0px' }
  );
  revealables.forEach((el) => io.observe(el));
} else {
  // Нет поддержки — показываем сразу
  revealables.forEach((el) => el.classList.add('is-visible'));
}
