/**
 * OPC Platform - 移动端底部导航栏
 */

// 移动端底部导航栏HTML
function createMobileNav() {
  // 检查是否已存在底部导航
  if (document.querySelector('.mobile-nav')) {
    return;
  }
  
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  
  const navItems = [
    { href: 'index.html', icon: '🏠', label: '首页' },
    { href: 'government.html', icon: '📋', label: '项目' },
    { href: 'platform.html', icon: '⚡', label: '平台' },
    { href: 'academy.html', icon: '📚', label: '学院' },
    { href: 'profile.html', icon: '👤', label: '我的' }
  ];
  
  const navHTML = `
    <div class="mobile-nav">
      ${navItems.map(item => `
        <a href="${item.href}" class="mobile-nav-item ${currentPage === item.href ? 'active' : ''}">
          <div class="mobile-nav-icon">${item.icon}</div>
          <div class="mobile-nav-label">${item.label}</div>
        </a>
      `).join('')}
    </div>
    <style>
      .mobile-nav {
        display: none;
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: rgba(6,6,10,0.95);
        backdrop-filter: blur(20px);
        border-top: 1px solid var(--bdr);
        padding: 8px 0;
        z-index: 1000;
        justify-content: space-around;
        align-items: center;
      }
      
      .mobile-nav-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 8px 12px;
        color: var(--t2);
        text-decoration: none;
        transition: all 0.2s;
        border-radius: 8px;
        min-width: 60px;
      }
      
      .mobile-nav-item.active {
        color: var(--a2);
        background: rgba(124,92,252,0.1);
      }
      
      .mobile-nav-item:hover {
        color: var(--t1);
      }
      
      .mobile-nav-icon {
        font-size: 20px;
        margin-bottom: 4px;
      }
      
      .mobile-nav-label {
        font-size: 10px;
        font-weight: 500;
        letter-spacing: 0.3px;
      }
      
      @media (max-width: 768px) {
        .mobile-nav {
          display: flex;
        }
        
        body {
          padding-bottom: 70px;
        }
        
        .ft {
          padding-bottom: 100px;
        }
      }
    </style>
  `;
  
  document.body.insertAdjacentHTML('beforeend', navHTML);
}

// 添加移动端样式
function addMobileStyles() {
  const style = document.createElement('style');
  style.textContent = `
    /* 移动端通用样式 */
    @media (max-width: 768px) {
      /* 增大点击区域 */
      button, a, .btn, .nl, .mc, .rc {
        min-height: 44px;
        min-width: 44px;
      }
      
      /* 改善表单输入 */
      input, textarea, select {
        font-size: 16px !important; /* 防止iOS缩放 */
        padding: 14px 16px !important;
      }
      
      /* 改善卡片间距 */
      .mc, .rc, .form-card {
        padding: 24px !important;
        margin-bottom: 16px !important;
      }
      
      /* 改善按钮 */
      .btn, .btn-p, .btn-s {
        padding: 16px 24px !important;
        font-size: 15px !important;
      }
      
      /* 改善标题 */
      h1 {
        font-size: 28px !important;
        letter-spacing: -1px !important;
      }
      
      h2 {
        font-size: 22px !important;
      }
      
      /* 改善网格 */
      .mg, .rg {
        gap: 16px !important;
      }
      
      /* 改善表单 */
      .form-row {
        flex-direction: column !important;
        gap: 0 !important;
      }
      
      .form-row .form-group {
        margin-bottom: 16px !important;
      }
      
      /* 改善标签页 */
      .tabs {
        flex-direction: row;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
      }
      
      .tab {
        white-space: nowrap;
        padding: 12px 16px !important;
      }
      
      /* 改善模态框 */
      .modal-content {
        margin: 16px !important;
        max-height: calc(100vh - 32px) !important;
        overflow-y: auto;
      }
      
      /* 改善表格 */
      table {
        font-size: 14px !important;
      }
      
      th, td {
        padding: 12px 8px !important;
      }
      
      /* 改善列表 */
      .list-item {
        padding: 16px !important;
      }
      
      /* 改善搜索框 */
      .search-input {
        font-size: 16px !important;
        padding: 14px 16px !important;
      }
      
      /* 改善下拉菜单 */
      .dropdown-content {
        max-height: 60vh !important;
        overflow-y: auto;
      }
      
      /* 改善轮播图 */
      .carousel {
        touch-action: pan-y;
      }
      
      /* 改善滚动 */
      .scroll-container {
        -webkit-overflow-scrolling: touch;
        overflow-scrolling: touch;
      }
      
      /* 改善图片 */
      img {
        max-width: 100%;
        height: auto;
      }
      
      /* 改善视频 */
      video {
        max-width: 100%;
        height: auto;
      }
      
      /* 改善工具提示 */
      .tooltip {
        position: fixed;
        bottom: 80px;
        left: 50%;
        transform: translateX(-50%);
        background: var(--bg3);
        padding: 12px 16px;
        border-radius: 8px;
        z-index: 1001;
      }
      
      /* 改善加载状态 */
      .loading {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 1002;
      }
      
      /* 改善错误提示 */
      .error-message {
        position: fixed;
        bottom: 80px;
        left: 16px;
        right: 16px;
        background: rgba(244,114,182,0.1);
        border: 1px solid rgba(244,114,182,0.2);
        color: var(--pk);
        padding: 14px 16px;
        border-radius: 12px;
        z-index: 1001;
      }
      
      /* 改善成功提示 */
      .success-message {
        position: fixed;
        bottom: 80px;
        left: 16px;
        right: 16px;
        background: rgba(52,211,153,0.1);
        border: 1px solid rgba(52,211,153,0.2);
        color: var(--g);
        padding: 14px 16px;
        border-radius: 12px;
        z-index: 1001;
      }
    }
    
    /* 触摸设备优化 */
    @media (hover: none) and (pointer: coarse) {
      /* 禁用悬停效果 */
      *:hover {
        background-color: inherit !important;
        color: inherit !important;
      }
      
      /* 改善触摸反馈 */
      button:active, a:active, .btn:active {
        transform: scale(0.98);
        opacity: 0.8;
      }
      
      /* 改善滑动 */
      .swipeable {
        touch-action: pan-x pan-y;
      }
      
      /* 改善拖拽 */
      .draggable {
        touch-action: none;
      }
    }
    
    /* 高DPI屏幕优化 */
    @media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
      /* 改善图标 */
      .icon {
        image-rendering: -webkit-optimize-contrast;
      }
      
      /* 改善边框 */
      .border-1px {
        border-width: 0.5px !important;
      }
    }
    
    /* 横屏优化 */
    @media (max-height: 500px) and (orientation: landscape) {
      .hero {
        min-height: auto;
        padding: 80px 16px 40px;
      }
      
      .hero h1 {
        font-size: 32px !important;
        margin-bottom: 16px;
      }
      
      .hero-sub {
        font-size: 16px !important;
        margin-bottom: 24px;
      }
      
      .sec {
        padding: 40px 16px;
      }
      
      .mg, .rg {
        grid-template-columns: 1fr 1fr;
      }
    }
    
    /* 打印优化 */
    @media print {
      .mobile-nav, .nav, .btn, button {
        display: none !important;
      }
      
      body {
        padding: 0 !important;
        background: white !important;
        color: black !important;
      }
      
      a {
        text-decoration: underline;
      }
    }
  `;
  
  document.head.appendChild(style);
}

