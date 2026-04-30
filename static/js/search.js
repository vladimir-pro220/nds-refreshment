/*
FICHIER : static/js/search.js
RÔLE    : Recherche live de produits via l'API REST
APPORT  : Interroge /api/search à chaque frappe et affiche les résultats
          dans un dropdown dynamique sans rechargement de page.
DÉPENDANCES : api.py /api/search, Bootstrap 5, main.css search-dropdown
*/

document.addEventListener('DOMContentLoaded', function () {

  // ═══════════════════════════════════════════════════
  // ÉLÉMENTS DOM
  // ═══════════════════════════════════════════════════
  const searchInput = document.getElementById('searchInput');
  const searchResults = document.getElementById('searchResults');
  const searchInputMobile = document.getElementById('searchInputMobile');
  const searchResultsMobile = document.getElementById('searchResultsMobile');

  if (!searchInput || !searchResults) return;

  // ═══════════════════════════════════════════════════
  // VARIABLES
  // ═══════════════════════════════════════════════════
  let searchTimeout = null;
  const MIN_CHARS = 2;
  const DEBOUNCE_DELAY = 350;

  // ═══════════════════════════════════════════════════
  // FONCTION RECHERCHE PRINCIPALE
  // ═══════════════════════════════════════════════════
  async function performSearch(query, resultsContainer) {
    if (!query || query.length < MIN_CHARS) {
      hideResults(resultsContainer);
      return;
    }

    // Afficher indicateur de chargement
    showLoading(resultsContainer);

    try {
      const response = await fetch(
        `/api/search?q=${encodeURIComponent(query)}&limit=8`
      );

      if (!response.ok) throw new Error('Erreur réseau');

      const data = await response.json();
      renderResults(data.produits, query, resultsContainer);

    } catch (error) {
      console.error('Erreur recherche:', error);
      showError(resultsContainer);
    }
  }

  // ═══════════════════════════════════════════════════
  // RENDU DES RÉSULTATS
  // ═══════════════════════════════════════════════════
  function renderResults(produits, query, container) {
    container.innerHTML = '';

    if (produits.length === 0) {
      container.innerHTML = `
        <div class="search-empty">
          <i class="bi bi-search me-2"></i>
          Aucun résultat pour « ${escapeHtml(query)} »
        </div>`;
      showResults(container);
      return;
    }

    // En-tête résultats
    const header = document.createElement('div');
    header.className = 'search-header';
    header.innerHTML = `
      <span>${produits.length} résultat(s) pour « ${escapeHtml(query)} »</span>
      <a href="/produits?q=${encodeURIComponent(query)}" class="search-voir-tout">
        Voir tout <i class="bi bi-arrow-right ms-1"></i>
      </a>`;
    container.appendChild(header);

    // Liste des produits
    produits.forEach(function (produit) {
      const item = document.createElement('a');
      item.href = produit.url;
      item.className = 'search-result-item';

      const prixHtml = produit.prix_promo
        ? `<span class="search-prix-barre">${formatPrix(produit.prix)}</span>
           <span class="search-prix-promo">${formatPrix(produit.prix_promo)}</span>
           <span class="search-badge-promo">-${produit.pourcentage_promo}%</span>`
        : `<span class="search-prix">${formatPrix(produit.prix)}</span>`;

      const starsHtml = produit.note_moyenne > 0
        ? `<span class="search-stars">${'★'.repeat(Math.round(produit.note_moyenne))}${'☆'.repeat(5 - Math.round(produit.note_moyenne))}</span>`
        : '';

      item.innerHTML = `
        <img src="/static/uploads/${produit.image}"
             alt="${escapeHtml(produit.nom)}"
             class="search-result-img"
             onerror="this.src='/static/img/default.jpg'"/>
        <div class="search-result-info">
          <span class="search-result-nom">
            ${highlightQuery(produit.nom, query)}
          </span>
          <span class="search-result-categorie">${escapeHtml(produit.categorie)}</span>
          <div class="search-result-prix">
            ${prixHtml}
            ${starsHtml}
          </div>
        </div>`;

      container.appendChild(item);
    });

    // Lien voir tout en bas
    const footer = document.createElement('a');
    footer.href = `/produits?q=${encodeURIComponent(query)}`;
    footer.className = 'search-footer';
    footer.innerHTML = `
      <i class="bi bi-grid me-2"></i>
      Voir tous les résultats pour « ${escapeHtml(query)} »`;
    container.appendChild(footer);

    showResults(container);
  }

  // ═══════════════════════════════════════════════════
  // ÉTAT CHARGEMENT
  // ═══════════════════════════════════════════════════
  function showLoading(container) {
    container.innerHTML = `
      <div class="search-loading">
        <div class="spinner-nds" style="width:24px;height:24px;
             border-width:3px;"></div>
        <span>Recherche en cours...</span>
      </div>`;
    showResults(container);
  }

  function showError(container) {
    container.innerHTML = `
      <div class="search-empty">
        <i class="bi bi-exclamation-triangle me-2 text-warning"></i>
        Une erreur est survenue. Réessayez.
      </div>`;
    showResults(container);
  }

  // ═══════════════════════════════════════════════════
  // AFFICHER / MASQUER DROPDOWN
  // ═══════════════════════════════════════════════════
  function showResults(container) {
    container.classList.add('show');
  }

  function hideResults(container) {
    container.classList.remove('show');
    container.innerHTML = '';
  }

  // ═══════════════════════════════════════════════════
  // UTILITAIRES
  // ═══════════════════════════════════════════════════
  function formatPrix(prix) {
    return new Intl.NumberFormat('fr-FR').format(prix) + ' FCFA';
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
  }

  function highlightQuery(text, query) {
    const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`(${escaped})`, 'gi');
    return escapeHtml(text).replace(regex,
      '<mark class="search-highlight">$1</mark>');
  }

  // ═══════════════════════════════════════════════════
  // ÉVÉNEMENTS CLAVIER — DEBOUNCE
  // ═══════════════════════════════════════════════════
  searchInput.addEventListener('input', function () {
    const query = this.value.trim();

    clearTimeout(searchTimeout);

    if (query.length < MIN_CHARS) {
      hideResults(searchResults);
      return;
    }

    searchTimeout = setTimeout(function () {
      performSearch(query, searchResults);
    }, DEBOUNCE_DELAY);
  });

  // Navigation clavier dans les résultats
  searchInput.addEventListener('keydown', function (e) {
    const items = searchResults.querySelectorAll('.search-result-item');
    const focused = searchResults.querySelector('.search-result-item:focus');
    const index = Array.from(items).indexOf(focused);

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (index < items.length - 1) {
        items[index + 1].focus();
      } else if (items.length > 0) {
        items[0].focus();
      }
    }

    if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (index > 0) {
        items[index - 1].focus();
      } else {
        searchInput.focus();
      }
    }

    if (e.key === 'Escape') {
      hideResults(searchResults);
      searchInput.blur();
    }

    if (e.key === 'Enter' && query.length >= MIN_CHARS) {
      window.location.href = `/produits?q=${encodeURIComponent(
        searchInput.value.trim()
      )}`;
    }
  });

  // ═══════════════════════════════════════════════════
  // FERMER AU CLIC EXTÉRIEUR
  // ═══════════════════════════════════════════════════
  document.addEventListener('click', function (e) {
    const wrapper = document.querySelector('.search-wrapper');
    if (wrapper && !wrapper.contains(e.target)) {
      hideResults(searchResults);
    }
  });

  // ═══════════════════════════════════════════════════
  // STYLES INLINE POUR LE DROPDOWN
  // ═══════════════════════════════════════════════════
  const style = document.createElement('style');
  style.textContent = `
    .search-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.6rem 1rem;
      font-size: 0.78rem;
      color: #6c757d;
      border-bottom: 1px solid #f0f0f0;
      background: #f8f9fa;
    }
    .search-voir-tout {
      color: #2d6a4f;
      font-weight: 600;
      text-decoration: none;
      font-size: 0.78rem;
    }
    .search-result-info {
      flex: 1;
      min-width: 0;
    }
    .search-result-nom {
      display: block;
      font-weight: 600;
      font-size: 0.9rem;
      color: #1a1a2e;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .search-result-categorie {
      display: block;
      font-size: 0.75rem;
      color: #6c757d;
      text-transform: capitalize;
    }
    .search-result-prix {
      display: flex;
      align-items: center;
      gap: 0.4rem;
      margin-top: 0.2rem;
    }
    .search-prix {
      font-weight: 700;
      font-size: 0.85rem;
      color: #2d6a4f;
    }
    .search-prix-promo {
      font-weight: 700;
      font-size: 0.85rem;
      color: #e76f51;
    }
    .search-prix-barre {
      font-size: 0.75rem;
      color: #adb5bd;
      text-decoration: line-through;
    }
    .search-badge-promo {
      background: #e76f51;
      color: white;
      font-size: 0.65rem;
      font-weight: 800;
      padding: 0.1rem 0.4rem;
      border-radius: 20px;
    }
    .search-stars {
      color: #ffc107;
      font-size: 0.75rem;
    }
    .search-highlight {
      background: #fff3cd;
      color: #1a1a2e;
      padding: 0 2px;
      border-radius: 2px;
    }
    .search-loading,
    .search-empty {
      padding: 1.2rem;
      text-align: center;
      color: #6c757d;
      font-size: 0.9rem;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
    }
    .search-footer {
      display: block;
      padding: 0.8rem 1rem;
      text-align: center;
      font-size: 0.85rem;
      font-weight: 600;
      color: #2d6a4f;
      border-top: 1px solid #f0f0f0;
      background: #f8f9fa;
      text-decoration: none;
      transition: background 0.2s;
    }
    .search-footer:hover {
      background: #e9f5ee;
      color: #1b4332;
    }
  `;
  document.head.appendChild(style);

});