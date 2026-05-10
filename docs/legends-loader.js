// ============================================
// OPC Legends — API Loader (v3.0)
// Tries backend API first, falls back to static data
// ============================================

const LEGENDS_API = '/api/chat/legends';

// Map API fields to LEGENDS format expected by legends-app.js
function mapLegendFromAPI(item) {
    return {
        id: String(item.id || ''),
        name: item.name || item.title || '',
        name_en: item.name_en || '',
        title: item.title || item.role || '',
        title_en: item.title_en || '',
        avatar: item.avatar || item.avatar_url || '',
        cartoon: true, // API legends use cartoon avatars
        desc: item.description || item.bio || '',
        desc_en: item.description_en || '',
        tags: item.tags || [],
        stats: {
            projects: item.projects_completed || item.project_count || 0,
            revenue: item.revenue || 0,
            team: item.team_size || item.team || 0,
            followers: item.followers || 0
        },
        highlights: item.highlights || [],
        quote: item.quote || item.motto || '',
        links: {
            github: item.github || '',
            website: item.website || '',
            twitter: item.twitter || ''
        }
    };
}

// Try loading from backend API
async function loadLegendsFromAPI() {
    try {
        const resp = await fetch(LEGENDS_API);
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();
        const legends = Array.isArray(data) ? data : (data.legends || data.data || []);
        
        if (legends.length > 0) {
            console.log(`✅ 从后端加载了 ${legends.length} 位名人数据`);
            return legends.map(mapLegendFromAPI);
        }
        console.warn('后端返回空名人数据');
    } catch (e) {
        console.warn('后端未连接，使用静态数据:', e.message);
    }
    return null;
}

// Initialize: try API, fallback to static LEGENDS
(async function initLegendsData() {
    const apiData = await loadLegendsFromAPI();
    if (apiData && apiData.length > 0) {
        // Override static LEGENDS with API data
        if (typeof LEGENDS !== 'undefined') {
            // Map API data into existing LEGENDS array format
            // Keep cartoonAvatar for generating avatars from seed
            window.__api_legends = apiData;
            // Replace LEGENDS in-place for legends-app.js to use
            LEGENDS.length = 0;
            Array.prototype.push.apply(LEGENDS, apiData);
            console.log('✅ 名人数据已从后端刷新');
        }
    }
    // If API failed, LEGENDS from legends-data.js is already loaded
})();
