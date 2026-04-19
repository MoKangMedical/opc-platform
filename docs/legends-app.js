// ============================================
// OPC Legends — App (Bilingual + Cartoon)
// ============================================

(function() {
    'use strict';

    // ---- Language ----
    const langToggle = document.getElementById('langToggle');
    let lang = localStorage.getItem('opc-lang') || 'en';

    function L(en, zh) { return lang === 'zh' ? (zh || en) : en; }

    function updateLangBtn() {
        langToggle.textContent = lang === 'zh' ? '🌐 EN/中' : '🌐 中/EN';
        document.documentElement.lang = lang === 'zh' ? 'zh-CN' : 'en';
    }

    langToggle.addEventListener('click', () => {
        lang = lang === 'en' ? 'zh' : 'en';
        localStorage.setItem('opc-lang', lang);
        updateLangBtn();
        renderAll();
    });
    updateLangBtn();

    // ---- Theme Toggle ----
    const themeToggle = document.getElementById('themeToggle');
    let theme = localStorage.getItem('opc-theme') || 'dark';
    
    function updateTheme() {
        document.documentElement.setAttribute('data-theme', theme);
        themeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
        localStorage.setItem('opc-theme', theme);
    }
    
    themeToggle.addEventListener('click', () => {
        theme = theme === 'dark' ? 'light' : 'dark';
        updateTheme();
    });
    updateTheme();

    // ---- DOM ----
    const grid = document.getElementById('legendsGrid');
    const modalOverlay = document.getElementById('modalOverlay');
    const modal = document.getElementById('modal');
    const modalContent = document.getElementById('modalContent');
    const modalClose = document.getElementById('modalClose');
    const filterBtns = document.querySelectorAll('.filter-btn');
    const searchInput = document.getElementById('searchInput');
    const clearSearchBtn = document.getElementById('clearSearch');
    let currentFilter = 'all';
    let currentSearch = '';

    // ---- I18N Nav Labels ----
    const i18n = {
        'nav-legends': { en: 'Legends', zh: '传奇人物' },
        'nav-philosophy': { en: 'Philosophy', zh: '商业哲学' },
        'nav-cases': { en: 'Cases', zh: '案例分析' },
        'nav-playbook': { en: 'Playbook', zh: '创业手册' }
    };

    function updateNavLabels() {
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.dataset.i18n;
            if (i18n[key]) el.textContent = L(i18n[key].en, i18n[key].zh);
        });
    }

    // ---- Render Legend Cards ----
    function renderCards(filter = 'all', search = '') {
        let filtered = LEGENDS;
        
        // Apply category filter
        if (filter !== 'all') {
            filtered = filtered.filter(l => l.category.includes(filter));
        }
        
        // Apply search filter
        if (search.trim()) {
            const searchLower = search.toLowerCase();
            filtered = filtered.filter(l => 
                l.name.toLowerCase().includes(searchLower) ||
                l.nameZh.toLowerCase().includes(searchLower) ||
                l.role.toLowerCase().includes(searchLower) ||
                l.roleZh.toLowerCase().includes(searchLower) ||
                l.bio.toLowerCase().includes(searchLower) ||
                l.bioZh.toLowerCase().includes(searchLower) ||
                l.tags.some(tag => tag.toLowerCase().includes(searchLower)) ||
                l.businessModel.toLowerCase().includes(searchLower) ||
                l.businessModelZh.toLowerCase().includes(searchLower)
            );
        }

        grid.innerHTML = filtered.map((legend, i) => `
            <div class="legend-card fade-in" data-id="${legend.id}" style="animation-delay: ${i * 0.06}s">
                <div class="legend-card-header">
                    <div class="legend-avatar cartoon-avatar">
                        ${legend.avatar}
                    </div>
                    <div class="legend-info">
                        <h3>${L(legend.name, legend.nameZh)}</h3>
                        <span class="legend-role">${L(legend.role, legend.roleZh)}</span>
                    </div>
                </div>
                <p class="legend-bio">${L(legend.bio, legend.bioZh)}</p>
                <div class="legend-metrics">
                    ${legend.metrics.slice(0, 3).map(m => `
                        <div class="metric">
                            <span class="metric-value">${m.value}</span>
                            <span class="metric-label">${L(m.label, m.labelZh)}</span>
                        </div>
                    `).join('')}
                </div>
                <div class="legend-tags">
                    ${legend.tags.map(t => `<span class="legend-tag">${t}</span>`).join('')}
                </div>
            </div>
        `).join('');

        requestAnimationFrame(() => {
            grid.querySelectorAll('.fade-in').forEach((el, i) => {
                setTimeout(() => el.classList.add('visible'), i * 60);
            });
        });

        grid.querySelectorAll('.legend-card').forEach(card => {
            card.addEventListener('click', () => openModal(card.dataset.id));
        });
    }

    // ---- Modal ----
    function openModal(id) {
        const legend = LEGENDS.find(l => l.id === id);
        if (!legend) return;

        modalContent.innerHTML = `
            <div class="modal-header">
                <div class="modal-avatar cartoon-avatar-lg">
                    ${legend.avatar}
                </div>
                <div>
                    <h2 class="modal-title">${L(legend.name, legend.nameZh)}</h2>
                    <p class="modal-role">${L(legend.role, legend.roleZh)}</p>
                    <div class="modal-links">
                        ${legend.website ? `<a href="${legend.website}" target="_blank">${L('Website', '官网')}</a>` : ''}
                        ${legend.twitter ? `<a href="${legend.twitter}" target="_blank">Twitter/X</a>` : ''}
                    </div>
                </div>
            </div>

            <div class="modal-metrics">
                ${legend.metrics.map(m => `
                    <div class="modal-metric">
                        <span class="val">${m.value}</span>
                        <span class="lbl">${L(m.label, m.labelZh)}</span>
                    </div>
                `).join('')}
            </div>

            <div class="modal-section">
                <h4>${L('BIO', '简介')}</h4>
                <p>${L(legend.bio, legend.bioZh)}</p>
            </div>

            <div class="modal-quote">"${L(legend.quote, legend.quoteZh)}"</div>

            <div class="modal-section">
                <h4>${L('BUSINESS PHILOSOPHY', '商业哲学')}</h4>
                <ul>
                    ${(L(legend.philosophy, legend.philosophyZh)).map(p => `<li>${p}</li>`).join('')}
                </ul>
            </div>

            <div class="modal-section">
                <h4>${L('KEY INSIGHT', '核心洞察')}</h4>
                <p>${L(legend.keyInsight, legend.keyInsightZh)}</p>
            </div>

            <div class="modal-section">
                <h4>${L('BUSINESS MODEL', '商业模式')}</h4>
                <p>${L(legend.businessModel, legend.businessModelZh)}</p>
            </div>
        `;

        modalOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeModal() {
        modalOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    modalClose.addEventListener('click', closeModal);
    modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) closeModal();
    });
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal();
    });

    // ---- Filters ----
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilter = btn.dataset.filter;
            renderCards(currentFilter, currentSearch);
        });
    });

    // ---- Search ----
    searchInput.addEventListener('input', (e) => {
        currentSearch = e.target.value;
        clearSearchBtn.style.display = currentSearch ? 'block' : 'none';
        renderCards(currentFilter, currentSearch);
    });

    clearSearchBtn.addEventListener('click', () => {
        searchInput.value = '';
        currentSearch = '';
        clearSearchBtn.style.display = 'none';
        renderCards(currentFilter, currentSearch);
    });

    // ---- Counter Animation ----
    function animateCounters() {
        const counters = document.querySelectorAll('[data-count]');
        counters.forEach(counter => {
            const target = parseInt(counter.dataset.count);
            const duration = 1500;
            const start = performance.now();
            function update(now) {
                const elapsed = now - start;
                const progress = Math.min(elapsed / duration, 1);
                const eased = 1 - Math.pow(1 - progress, 3);
                counter.textContent = Math.round(target * eased);
                if (progress < 1) requestAnimationFrame(update);
            }
            requestAnimationFrame(update);
        });
    }

    // ---- Scroll Animations ----
    function initScrollObserver() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        document.querySelectorAll('.philosophy-card, .case-card, .timeline-item, .model-card').forEach(el => {
            el.classList.add('fade-in');
            observer.observe(el);
        });
    }

    // ---- Nav Scroll Effect ----
    function initNavScroll() {
        const nav = document.getElementById('nav');
        window.addEventListener('scroll', () => {
            nav.style.borderBottomColor = window.scrollY > 100 ? 'rgba(30, 30, 46, 0.8)' : 'var(--border)';
        });
    }

    // ---- Case Card Click ----
    function initCaseClicks() {
        const caseToLegend = {
            '1': 'pieter-levels', '2': 'naval-ravikant', '3': 'james-clear',
            '4': 'jason-fried', '5': 'sahil-lavingia', '6': 'jack-butcher',
            '7': 'ali-abdaal'
        };
        document.querySelectorAll('.case-card').forEach(card => {
            card.addEventListener('click', () => {
                const legendId = caseToLegend[card.dataset.case];
                if (legendId) openModal(legendId);
            });
        });
    }

    // ---- Mobile Menu ----
    function initMobileMenu() {
        const menuBtn = document.getElementById('menuBtn');
        const navLinks = document.querySelector('.nav-links');
        if (menuBtn) {
            menuBtn.addEventListener('click', () => {
                navLinks.style.display = navLinks.style.display === 'flex' ? 'none' : 'flex';
                navLinks.style.position = 'absolute';
                navLinks.style.top = '64px';
                navLinks.style.left = '0';
                navLinks.style.right = '0';
                navLinks.style.flexDirection = 'column';
                navLinks.style.background = 'var(--bg)';
                navLinks.style.padding = '16px 24px';
                navLinks.style.borderBottom = '1px solid var(--border)';
            });
        }
    }

    // ---- Smooth Scroll ----
    document.querySelectorAll('a[href^="#"]').forEach(a => {
        a.addEventListener('click', (e) => {
            const href = a.getAttribute('href');
            if (href === '#') return;
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
    });

    // ---- Render All (for language switch) ----
    function renderAll() {
        updateNavLabels();
        renderCards(currentFilter, currentSearch);
        // Update static text elements
        document.querySelectorAll('.section-tag').forEach(el => {
            const text = el.textContent.trim();
            const map = {
                'PROFILES': L('PROFILES', '人物档案'),
                'MINDSET': L('MINDSET', '思维模式'),
                'DEEP DIVES': L('DEEP DIVES', '深度分析'),
                'ACTIONABLE': L('ACTIONABLE', '行动指南'),
                'MODELS': L('MODELS', '商业模式')
            };
            if (map[text]) el.textContent = map[text];
        });
        // Update section titles
        document.querySelectorAll('.section-title').forEach(el => {
            const text = el.textContent.trim();
            const map = {
                'The Legends': L('The Legends', '传奇人物'),
                'Business Philosophy DNA': L('Business Philosophy DNA', '商业哲学DNA'),
                'Case Studies': L('Case Studies', '案例深度分析'),
                'The OPC Playbook': L('The OPC Playbook', 'OPC创业手册'),
                '7 Proven OPC Revenue Models': L('7 Proven OPC Revenue Models', '7种已验证的OPC收入模型')
            };
            if (map[text]) el.textContent = map[text];
        });
        // Update section descriptions
        document.querySelectorAll('.section-desc').forEach(el => {
            const text = el.textContent.trim();
            const map = {
                "Each built a world-class business as a one-person company. Click to explore their thinking.": L("Each built a world-class business as a one-person company. Click to explore their thinking.", "每个人都以一人公司模式打造了世界级企业。点击探索他们的思维。"),
                "The shared mental models across all OPC legends.": L("The shared mental models across all OPC legends.", "所有OPC传奇人物共享的心智模型。"),
                "Detailed breakdowns of how OPC legends built and scaled their businesses.": L("Detailed breakdowns of how OPC legends built and scaled their businesses.", "OPC传奇人物如何建立和发展业务的详细分析。"),
                "Distilled wisdom from 18 legends. The framework for building your own one-person company.": L("Distilled wisdom from 18 legends. The framework for building your own one-person company.", "从18位传奇人物提炼的智慧。打造你自己一人公司的框架。")
            };
            if (map[text]) el.textContent = map[text];
        });
        // Update hero
        const heroTitle = document.querySelector('.hero-title');
        if (heroTitle) {
            heroTitle.innerHTML = `<span class="line">${L('The Legends Who', '那些以一人之力')}</span><span class="line gradient-text">${L('Built Empires Alone', '建立帝国的传奇')}</span>`;
        }
        const heroSub = document.querySelector('.hero-subtitle');
        if (heroSub) {
            heroSub.textContent = L(
                'Deep dives into the business thinking, strategies, and playbooks of the world\'s most successful solopreneurs. No VC. No co-founders. Just one person changing the game.',
                '深入研究全球最成功独立创业者的商业思维、战略和行动手册。没有风投，没有联合创始人。只有一个人在改变游戏规则。'
            );
        }
        const heroBadge = document.querySelector('.hero-badge');
        if (heroBadge) heroBadge.textContent = L('ONE PERSON COMPANY • HALL OF FAME', '一人公司 • 名人堂');
        const heroCta = document.querySelector('.hero-cta');
        if (heroCta) {
            heroCta.innerHTML = L('Explore the Legends', '探索传奇人物') + ' <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12l7 7 7-7"/></svg>';
        }
        // Stat labels
        document.querySelectorAll('.stat-label').forEach(el => {
            const text = el.textContent.trim();
            const map = {
                'Legends Profiled': L('Legends Profiled', '传奇人物'),
                'Combined Revenue': L('Combined Revenue', '总收入'),
                'Business Models': L('Business Models', '收入模型'),
                'Key Insights': L('Key Insights', '核心洞察')
            };
            if (map[text]) el.textContent = map[text];
        });
        // Footer
        const footerTagline = document.querySelector('.footer-tagline');
        if (footerTagline) footerTagline.textContent = L('One Person. Infinite Possibilities.', '一个人，无限可能。');
    }

    // ---- Init ----
    renderAll();
    animateCounters();
    initScrollObserver();
    initNavScroll();
    initCaseClicks();
    initMobileMenu();

    console.log('🏆 OPC Legends loaded —', LEGENDS.length, 'legends | lang:', lang);

})();
