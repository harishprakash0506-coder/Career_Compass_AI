/**
 * main.js — CareerCompass AI Global JavaScript
 * ─────────────────────────────────────────────
 * Handles: sidebar toggle, flash auto-dismiss,
 *          stats counter animation, scroll reveals,
 *          progress bar animations.
 */

'use strict';

/* ── DOM-Ready Helper ──────────────────────────────────────────────── */
function ready(fn) {
  if (document.readyState !== 'loading') { fn(); }
  else { document.addEventListener('DOMContentLoaded', fn); }
}

ready(function () {

  /* ──────────────────────────────────────────────────────────────────
     1. Sidebar Toggle (mobile)
     ────────────────────────────────────────────────────────────────── */
  const sidebar      = document.getElementById('sidebar');
  const sidebarBtn   = document.getElementById('sidebar-toggle');
  const overlay      = document.getElementById('sidebar-overlay');

  if (sidebarBtn && sidebar) {
    sidebarBtn.addEventListener('click', function () {
      const isOpen = sidebar.classList.toggle('is-open');
      sidebarBtn.setAttribute('aria-expanded', String(isOpen));
      if (overlay) {
        overlay.style.display = isOpen ? 'block' : 'none';
        overlay.setAttribute('aria-hidden', String(!isOpen));
      }
    });
  }

  if (overlay) {
    overlay.addEventListener('click', closeSidebar);
  }

  function closeSidebar() {
    if (sidebar) sidebar.classList.remove('is-open');
    if (sidebarBtn) sidebarBtn.setAttribute('aria-expanded', 'false');
    if (overlay) {
      overlay.style.display = 'none';
      overlay.setAttribute('aria-hidden', 'true');
    }
  }

  // Inject overlay style once
  injectStyle(`
    #sidebar-overlay {
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.55);
      z-index: 1100;
      backdrop-filter: blur(2px);
    }
  `);

  /* ──────────────────────────────────────────────────────────────────
     2. Auto-dismiss Flash Messages (after 5 seconds)
     ────────────────────────────────────────────────────────────────── */
  document.querySelectorAll('.flash-container .alert').forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });

  /* ──────────────────────────────────────────────────────────────────
     3. Progress Bar Animate-on-View
     ────────────────────────────────────────────────────────────────── */
  const progressBars = document.querySelectorAll('.cc-progress-bar[style*="width"]');
  if (progressBars.length > 0 && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          const bar = entry.target;
          const targetWidth = bar.style.width;
          bar.style.width = '0%';
          requestAnimationFrame(function () {
            bar.style.transition = 'width 1s cubic-bezier(0.4, 0, 0.2, 1)';
            bar.style.width = targetWidth;
          });
          observer.unobserve(bar);
        }
      });
    }, { threshold: 0.3 });

    progressBars.forEach(function (bar) { observer.observe(bar); });
  }

  /* ──────────────────────────────────────────────────────────────────
     4. Animated Stats Counters (Landing Page)
     ────────────────────────────────────────────────────────────────── */
  const statsElements = document.querySelectorAll('[data-count]');

  if (statsElements.length > 0 && 'IntersectionObserver' in window) {
    const statsObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          statsObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });

    statsElements.forEach(function (el) { statsObserver.observe(el); });
  }

  function animateCounter(el) {
    const target   = parseInt(el.dataset.count, 10);
    const suffix   = el.dataset.suffix || '';
    const duration = 1800;
    const start    = performance.now();

    function update(now) {
      const elapsed  = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased    = 1 - Math.pow(1 - progress, 3); // ease-out-cubic
      const current  = Math.round(eased * target);
      el.textContent = current + suffix;
      if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
  }

  /* ──────────────────────────────────────────────────────────────────
     5. Scroll-reveal for Feature Cards
     ────────────────────────────────────────────────────────────────── */
  const revealCards = document.querySelectorAll('.feature-card, .cc-card');

  if (revealCards.length > 0 && 'IntersectionObserver' in window) {
    const revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.style.animation = 'fadeInUp 0.6s cubic-bezier(0.4,0,0.2,1) both';
          revealObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });

    revealCards.forEach(function (card) {
      card.style.opacity = '0';
      revealObserver.observe(card);
    });
  }

  /* ──────────────────────────────────────────────────────────────────
     6. SVG Score Ring — update stroke-dashoffset from data attribute
     ────────────────────────────────────────────────────────────────── */
  document.querySelectorAll('[data-score-ring]').forEach(function (ring) {
    const score  = parseFloat(ring.dataset.scoreRing) || 0;
    const fill   = ring.querySelector('.score-ring-fill');
    if (!fill) return;
    // Circumference = 2π × 54 ≈ 339.3
    const circumference = 339.3;
    const offset = circumference - (score / 100) * circumference;
    setTimeout(function () {
      fill.style.strokeDashoffset = offset;
    }, 300);
  });

  /* ──────────────────────────────────────────────────────────────────
     7. Global CSRF token helper for fetch() calls
     ────────────────────────────────────────────────────────────────── */
  window.getCsrfToken = function () {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
  };

  /**
   * Convenience wrapper around fetch() that injects the CSRF header
   * and returns parsed JSON. Used by chart data loaders in charts.js.
   *
   * @param {string} url
   * @param {object} options  — fetch options (method, body, etc.)
   * @returns {Promise<object>}
   */
  window.ccFetch = function (url, options) {
    options = options || {};
    options.headers = Object.assign({
      'Content-Type':  'application/json',
      'X-CSRFToken':   window.getCsrfToken(),
    }, options.headers || {});
    return fetch(url, options).then(function (res) {
      if (!res.ok) throw new Error('Network response was not ok: ' + res.status);
      return res.json();
    });
  };

  /* ──────────────────────────────────────────────────────────────────
     8. Tooltip initialisation (Bootstrap)
     ────────────────────────────────────────────────────────────────── */
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
    new bootstrap.Tooltip(el);
  });

  /* ──────────────────────────────────────────────────────────────────
     9. Active nav highlight for current page
     ────────────────────────────────────────────────────────────────── */
  const currentPath = window.location.pathname;
  document.querySelectorAll('.sidebar .nav-item').forEach(function (link) {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active');
    }
  });

});

/* ── Utility: inject a <style> block once ──────────────────────────── */
function injectStyle(css) {
  const style = document.createElement('style');
  style.textContent = css;
  document.head.appendChild(style);
}
