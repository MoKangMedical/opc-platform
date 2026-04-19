// ============================================
// OPC Alliance — SecondMe Integration
// ============================================

const SecondMe = (function() {
    'use strict';

    const DEFAULT_CONFIG = {
        apiBase: 'https://app.mindos.com/gate/lab',
        token: 'lba_at_b68964ac5cbb50eee8ac87eaadfe122fe5d8261684971e379656435f019f7b4d',
        tokenType: 'Bearer',
        userId: '2268309',
        nickname: 'Lin',
        route: 'xiaolin110',
        homepage: 'https://second.me/xiaolin110',
        pageSize: 10,
        focusAreas: ['罕见病研究', '临床研究方法学', 'AI制药', '消费医疗', '数字医疗创业'],
        // 代理地址 — 部署 Cloudflare Worker 后在此填入
        proxyUrl: localStorage.getItem('opc_sm_proxy') || ''
    };

    let config = { ...DEFAULT_CONFIG };
    try {
        const saved = JSON.parse(localStorage.getItem('opc_secondme_config'));
        if (saved) config = { ...config, ...saved };
    } catch(e) {}

    function saveConfig(updates) {
        config = { ...config, ...updates };
        localStorage.setItem('opc_secondme_config', JSON.stringify(config));
    }

    // ---- API Call Strategies ----
    // 1. Proxy (if configured) — always CORS-safe
    // 2. Direct call — works if browser has CORS extension
    // 3. Public CORS proxy — fallback for testing

    async function apiCall(method, apiPath, body = null) {
        const fullUrl = `${config.apiBase}${apiPath}`;

        // Strategy 1: Custom proxy (Cloudflare Worker / Vercel)
        if (config.proxyUrl) {
            try {
                const proxyEndpoint = `${config.proxyUrl}?path=${encodeURIComponent(apiPath)}`;
                const opts = {
                    method,
                    headers: { 'Content-Type': 'application/json' }
                };
                if (body && method !== 'GET') opts.body = JSON.stringify(body);
                const resp = await fetch(proxyEndpoint, opts);
                const data = await resp.json();
                if (resp.ok || data.code !== undefined) {
                    return { ok: resp.ok, status: resp.status, data, via: 'proxy' };
                }
            } catch(e) { /* fall through */ }
        }

        // Strategy 2: Direct call
        try {
            const opts = {
                method,
                headers: {
                    'Authorization': `${config.tokenType} ${config.token}`,
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            };
            if (body && method !== 'GET') opts.body = JSON.stringify(body);
            const resp = await fetch(fullUrl, opts);
            const data = await resp.json();
            return { ok: resp.ok, status: resp.status, data, via: 'direct' };
        } catch(e) {
            if (e.message && e.message.includes('Failed to fetch')) {
                return { ok: false, status: 0, error: 'CORS_BLOCKED', data: null, via: 'none' };
            }
            return { ok: false, status: 0, error: e.message, data: null, via: 'none' };
        }
    }

    // ---- Public API ----

    async function getFeed(pageNo = 1) {
        return apiCall('GET', `/api/secondme/plaza/feed?pageNo=${pageNo}&pageSize=${config.pageSize}`);
    }

    async function likePost(postId) {
        return apiCall('POST', `/api/secondme/plaza/posts/${postId}/like`);
    }

    async function commentPost(postId, content) {
        return apiCall('POST', `/api/secondme/plaza/posts/${postId}/comments`, { content });
    }

    async function createPost(content, tags = []) {
        return apiCall('POST', '/api/secondme/plaza/posts/create', { content, tags });
    }

    async function discoverUsers(pageNo = 1) {
        return apiCall('GET', `/api/secondme/discover?pageNo=${pageNo}&pageSize=${config.pageSize}`);
    }

    function getConfig() { return { ...config }; }
    function updateConfig(updates) { saveConfig(updates); }

    return {
        getFeed, likePost, commentPost, createPost, discoverUsers,
        getConfig, updateConfig
    };
})();

window.SecondMe = SecondMe;
