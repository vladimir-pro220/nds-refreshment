/*
FICHIER : static/js/admin.js
RÔLE    : Scripts de l'interface d'administration
APPORT  : Gère le toggle sidebar, les confirmations de suppression,
          la prévisualisation d'images et les interactions admin.
DÉPENDANCES : admin.css, Bootstrap 5, admin_base.html
*/

document.addEventListener('DOMContentLoaded', function () {

  // ═══════════════════════════════════════════════════
  // SIDEBAR — TOGGLE MOBILE
  // ═══════════════════════════════════════════════════
  const toggleBtn = document.getElementById('toggleSidebar');
  const sidebar = document.getElementById('adminSidebar');

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', function () {
      sidebar.classList.toggle('show');
    });

    document.addEventListener('click', function (e) {
      if (!sidebar.contains(e.target) &&
          !toggleBtn.contains(e.target) &&
          sidebar.classList.contains('show')) {
        sidebar.classList.remove('show');
      }
    });
  }

  // ═══════════════════════════════════════════════════
  // FLASH MESSAGES — AUTO-HIDE APRÈS 5 SECONDES
  // ═══════════════════════════════════════════════════
  document.querySelectorAll('.admin-flash').forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });

  // ═══════════════════════════════════════════════════
  // PRÉVISUALISATION IMAGE PRODUIT
  // ═══════════════════════════════════════════════════
  const imageInput = document.getElementById('image');
  const imgPreview = document.getElementById('imgPreview');

  if (imageInput && imgPreview) {
    imageInput.addEventListener('change', function () {
      if (this.files && this.files[0]) {
        const reader = new FileReader();
        reader.onload = function (e) {
          imgPreview.src = e.target.result;
          imgPreview.style.opacity = '0';
          setTimeout(function () {
            imgPreview.style.transition = 'opacity 0.3s ease';
            imgPreview.style.opacity = '1';
          }, 50);
        };
        reader.readAsDataURL(this.files[0]);
      }
    });
  }

  // ═══════════════════════════════════════════════════
  // CONFIRMATIONS SUPPRESSION
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
  // TOGGLE DISPONIBILITÉ PRODUIT — SWITCH
  // ═══════════════════════════════════════════════════
  const disponibleSwitch = document.getElementById('disponible');
  if (disponibleSwitch) {
    const label = disponibleSwitch.nextElementSibling;
    disponibleSwitch.addEventListener('change', function () {
      if (label) {
        label.textContent = this.checked
          ? 'Produit visible sur le site'
          : 'Produit masqué du site';
      }
    });
  }

  // ═══════════════════════════════════════════════════
  // RECHERCHE ADMIN — SOUMISSION AUTO
  // ═══════════════════════════════════════════════════
  const adminSearch = document.querySelector('.admin-search-input');
  if (adminSearch) {
    let searchTimeout = null;
    adminSearch.addEventListener('input', function () {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(function () {
        adminSearch.closest('form').submit();
      }, 500);
    });
  }

  // ═══════════════════════════════════════════════════
  // TABLEAU — SÉLECTION MULTIPLE LIGNES
  // ═══════════════════════════════════════════════════
  const selectAll = document.getElementById('selectAll');
  if (selectAll) {
    selectAll.addEventListener('change', function () {
      document.querySelectorAll('.row-checkbox').forEach(function (cb) {
        cb.checked = selectAll.checked;
      });
      updateBulkActions();
    });

    document.querySelectorAll('.row-checkbox').forEach(function (cb) {
      cb.addEventListener('change', updateBulkActions);
    });
  }

  function updateBulkActions() {
    const checked = document.querySelectorAll('.row-checkbox:checked');
    const bulkBar = document.getElementById('bulkActionsBar');
    const bulkCount = document.getElementById('bulkCount');

    if (bulkBar) {
      bulkBar.style.display = checked.length > 0 ? 'flex' : 'none';
    }
    if (bulkCount) {
      bulkCount.textContent = checked.length;
    }
  }

  // ═══════════════════════════════════════════════════
  // VALIDATION FORMULAIRE NOUVEAU PRODUIT
  // ═══════════════════════════════════════════════════
  const formProduit = document.getElementById('formNouveauProduit') ||
                      document.getElementById('formModifierProduit');

  if (formProduit) {
    formProduit.addEventListener('submit', function (e) {
      const prix = formProduit.querySelector('[name="prix"]');
      const nom = formProduit.querySelector('[name="nom"]');
      const categorie = formProduit.querySelector('[name="categorie"]');

      let valid = true;
      let message = '';

      if (!nom || !nom.value.trim()) {
        valid = false;
        message = 'Le nom du produit est obligatoire.';
      } else if (!prix || parseFloat(prix.value) <= 0) {
        valid = false;
        message = 'Le prix doit être supérieur à 0.';
      } else if (!categorie || !categorie.value) {
        valid = false;
        message = 'Veuillez sélectionner une catégorie.';
      }

      if (!valid) {
        e.preventDefault();
        showAdminAlert(message, 'danger');
        return;
      }

      // Désactiver le bouton pour éviter double soumission
      const btn = formProduit.querySelector('[type="submit"]');
      if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Enregistrement...';
      }
    });
  }

  // ═══════════════════════════════════════════════════
  // VALIDATION FORMULAIRE PROMOTION
  // ═══════════════════════════════════════════════════
  const formPromo = document.getElementById('formPromotion');
  if (formPromo) {
    formPromo.addEventListener('submit', function (e) {
      const pourcentage = formPromo.querySelector('[name="pourcentage"]');
      const dateDebut = formPromo.querySelector('[name="date_debut"]');
      const dateFin = formPromo.querySelector('[name="date_fin"]');

      if (pourcentage && (parseFloat(pourcentage.value) < 1 ||
          parseFloat(pourcentage.value) > 99)) {
        e.preventDefault();
        showAdminAlert('Le pourcentage doit être entre 1 et 99.', 'danger');
        return;
      }

      if (dateDebut && dateFin) {
        const debut = new Date(dateDebut.value);
        const fin = new Date(dateFin.value);
        if (fin <= debut) {
          e.preventDefault();
          showAdminAlert(
            'La date de fin doit être après la date de début.', 'danger'
          );
          return;
        }
      }
    });
  }

  // ═══════════════════════════════════════════════════
  // ALERTE ADMIN DYNAMIQUE
  // ═══════════════════════════════════════════════════
  function showAdminAlert(message, type) {
    const existing = document.getElementById('adminDynamicAlert');
    if (existing) existing.remove();

    const alert = document.createElement('div');
    alert.id = 'adminDynamicAlert';
    alert.className = `alert alert-${type} alert-dismissible fade show
                       admin-flash`;
    alert.innerHTML = `
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      ${message}
      <button type="button" class="btn-close"
              data-bs-dismiss="alert"></button>`;

    const content = document.querySelector('.admin-content');
    if (content) {
      content.insertBefore(alert, content.firstChild);
      alert.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 5000);
  }

  // ═══════════════════════════════════════════════════
  // TABLEAU DE BORD — MISE À JOUR AUTOMATIQUE
  // ═══════════════════════════════════════════════════
  if (window.location.pathname.includes('/admin/dashboard')) {
    setInterval(async function () {
      try {
        const response = await fetch('/api/panier/count');
        if (response.ok) {
          // Vérification silencieuse — pas d'action visible
        }
      } catch (e) {
        // Silencieux
      }
    }, 60000); // Toutes les 60 secondes
  }

  // ═══════════════════════════════════════════════════
  // TOOLTIPS BOOTSTRAP
  // ═══════════════════════════════════════════════════
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
    new bootstrap.Tooltip(el);
  });

  // ═══════════════════════════════════════════════════
  // DATES MIN — FORMULAIRES PROMOTION
  // ═══════════════════════════════════════════════════
  const dateDebutInput = document.querySelector('[name="date_debut"]');
  const dateFinInput = document.querySelector('[name="date_fin"]');

  if (dateDebutInput && dateFinInput) {
    // Date minimum = aujourd'hui
    const today = new Date().toISOString().split('T')[0];
    dateDebutInput.min = today;
    dateFinInput.min = today;

    dateDebutInput.addEventListener('change', function () {
      dateFinInput.min = this.value;
      if (dateFinInput.value && dateFinInput.value <= this.value) {
        dateFinInput.value = '';
      }
    });
  }

});