/*
FICHIER : static/js/main.js
RÔLE    : Scripts globaux du site client
APPORT  : Gère les flash messages auto-hide, les animations scroll,
          la navbar au scroll et les interactions globales du site.
DÉPENDANCES : animations.css, Bootstrap 5
*/

document.addEventListener('DOMContentLoaded', function () {

  // ═══════════════════════════════════════════════════
  // FLASH MESSAGES — AUTO-HIDE APRÈS 5 SECONDES
  // ═══════════════════════════════════════════════════
  const flashAlerts = document.querySelectorAll('.flash-alert');
  flashAlerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });

  // ═══════════════════════════════════════════════════
  // NAVBAR — EFFET AU SCROLL
  // ═══════════════════════════════════════════════════
  const navbar = document.querySelector('.navbar-nds');
  if (navbar) {
    window.addEventListener('scroll', function () {
      if (window.scrollY > 50) {
        navbar.classList.add('navbar-scrolled');
      } else {
        navbar.classList.remove('navbar-scrolled');
      }
    });
  }

  // ═══════════════════════════════════════════════════
  // ANIMATIONS SCROLL — INTERSECTION OBSERVER
  // ═══════════════════════════════════════════════════
  const scrollElements = document.querySelectorAll(
    '.scroll-animate, .scroll-animate-left, ' +
    '.scroll-animate-right, .scroll-animate-scale'
  );

  if (scrollElements.length > 0) {
    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });

    scrollElements.forEach(function (el) {
      observer.observe(el);
    });
  }

  // ═══════════════════════════════════════════════════
  // SIDEBAR ADMIN — TOGGLE MOBILE
  // ═══════════════════════════════════════════════════
  const toggleBtn = document.getElementById('toggleSidebar');
  const sidebar = document.getElementById('adminSidebar');

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', function () {
      sidebar.classList.toggle('show');
    });

    // Fermer sidebar en cliquant ailleurs
    document.addEventListener('click', function (e) {
      if (!sidebar.contains(e.target) &&
          !toggleBtn.contains(e.target) &&
          sidebar.classList.contains('show')) {
        sidebar.classList.remove('show');
      }
    });
  }

  // ═══════════════════════════════════════════════════
  // BOUTONS AJOUTER AU PANIER — ANIMATION
  // ═══════════════════════════════════════════════════
  document.querySelectorAll('.btn-ajouter').forEach(function (btn) {
    btn.addEventListener('click', function () {
      btn.classList.add('adding');
      setTimeout(function () {
        btn.classList.remove('adding');
      }, 400);
    });
  });

  // ═══════════════════════════════════════════════════
  // CONFIRMATION SUPPRESSION GÉNÉRIQUE
  // ═══════════════════════════════════════════════════
  document.querySelectorAll('[data-confirm]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      const message = el.getAttribute('data-confirm');
      if (!confirm(message)) {
        e.preventDefault();
      }
    });
  });

  // ═══════════════════════════════════════════════════
  // SMOOTH SCROLL — ANCRES
  // ═══════════════════════════════════════════════════
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // ═══════════════════════════════════════════════════
  // RETOUR EN HAUT DE PAGE
  // ═══════════════════════════════════════════════════
  const btnTop = document.getElementById('btnScrollTop');
  if (btnTop) {
    window.addEventListener('scroll', function () {
      if (window.scrollY > 400) {
        btnTop.classList.add('visible');
      } else {
        btnTop.classList.remove('visible');
      }
    });

    btnTop.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // ═══════════════════════════════════════════════════
  // TOOLTIPS BOOTSTRAP
  // ═══════════════════════════════════════════════════
  const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  tooltips.forEach(function (el) {
    new bootstrap.Tooltip(el);
  });

  // ═══════════════════════════════════════════════════
  // PRÉVISUALISATION IMAGE GÉNÉRIQUE
  // ═══════════════════════════════════════════════════
  document.querySelectorAll('.input-img-preview').forEach(function (input) {
    input.addEventListener('change', function () {
      const previewId = input.getAttribute('data-preview');
      const preview = document.getElementById(previewId);
      if (preview && input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function (e) {
          preview.src = e.target.result;
        };
        reader.readAsDataURL(input.files[0]);
      }
    });
  });

  // ═══════════════════════════════════════════════════
  // COMPTEUR ANIMÉ — STATISTIQUES
  // ═══════════════════════════════════════════════════
  function animateCounter(el) {
    const target = parseInt(el.getAttribute('data-target'));
    const duration = 1500;
    const step = target / (duration / 16);
    let current = 0;

    const timer = setInterval(function () {
      current += step;
      if (current >= target) {
        current = target;
        clearInterval(timer);
      }
      el.textContent = Math.floor(current).toLocaleString('fr-FR');
    }, 16);
  }

  const counterObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        counterObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });

  document.querySelectorAll('[data-target]').forEach(function (el) {
    counterObserver.observe(el);
  });

});