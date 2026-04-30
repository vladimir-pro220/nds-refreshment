/*
FICHIER : static/js/cart.js
RÔLE    : Gestion du panier côté JavaScript
APPORT  : Met à jour le badge panier en temps réel via /api/panier/count
          et gère les interactions visuelles du panier sans rechargement.
DÉPENDANCES : api.py /api/panier/count, Bootstrap 5, main.css .panier-badge
*/

document.addEventListener('DOMContentLoaded', function () {

  // ═══════════════════════════════════════════════════
  // ÉLÉMENTS DOM
  // ═══════════════════════════════════════════════════
  const panierBadge = document.getElementById('panierCount');

  // ═══════════════════════════════════════════════════
  // MISE À JOUR BADGE PANIER
  // ═══════════════════════════════════════════════════
  async function updateCartBadge() {
    try {
      const response = await fetch('/api/panier/count');
      if (!response.ok) return;
      const data = await response.json();
      setCartBadge(data.count);
    } catch (error) {
      console.error('Erreur mise à jour panier:', error);
    }
  }

  function setCartBadge(count) {
    if (!panierBadge) return;
    panierBadge.textContent = count;

    if (count > 0) {
      panierBadge.style.display = 'flex';
      panierBadge.classList.add('animate-scale-in');
      setTimeout(() => panierBadge.classList.remove('animate-scale-in'), 400);
    } else {
      panierBadge.style.display = 'none';
    }
  }

  // ═══════════════════════════════════════════════════
  // SOUMISSION FORMULAIRES AJOUT PANIER — AJAX
  // ═══════════════════════════════════════════════════
  document.querySelectorAll('form[action*="ajouter"]').forEach(function (form) {
    form.addEventListener('submit', async function (e) {
      e.preventDefault();

      const btn = form.querySelector('.btn-ajouter');
      if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="bi bi-hourglass-split"></i>';
      }

      try {
        const formData = new FormData(form);
        const response = await fetch(form.action, {
          method: 'POST',
          body: formData,
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });

        if (response.ok) {
          // Mise à jour badge
          await updateCartBadge();

          // Animation succès sur le bouton
          if (btn) {
            btn.innerHTML = '<i class="bi bi-check-lg"></i>';
            btn.style.background = '#198754';
            setTimeout(function () {
              btn.innerHTML = '<i class="bi bi-bag-plus"></i>';
              btn.style.background = '';
              btn.disabled = false;
            }, 1200);
          }

          // Toast notification
          showCartToast('Produit ajouté au panier !');

        } else {
          if (btn) {
            btn.innerHTML = '<i class="bi bi-bag-plus"></i>';
            btn.disabled = false;
          }
          // Fallback — soumission classique
          form.submit();
        }

      } catch (error) {
        console.error('Erreur ajout panier:', error);
        if (btn) {
          btn.innerHTML = '<i class="bi bi-bag-plus"></i>';
          btn.disabled = false;
        }
        form.submit();
      }
    });
  });

  // ═══════════════════════════════════════════════════
  // TOAST NOTIFICATION PANIER
  // ═══════════════════════════════════════════════════
  function showCartToast(message) {
    // Supprimer toast existant
    const existing = document.getElementById('cartToast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.id = 'cartToast';
    toast.innerHTML = `
      <div class="cart-toast">
        <i class="bi bi-bag-check-fill me-2"></i>
        ${message}
        <a href="/panier" class="cart-toast-link ms-2">
          Voir le panier <i class="bi bi-arrow-right ms-1"></i>
        </a>
      </div>`;

    document.body.appendChild(toast);

    // Animation entrée
    setTimeout(() => toast.querySelector('.cart-toast').classList.add('show'), 10);

    // Auto-hide après 3 secondes
    setTimeout(function () {
      const cartToast = toast.querySelector('.cart-toast');
      if (cartToast) cartToast.classList.remove('show');
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }

  // ═══════════════════════════════════════════════════
  // STYLES TOAST
  // ═══════════════════════════════════════════════════
  const style = document.createElement('style');
  style.textContent = `
    .cart-toast {
      position: fixed;
      bottom: 2rem;
      right: 2rem;
      background: #1a1a2e;
      color: white;
      padding: 1rem 1.5rem;
      border-radius: 12px;
      font-size: 0.9rem;
      font-weight: 600;
      box-shadow: 0 8px 24px rgba(0,0,0,0.2);
      z-index: 9999;
      display: flex;
      align-items: center;
      transform: translateY(100px);
      opacity: 0;
      transition: all 0.3s ease;
      max-width: 360px;
    }
    .cart-toast.show {
      transform: translateY(0);
      opacity: 1;
    }
    .cart-toast-link {
      color: #f4a261;
      font-weight: 700;
      text-decoration: none;
      white-space: nowrap;
    }
    .cart-toast-link:hover {
      color: #f9c784;
      text-decoration: underline;
    }
  `;
  document.head.appendChild(style);

  // ═══════════════════════════════════════════════════
  // INITIALISATION — MISE À JOUR BADGE AU CHARGEMENT
  // ═══════════════════════════════════════════════════
  updateCartBadge();

});