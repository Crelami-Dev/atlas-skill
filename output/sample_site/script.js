/* ==========================================================================
   Atlas Design System — Vanilla Interactive Components
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Accessible Mobile Navigation Toggle
  const navToggle = document.getElementById('navToggle');
  const navMenu = document.getElementById('navMenu');

  if (navToggle && navMenu) {
    navToggle.addEventListener('click', () => {
      const isOpen = navMenu.classList.toggle('open');
      navToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      navToggle.innerHTML = isOpen ? '✕' : '☰';
    });

    // Close menu when clicking outside or pressing Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && navMenu.classList.contains('open')) {
        navMenu.classList.remove('open');
        navToggle.setAttribute('aria-expanded', 'false');
        navToggle.innerHTML = '☰';
      }
    });

    // Close mobile menu on link navigation
    navMenu.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        if (navMenu.classList.contains('open')) {
          navMenu.classList.remove('open');
          navToggle.setAttribute('aria-expanded', 'false');
          navToggle.innerHTML = '☰';
        }
      });
    });
  }

  // 2. Accessible FAQ Accordions
  const faqItems = document.querySelectorAll('.faq-item');
  faqItems.forEach(item => {
    const question = item.querySelector('.faq-question');
    if (question) {
      question.addEventListener('click', () => {
        const isActive = item.classList.contains('active');
        
        // Close other items
        faqItems.forEach(other => {
          if (other !== item) {
            other.classList.remove('active');
            const otherBtn = other.querySelector('.faq-question');
            if (otherBtn) {
              otherBtn.setAttribute('aria-expanded', 'false');
              otherBtn.querySelector('span:last-child').textContent = '+';
            }
          }
        });

        // Toggle current item
        item.classList.toggle('active', !isActive);
        question.setAttribute('aria-expanded', !isActive ? 'true' : 'false');
        const icon = question.querySelector('span:last-child');
        if (icon) {
          icon.textContent = !isActive ? '−' : '+';
        }
      });
    }
  });
});
