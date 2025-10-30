window.addEventListener('load', () => {
   const loadingAnimation = document.querySelector('.loading-animation');
   loadingAnimation.style.opacity = '0';
   setTimeout(() => {
       loadingAnimation.style.display = 'none';
   }, 500);

   // Check if dark mode was enabled before and persist it
   const darkMode = localStorage.getItem('darkMode');
   if (darkMode === 'enabled') {
       body.classList.add('dark-mode');
       darkModeToggle.textContent = '☀️'; // Update button to sun icon
   }
});

// Dark Mode Toggle
const darkModeToggle = document.getElementById('darkModeToggle');
const body = document.body;

darkModeToggle.addEventListener('click', () => {
   body.classList.toggle('dark-mode');
   
   if (body.classList.contains('dark-mode')) {
       localStorage.setItem('darkMode', 'enabled'); // Save dark mode preference
       darkModeToggle.textContent = '☀️'; // Change to sun icon
   } else {
       localStorage.setItem('darkMode', 'disabled'); // Save light mode preference
       darkModeToggle.textContent = '🌓'; // Change to moon icon
   }
});

// Mobile Navigation Toggle
const navToggle = document.querySelector('.nav-toggle');
const navMenu = document.querySelector('nav ul');

navToggle.addEventListener('click', () => {
   navMenu.classList.toggle('show');
});

// Close mobile menu when clicking outside
document.addEventListener('click', (e) => {
   if (navMenu.classList.contains('show') && 
       !navMenu.contains(e.target) && 
       !navToggle.contains(e.target)) {
       navMenu.classList.remove('show');
       navToggle.setAttribute('aria-expanded', 'false');
   }
});

// Close mobile menu when pressing escape key
document.addEventListener('keydown', (e) => {
   if (e.key === 'Escape' && navMenu.classList.contains('show')) {
       navMenu.classList.remove('show');
       navToggle.setAttribute('aria-expanded', 'false');
   }
});

// Add smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
   anchor.addEventListener('click', function (e) {
       e.preventDefault();
       const targetId = this.getAttribute('href');
       if (targetId === '#') return;
       
       const targetElement = document.querySelector(targetId);
       if (targetElement) {
           targetElement.scrollIntoView({
               behavior: 'smooth'
           });
           
           // Set focus on the target element if it's the main content
           if (targetId === '#main-content') {
               targetElement.setAttribute('tabindex', '-1');
               targetElement.focus();
               // Remove the tabindex after focus to avoid 
               // interfering with normal tab navigation
               setTimeout(() => {
                   targetElement.removeAttribute('tabindex');
               }, 1000);
           }
       }
   });
});

// Tool search filter on home page
(() => {
  const searchInput = document.getElementById('toolSearch');
  const clearBtn = document.getElementById('toolSearchClear');
  const suggBox = document.getElementById('toolSuggestions');
  if (!searchInput) return;

  const sections = Array.from(document.querySelectorAll('section'));
  const toolCards = Array.from(document.querySelectorAll('.tool-card'));

  const normalize = (s) => (s || '').toLowerCase();
  const strip = (s) => (s || '').trim();

  // Build a small index of tools
  const tools = toolCards.map(card => ({
    el: card,
    href: card.getAttribute('href') || '',
    title: strip(card.querySelector('h3')?.textContent),
    desc: strip(card.querySelector('p')?.textContent),
    keywords: strip(card.getAttribute('title')),
  }));

  const rank = (q, t) => {
    if (!q) return 0;
    if (!t) return 9999;
    const i = t.indexOf(q);
    if (i === 0) return 1; // starts with
    if (i > 0) return 2;   // contains
    return 9999;
  };

  const search = (query) => {
    const q = normalize(query);
    // Score, sort, and return top 8 suggestions
    const scored = tools.map(t => {
      const T = normalize(t.title);
      const D = normalize(t.desc);
      const K = normalize(t.keywords);
      const H = normalize(t.href);
      const score = Math.min(
        rank(q, T),
        rank(q, D),
        rank(q, K),
        rank(q, H)
      );
      return { ...t, score };
    }).filter(x => q && x.score < 9999)
      .sort((a, b) => a.score - b.score || a.title.localeCompare(b.title))
      .slice(0, 8);
    return scored;
  };

  const filter = (query) => {
    const q = normalize(query);
    toolCards.forEach(card => {
      const title = normalize(card.querySelector('h3')?.textContent);
      const desc = normalize(card.querySelector('p')?.textContent);
      const href = normalize(card.getAttribute('href'));
      const match = !q || title.includes(q) || desc.includes(q) || href.includes(q);
      card.style.display = match ? '' : 'none';
    });

    sections.forEach(sec => {
      const grid = sec.querySelector('.tools-grid');
      if (!grid) return;
      const visible = Array.from(grid.querySelectorAll('.tool-card')).some(c => c.style.display !== 'none');
      sec.style.display = visible ? '' : 'none';
    });
  };

  let activeIndex = -1;
  const renderSuggestions = (items) => {
    suggBox.innerHTML = '';
    activeIndex = -1;
    if (!items.length) {
      suggBox.style.display = 'none';
      searchInput.setAttribute('aria-expanded', 'false');
      return;
    }
    items.forEach((it, idx) => {
      const div = document.createElement('div');
      div.className = 'suggestion-item';
      div.setAttribute('role', 'option');
      div.setAttribute('aria-selected', idx === activeIndex ? 'true' : 'false');
      div.innerHTML = `<div class="suggestion-title">${it.title}</div><div class="suggestion-desc">${it.desc || it.href}</div>`;
      div.addEventListener('mousedown', (ev) => {
        ev.preventDefault();
        window.location.href = it.href;
      });
      suggBox.appendChild(div);
    });
    suggBox.style.display = 'block';
    searchInput.setAttribute('aria-expanded', 'true');
  };

  const update = (q) => {
    clearBtn.style.display = q ? 'block' : 'none';
    filter(q);
    renderSuggestions(search(q));
  };

  let debounceTimer;
  searchInput.addEventListener('input', (e) => {
    const val = e.target.value;
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => update(val), 80);
  });

  searchInput.addEventListener('keydown', (e) => {
    const items = Array.from(suggBox.querySelectorAll('.suggestion-item'));
    if (!items.length) return;
    if (e.key === 'ArrowDown' || e.key === 'Down') {
      e.preventDefault();
      activeIndex = Math.min(items.length - 1, activeIndex + 1);
    } else if (e.key === 'ArrowUp' || e.key === 'Up') {
      e.preventDefault();
      activeIndex = Math.max(0, activeIndex - 1);
    } else if (e.key === 'Enter') {
      if (activeIndex >= 0) {
        const link = tools.find(t => t.title === items[activeIndex].querySelector('.suggestion-title')?.textContent);
        if (link) window.location.href = link.href;
      }
    } else if (e.key === 'Escape') {
      searchInput.value = '';
      update('');
    } else {
      return; // let input handler run
    }
    items.forEach((el, i) => el.setAttribute('aria-selected', i === activeIndex ? 'true' : 'false'));
  });

  clearBtn?.addEventListener('click', () => {
    searchInput.value = '';
    update('');
    searchInput.focus();
  });

  document.addEventListener('click', (e) => {
    if (!suggBox.contains(e.target) && e.target !== searchInput) {
      suggBox.style.display = 'none';
      searchInput.setAttribute('aria-expanded', 'false');
    }
  });
})();