// 添加触摸事件支持
function addTouchSupport() {
  // 防止双击缩放
  let lastTouchEnd = 0;
  document.addEventListener('touchend', function(event) {
    const now = (new Date()).getTime();
    if (now - lastTouchEnd <= 300) {
      event.preventDefault();
    }
    lastTouchEnd = now;
  }, false);
  
  // 添加触摸反馈
  document.addEventListener('touchstart', function(e) {
    const target = e.target.closest('button, a, .btn, .nl, .mc, .rc');
    if (target) {
      target.style.opacity = '0.7';
    }
  });
  
  document.addEventListener('touchend', function(e) {
    const target = e.target.closest('button, a, .btn, .nl, .mc, .rc');
    if (target) {
      target.style.opacity = '1';
    }
  });
  
  // 添加滑动支持
  let touchStartX = 0;
  let touchStartY = 0;
  
  document.addEventListener('touchstart', function(e) {
    touchStartX = e.touches[0].clientX;
    touchStartY = e.touches[0].clientY;
  });
  
  document.addEventListener('touchmove', function(e) {
    if (!touchStartX || !touchStartY) {
      return;
    }
    
    const touchEndX = e.touches[0].clientX;
    const touchEndY = e.touches[0].clientY;
    
    const diffX = touchStartX - touchEndX;
    const diffY = touchStartY - touchEndY;
    
    // 水平滑动距离大于垂直滑动距离
    if (Math.abs(diffX) > Math.abs(diffY)) {
      // 向左滑动
      if (diffX > 50) {
        document.dispatchEvent(new CustomEvent('swipeLeft'));
      }
      // 向右滑动
      if (diffX < -50) {
        document.dispatchEvent(new CustomEvent('swipeRight'));
      }
    }
    
    touchStartX = 0;
    touchStartY = 0;
  });
}

// 初始化移动端优化
function initMobileOptimization() {
  // 检查是否为移动设备
  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  
  if (isMobile) {
    addMobileStyles();
    createMobileNav();
    addTouchSupport();
    
    // 添加viewport meta标签（如果没有）
    if (!document.querySelector('meta[name="viewport"]')) {
      const meta = document.createElement('meta');
      meta.name = 'viewport';
      meta.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no';
      document.head.appendChild(meta);
    }
    
    // 添加移动端CSS类
    document.body.classList.add('mobile-device');
    
    console.log('✅ 移动端优化已启用');
  }
}

// 页面加载完成后初始化
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initMobileOptimization);
} else {
  initMobileOptimization();
}

// 导出函数供其他模块使用
window.OPCMobile = {
  createMobileNav,
  addMobileStyles,
  addTouchSupport,
  initMobileOptimization
};
