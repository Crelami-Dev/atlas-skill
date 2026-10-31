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


    // Atlas Motion Adapter Runtime Integration
    (function() {
      const motionPlan = {
  "engine": "animejs-v4-with-css-fallback",
  "engineCompatibility": "Anime.js v4.x official runtime target; native CSS fallback when library is not loaded",
  "primaryPattern": "stillness",
  "patterns": [
    {
      "id": "stillness",
      "name": "Stillness (Intentional Restraint)",
      "intent": "Maximize clarity, respect reader attention, and communicate rigorous authority by deliberately abstaining from ambient or entrance animations.",
      "useCase": "Financial platforms, dense data applications, technical documentation, minimal luxury.",
      "trigger": "none",
      "targets": [
        "body",
        "main",
        ".app-shell"
      ],
      "timing": {
        "durationMs": 0,
        "delayMs": 0,
        "staggerMs": 0
      },
      "easing": {
        "token": "--ease-out",
        "bezier": "cubic-bezier(0.22, 1, 0.36, 1)",
        "animeName": "easeOutQuint"
      },
      "stagger": null,
      "reducedMotionFallback": {
        "behavior": "stillness",
        "description": "Native stillness matches reduced motion perfectly."
      },
      "performanceConsiderations": "Maximum performance: zero RAF loops, zero animation overhead, instant LCP.",
      "lifecycle": {
        "cleanupRequirements": "None; clean static render.",
        "removesListeners": false,
        "resetsTransform": false
      },
      "responsiveBehavior": "Consistently static across all form factors.",
      "sourceProvenance": {
        "sourceFile": "library/motions.json",
        "originalId": "stillness",
        "license": "MIT (Leonxlnx, 2026)"
      },
      "adapterConfig": {
        "css": {
          "transition": "none",
          "animation": "none"
        }
      }
    }
  ],
  "reducedMotionBehavior": "instant",
  "rationale": "Selected 'stillness' for high-density / application layout to maximize data readability and eliminate decorative distraction.",
  "tokens": {
    "easeOut": "cubic-bezier(0.22, 1, 0.36, 1)",
    "easeExpo": "cubic-bezier(0.16, 1, 0.3, 1)",
    "easeSoft": "cubic-bezier(0.33, 1, 0.68, 1)",
    "easeExit": "cubic-bezier(0.55, 0.055, 0.675, 0.19)",
    "durationRevealMs": 800,
    "durationHeroMs": 1100,
    "staggerLineMs": 110
  }
};
      
      function runMotion() {
        if (typeof AtlasMotionAdapter === 'undefined') {
          // Graceful fallback if adapter script failed to load
          document.querySelectorAll('.lines [data-line], .hero h1 [data-line]').forEach(el => {
            el.style.transform = 'none';
            el.style.opacity = '1';
          });
          return;
        }
        
        const adapter = new AtlasMotionAdapter();
        if (motionPlan.patterns && motionPlan.patterns.length > 0) {
          motionPlan.patterns.forEach(spec => {
            adapter.execute(spec);
          });
        }
        window.__atlasMotionAdapterInstance = adapter;
      }
      
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', runMotion);
      } else {
        runMotion();
      }
    })();
