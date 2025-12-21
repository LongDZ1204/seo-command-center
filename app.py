import streamlit as st
import pandas as pd
import os
import unicodedata

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(
    page_title="SEO Command Center", 
    layout="wide", 
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# === LUCIDE ICONS (SVG) ===
ICONS = {
    # Navigation & UI
    'dashboard': '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/></svg>',
    'settings': '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>',
    'target': '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
    'upload': '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/></svg>',
    'calendar': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/></svg>',
    'folder': '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/></svg>',
    
    # Trends
    'trend_up': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>',
    'trend_down': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 17 13.5 8.5 8.5 13.5 2 7"/><polyline points="16 17 22 17 22 11"/></svg>',
    'arrow_up': '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 7-7 7 7"/><path d="M12 19V5"/></svg>',
    'arrow_down': '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v14"/><path d="m19 12-7 7-7-7"/></svg>',
    'minus': '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/></svg>',
    'rocket': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/></svg>',
    'zap': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    
    # Status
    'alert_triangle': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>',
    'alert_circle': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg>',
    'check_circle': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg>',
    'x_circle': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/></svg>',
    'sparkles': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/><path d="M5 3v4"/><path d="M19 17v4"/><path d="M3 5h4"/><path d="M17 19h4"/></svg>',
    'flame': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/></svg>',
    
    # Analytics
    'bar_chart': '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" x2="12" y1="20" y2="10"/><line x1="18" x2="18" y1="20" y2="4"/><line x1="6" x2="6" y1="20" y2="16"/></svg>',
    'pie_chart': '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/></svg>',
    'activity': '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>',
    'layers': '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/></svg>',
    
    # Actions
    'search': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>',
    'filter': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>',
    'external_link': '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" x2="21" y1="14" y2="3"/></svg>',
    'copy': '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>',
    'info': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>',
    'history': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l4 2"/></svg>',
    
    # Objects
    'link': '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>',
    'unlink': '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m18.84 12.25 1.72-1.71h-.02a5.004 5.004 0 0 0-.12-7.07 5.006 5.006 0 0 0-6.95 0l-1.72 1.71"/><path d="m5.17 11.75-1.71 1.71a5.004 5.004 0 0 0 .12 7.07 5.006 5.006 0 0 0 6.95 0l1.71-1.71"/><line x1="8" x2="8" y1="2" y2="5"/><line x1="2" x2="5" y1="8" y2="8"/><line x1="16" x2="16" y1="19" y2="22"/><line x1="19" x2="22" y1="16" y2="16"/></svg>',
    'globe': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/></svg>',
    'hash': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" x2="20" y1="9" y2="9"/><line x1="4" x2="20" y1="15" y2="15"/><line x1="10" x2="8" y1="3" y2="21"/><line x1="16" x2="14" y1="3" y2="21"/></svg>',
}

def icon(name, color=None):
    """Render icon với màu tùy chọn"""
    svg = ICONS.get(name, '')
    if color:
        svg = svg.replace('currentColor', color)
    return svg

# === MODERN CSS STYLES ===
st.markdown("""
<style>
    /* === VARIABLES === */
    :root {
        --primary: #6366f1;
        --primary-light: #818cf8;
        --primary-dark: #4f46e5;
        --success: #10b981;
        --success-light: #34d399;
        --success-bg: #ecfdf5;
        --warning: #f59e0b;
        --warning-light: #fbbf24;
        --warning-bg: #fffbeb;
        --danger: #ef4444;
        --danger-light: #f87171;
        --danger-bg: #fef2f2;
        --info: #3b82f6;
        --info-light: #60a5fa;
        --info-bg: #eff6ff;
        
        --gray-50: #f9fafb;
        --gray-100: #f3f4f6;
        --gray-200: #e5e7eb;
        --gray-300: #d1d5db;
        --gray-400: #9ca3af;
        --gray-500: #6b7280;
        --gray-600: #4b5563;
        --gray-700: #374151;
        --gray-800: #1f2937;
        --gray-900: #111827;
        
        --radius-sm: 6px;
        --radius-md: 10px;
        --radius-lg: 16px;
        --radius-xl: 20px;
        
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
    }
    
    /* === GLOBAL STYLES === */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* === SIDEBAR === */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--gray-900) 0%, var(--gray-800) 100%);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: var(--gray-300);
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: white !important;
    }
    
    [data-testid="stSidebar"] label {
        color: var(--gray-300) !important;
    }
    
    /* === HEADER === */
    .dashboard-header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        padding: 24px 32px;
        border-radius: var(--radius-xl);
        margin-bottom: 24px;
        box-shadow: var(--shadow-lg);
        color: white;
    }
    
    .dashboard-header h1 {
        margin: 0;
        font-size: 28px;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .dashboard-header .subtitle {
        margin-top: 8px;
        opacity: 0.9;
        font-size: 14px;
        display: flex;
        align-items: center;
        gap: 16px;
    }
    
    .dashboard-header .stat-badge {
        background: rgba(255,255,255,0.2);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 13px;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    
    /* === SECTION HEADERS === */
    .section-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 32px 0 16px 0;
        padding-bottom: 12px;
        border-bottom: 2px solid var(--gray-200);
    }
    
    .section-header h2 {
        margin: 0;
        font-size: 18px;
        font-weight: 600;
        color: var(--gray-800);
    }
    
    .section-header .icon {
        width: 32px;
        height: 32px;
        background: var(--primary);
        border-radius: var(--radius-sm);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 16px;
    }
    
    /* === KPI CARDS === */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    
    .kpi-card {
        background: white;
        border-radius: var(--radius-lg);
        padding: 20px;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--gray-100);
        transition: all 0.2s ease;
        position: relative;
        overflow: hidden;
        min-height: 200px;
        display: flex;
        flex-direction: column;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--primary);
    }
    
    .kpi-card.success::before { background: var(--success); }
    .kpi-card.warning::before { background: var(--warning); }
    .kpi-card.danger::before { background: var(--danger); }
    .kpi-card.info::before { background: var(--info); }
    
    .kpi-card .label {
        font-size: 12px;
        font-weight: 600;
        color: var(--gray-500);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    
    .kpi-card .value {
        font-size: 32px;
        font-weight: 700;
        color: var(--gray-900);
        line-height: 1;
        margin-bottom: 4px;
    }
    
    .kpi-card .percentage {
        font-size: 14px;
        color: var(--gray-500);
        margin-bottom: 12px;
    }
    
    .kpi-card .trend {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 13px;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 20px;
    }
    
    .kpi-card .trend.up {
        background: var(--success-bg);
        color: var(--success);
    }
    
    .kpi-card .trend.down {
        background: var(--danger-bg);
        color: var(--danger);
    }
    
    .kpi-card .trend.stable {
        background: var(--gray-100);
        color: var(--gray-500);
    }
    
    .kpi-card .compare {
        font-size: 12px;
        color: var(--gray-400);
        margin-top: 8px;
    }
    
    .kpi-card .target-status {
        margin-top: 12px;
        padding: 8px 12px;
        border-radius: var(--radius-sm);
        font-size: 12px;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    .kpi-card .target-status.met {
        background: var(--success-bg);
        color: var(--success);
    }
    
    .kpi-card .target-status.miss {
        background: var(--danger-bg);
        color: var(--danger);
    }
    
    /* === ALERT BOXES === */
    .alert-box {
        padding: 16px 20px;
        border-radius: var(--radius-md);
        margin-bottom: 16px;
        display: flex;
        align-items: flex-start;
        gap: 12px;
    }
    
    .alert-box.danger {
        background: var(--danger-bg);
        border: 1px solid #fecaca;
    }
    
    .alert-box.success {
        background: var(--success-bg);
        border: 1px solid #a7f3d0;
    }
    
    .alert-box.warning {
        background: var(--warning-bg);
        border: 1px solid #fde68a;
    }
    
    .alert-box .icon-wrapper {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        font-size: 18px;
    }
    
    .alert-box.danger .icon-wrapper {
        background: var(--danger);
        color: white;
    }
    
    .alert-box.success .icon-wrapper {
        background: var(--success);
        color: white;
    }
    
    .alert-box .content {
        flex: 1;
    }
    
    .alert-box .title {
        font-weight: 600;
        font-size: 14px;
        margin-bottom: 4px;
    }
    
    .alert-box.danger .title { color: var(--danger); }
    .alert-box.success .title { color: var(--success); }
    
    .alert-box .description {
        font-size: 13px;
        color: var(--gray-600);
    }
    
    /* === TOPIC HEALTH TABLE === */
    .topic-table {
        background: white;
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-md);
        overflow: hidden;
    }
    
    .topic-row {
        display: grid;
        grid-template-columns: 2fr 1fr 1fr 1fr 1fr 1fr 2fr;
        padding: 14px 20px;
        border-bottom: 1px solid var(--gray-100);
        align-items: center;
        transition: background 0.15s ease;
    }
    
    .topic-row:hover {
        background: var(--gray-50);
    }
    
    .topic-row.header {
        background: var(--gray-50);
        font-weight: 600;
        font-size: 12px;
        color: var(--gray-500);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .topic-row .topic-name {
        font-weight: 500;
        color: var(--gray-800);
    }
    
    .topic-row .net-flow {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .net-flow-bar {
        height: 8px;
        border-radius: 4px;
        background: var(--gray-200);
        flex: 1;
        max-width: 100px;
        overflow: hidden;
    }
    
    .net-flow-bar .fill {
        height: 100%;
        border-radius: 4px;
    }
    
    .net-flow-bar .fill.positive { background: var(--success); }
    .net-flow-bar .fill.negative { background: var(--danger); }
    
    /* === BADGES === */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
    }
    
    .badge.success { background: var(--success-bg); color: var(--success); }
    .badge.danger { background: var(--danger-bg); color: var(--danger); }
    .badge.warning { background: var(--warning-bg); color: var(--warning); }
    .badge.info { background: var(--info-bg); color: var(--info); }
    .badge.default { background: var(--gray-100); color: var(--gray-600); }
    
    /* === FILTER BAR === */
    .filter-bar {
        background: white;
        padding: 16px 20px;
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-sm);
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 16px;
        flex-wrap: wrap;
    }
    
    .filter-bar .filter-label {
        font-size: 13px;
        font-weight: 500;
        color: var(--gray-600);
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    /* === WORKSTATION TABLE === */
    .data-table-wrapper {
        background: white;
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-md);
        overflow: hidden;
    }
    
    .data-table-header {
        background: var(--gray-50);
        padding: 16px 20px;
        border-bottom: 1px solid var(--gray-200);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .data-table-header .title {
        font-weight: 600;
        color: var(--gray-800);
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .data-table-header .count {
        background: var(--primary);
        color: white;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 12px;
    }
    
    /* === STATS BAR === */
    .stats-bar {
        display: flex;
        gap: 24px;
        padding: 12px 20px;
        background: var(--gray-50);
        border-radius: var(--radius-md);
        margin-top: 16px;
    }
    
    .stats-bar .stat-item {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 13px;
        color: var(--gray-600);
    }
    
    .stats-bar .stat-item .value {
        font-weight: 600;
        color: var(--gray-800);
    }
    
    /* === COMPARE SELECTOR === */
    .compare-selector {
        background: white;
        padding: 12px 16px;
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-sm);
        display: inline-flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;
    }
    
    .compare-selector .label {
        font-size: 13px;
        color: var(--gray-500);
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    /* === EMPTY STATE === */
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        color: var(--gray-400);
    }
    
    .empty-state .icon {
        font-size: 48px;
        margin-bottom: 16px;
    }
    
    .empty-state .title {
        font-size: 18px;
        font-weight: 600;
        color: var(--gray-600);
        margin-bottom: 8px;
    }
    
    .empty-state .description {
        font-size: 14px;
    }
    
    /* === CUSTOM DATAFRAME === */
    .stDataFrame {
        border-radius: var(--radius-md) !important;
        overflow: hidden;
    }
    
    /* === RESPONSIVE === */
    @media (max-width: 1200px) {
        .kpi-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    
    @media (max-width: 768px) {
        .kpi-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- CORE UTILITIES ---

def clean_text_strict(text):
    if pd.isna(text) or text == "":
        return ""
    text = str(text)
    text = unicodedata.normalize('NFKC', text)
    return text.strip().lower()

def clean_url_for_compare(url):
    if pd.isna(url) or url == "":
        return ""
    url = str(url).strip().lower()
    url = url.replace("https://", "").replace("http://", "").replace("www.", "")
    return url.rstrip('/')

def clean_rank(val):
    try:
        val = str(val).lower().strip()
        if val in ['-', 'n/a', '', 'nan', 'none']: 
            return None
        result = int(float(val))
        return result if result <= 100 else None
    except: 
        return None

def safe_int(val, default=0):
    if pd.isna(val):
        return default
    try:
        return int(val)
    except:
        return default

# --- TREND CLASSIFICATION ---

def classify_trend_extended(current_rank, previous_rank, threshold=100):
    curr_valid = current_rank is not None and not pd.isna(current_rank)
    prev_valid = previous_rank is not None and not pd.isna(previous_rank)
    
    if prev_valid and previous_rank <= threshold:
        if not curr_valid:
            return {'label': 'Rớt Top 100', 'type': 'dropped', 'severity': 5}
    
    if curr_valid and current_rank <= threshold:
        if not prev_valid:
            return {'label': 'Mới vào Top 100', 'type': 'new', 'severity': 1}
    
    if not curr_valid:
        return {'label': 'Ngoài Top 100', 'type': 'out', 'severity': 0}
    
    if not prev_valid:
        return {'label': 'Đi ngang', 'type': 'stable', 'severity': 1}
    
    delta = int(previous_rank) - int(current_rank)
    
    if delta >= 10:
        return {'label': 'Tăng mạnh', 'type': 'surge', 'severity': 2}
    elif delta > 0:
        return {'label': 'Tăng', 'type': 'up', 'severity': 2}
    elif delta == 0:
        return {'label': 'Đi ngang', 'type': 'stable', 'severity': 1}
    elif delta > -10:
        return {'label': 'Giảm', 'type': 'down', 'severity': 3}
    else:
        return {'label': 'Giảm mạnh', 'type': 'crash', 'severity': 4}

def get_trend_badge(trend_type):
    """Trả về HTML badge cho trend"""
    badges = {
        'surge': f'<span class="badge success">{icon("rocket", "#10b981")} Tăng mạnh</span>',
        'up': f'<span class="badge success">{icon("trend_up", "#10b981")} Tăng</span>',
        'stable': f'<span class="badge default">{icon("minus", "#6b7280")} Đi ngang</span>',
        'down': f'<span class="badge warning">{icon("trend_down", "#f59e0b")} Giảm</span>',
        'crash': f'<span class="badge danger">{icon("flame", "#ef4444")} Giảm mạnh</span>',
        'dropped': f'<span class="badge danger">{icon("alert_triangle", "#ef4444")} Rớt Top 100</span>',
        'new': f'<span class="badge info">{icon("sparkles", "#3b82f6")} Mới vào</span>',
        'out': f'<span class="badge default">{icon("x_circle", "#6b7280")} Ngoài Top 100</span>',
    }
    return badges.get(trend_type, '')

# --- DATA LOADERS ---

def load_master_data(project_path):
    master_file = os.path.join(project_path, 'master.xlsx')
    if os.path.exists(master_file):
        try:
            df = pd.read_excel(master_file)
            df.columns = [clean_text_strict(c) for c in df.columns]
            
            col_map = {}
            for c in df.columns:
                if 'keyword' in c: col_map['keyword'] = c
                elif 'topic' in c: col_map['topic'] = c
                elif 'target' in c and 'url' in c: col_map['target_url'] = c
            
            df = df.rename(columns={
                col_map.get('keyword', 'keyword'): 'Keyword',
                col_map.get('topic', 'topic'): 'Topic',
                col_map.get('target_url', 'target_url'): 'Target URL',
            })
            
            if 'Keyword' in df.columns:
                df['Keyword_Join'] = df['Keyword'].apply(clean_text_strict)
                return df
        except Exception as e:
            st.error(f"Lỗi Master File: {e}")
    return None

def process_ranking_data(uploaded_file, master_df):
    try:
        df = pd.read_excel(uploaded_file)
        
        rank_cols_lower = [str(c).lower().strip() for c in df.columns]
        key_col, url_col = None, None
        
        for idx, c in enumerate(rank_cols_lower):
            if 'keyword' in c: key_col = df.columns[idx]
            if 'url' in c and 'target' not in c: url_col = df.columns[idx]
            
        if not key_col:
            st.error("File Tracking thiếu cột Keyword!")
            return pd.DataFrame(), [], []

        rename_dict = {key_col: "Keyword"}
        if url_col: rename_dict[url_col] = "Actual_URL"
        df.rename(columns=rename_dict, inplace=True)
        
        id_vars = ['Keyword']
        if "Actual_URL" in df.columns: id_vars.append("Actual_URL")
        
        date_cols = [c for c in df.columns if c not in id_vars]
        df_long = pd.melt(df, id_vars=id_vars, value_vars=date_cols, var_name='Date_Raw', value_name='Rank')
        
        df_long['Date'] = pd.to_datetime(df_long['Date_Raw'], errors='coerce')
        df_long = df_long.dropna(subset=['Date']) 
        df_long['Rank'] = df_long['Rank'].apply(clean_rank)
        df_long['Keyword_Join'] = df_long['Keyword'].apply(clean_text_strict)
        
        full_df = df_long.copy()
        missing_keys = []
        all_dates = sorted(df_long['Date'].unique(), reverse=True)

        if master_df is not None:
            full_df = pd.merge(df_long, master_df[['Keyword_Join', 'Topic', 'Target URL']], 
                               on='Keyword_Join', how='left')
            
            missing_mask = full_df['Topic'].isna()
            if missing_mask.any():
                missing_keys = full_df[missing_mask]['Keyword'].unique().tolist()
                
            full_df['Topic'].fillna('Unmapped', inplace=True)
            full_df['Target URL'].fillna('', inplace=True)
        else:
            full_df['Topic'] = 'Unknown'
            full_df['Target URL'] = ''
            missing_keys = full_df['Keyword'].unique().tolist()
            
        return full_df.sort_values(by=['Date', 'Keyword'], ascending=[False, True]), missing_keys, all_dates
        
    except Exception as e:
        st.error(f"Lỗi Tracking File: {e}")
        return pd.DataFrame(), [], []

# --- ANALYSIS FUNCTIONS ---

def calculate_historical_kpi(df_full, all_dates, top_n_list=[3, 5, 10, 15, 30, 50, 100]):
    history_data = []
    
    for date in all_dates:
        df_date = df_full[df_full['Date'] == date]
        total_kw = len(df_date)
        
        if total_kw == 0:
            continue
            
        row = {'Date': date, 'Total_KW': total_kw}
        
        for top_n in top_n_list:
            count = len(df_date[df_date['Rank'].notna() & (df_date['Rank'] <= top_n)])
            row[f'Top{top_n}_count'] = count
            row[f'Top{top_n}_pct'] = (count / total_kw) * 100
        
        row['Out100_count'] = len(df_date[df_date['Rank'].isna()])
        history_data.append(row)
    
    return pd.DataFrame(history_data).sort_values('Date', ascending=False)

def get_available_compare_dates(all_dates, current_date):
    if len(all_dates) <= 1:
        return {}
    
    compare_options = {}
    other_dates = [d for d in all_dates if d != current_date]
    
    for date in other_dates:
        days_diff = (current_date - date).days
        
        if days_diff == 1:
            label = "Hôm qua"
        elif days_diff <= 7:
            label = f"{days_diff} ngày trước"
        else:
            label = f"{days_diff} ngày trước ({pd.to_datetime(date).strftime('%d/%m')})"
        
        compare_options[label] = date
    
    return compare_options

def calculate_comparison(df_history, current_date, compare_date):
    if df_history.empty or compare_date is None:
        return {}
    
    curr_row = df_history[df_history['Date'] == current_date]
    comp_row = df_history[df_history['Date'] == compare_date]
    
    if curr_row.empty or comp_row.empty:
        return {}
    
    curr_row = curr_row.iloc[0]
    comp_row = comp_row.iloc[0]
    
    results = {}
    for top_n in [3, 5, 10, 15, 30, 50, 100]:
        curr_count = safe_int(curr_row.get(f'Top{top_n}_count', 0))
        comp_count = safe_int(comp_row.get(f'Top{top_n}_count', 0))
        
        delta = curr_count - comp_count
        delta_pct = ((curr_count - comp_count) / comp_count * 100) if comp_count > 0 else 0
        
        results[f'top{top_n}'] = {
            'current': curr_count,
            'compare': comp_count,
            'delta': delta,
            'delta_pct': round(delta_pct, 1)
        }
    
    return results

def calculate_topic_health(df_curr, top_n_threshold=10):
    topic_stats = df_curr.groupby('Topic').agg({
        'Keyword': 'count',
    }).rename(columns={'Keyword': 'Total_KW'})
    
    df_in_top = df_curr[df_curr['Rank'].notna() & (df_curr['Rank'] <= top_n_threshold)]
    in_top_counts = df_in_top.groupby('Topic').size().rename('In_Top')
    
    up_counts = df_curr[df_curr['Change'] > 0].groupby('Topic').size().rename('Up')
    down_counts = df_curr[df_curr['Change'] < 0].groupby('Topic').size().rename('Down')
    
    dropped_counts = df_curr[df_curr['Trend_Type'] == 'dropped'].groupby('Topic').size().rename('Dropped')
    new_counts = df_curr[df_curr['Trend_Type'] == 'new'].groupby('Topic').size().rename('New_Entry')
    
    topic_health = topic_stats.join([in_top_counts, up_counts, down_counts, dropped_counts, new_counts]).fillna(0)
    
    topic_health['In_Top_Pct'] = (topic_health['In_Top'] / topic_health['Total_KW'] * 100).round(1)
    topic_health['Net_Flow'] = topic_health['Up'] - topic_health['Down']
    
    return topic_health.reset_index().sort_values('In_Top_Pct', ascending=False)

# === MAIN APP ===

# Sidebar
with st.sidebar:
    st.markdown(f"""
    <div style="padding: 20px 0; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 20px;">
        <div style="font-size: 24px; font-weight: 700; color: white; display: flex; align-items: center; justify-content: center; gap: 10px;">
            📊 SEO Center
        </div>
        <div style="font-size: 12px; color: rgba(255,255,255,0.5); margin-top: 4px;">Version 10.0</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<div style='display: flex; align-items: center; gap: 8px; color: white; margin-bottom: 12px;'>📁 <strong>Project</strong></div>", unsafe_allow_html=True)
    
    if not os.path.exists('projects'): 
        os.makedirs('projects')
        
    projects = [f for f in os.listdir('projects') if os.path.isdir(os.path.join('projects', f))]
    selected_project = st.selectbox("Chọn dự án", ["-- Chọn Dự Án --"] + projects, label_visibility="collapsed")
    
    if selected_project != "-- Chọn Dự Án --":
        st.markdown(f"<div style='display: flex; align-items: center; gap: 8px; color: white; margin: 24px 0 12px 0;'>🎯 <strong>KPI Targets</strong></div>", unsafe_allow_html=True)
        
        kpi = {
            3: st.number_input("Top 3 (%)", value=30, min_value=0, max_value=100, step=5),
            5: st.number_input("Top 5 (%)", value=50, min_value=0, max_value=100, step=5),
            10: st.number_input("Top 10 (%)", value=70, min_value=0, max_value=100, step=5),
            30: st.number_input("Top 30 (%)", value=90, min_value=0, max_value=100, step=5)
        }
        
        st.markdown(f"<div style='display: flex; align-items: center; gap: 8px; color: white; margin: 24px 0 12px 0;'>📤 <strong>Upload Data</strong></div>", unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Upload Ranking File", type=['xlsx', 'xls'], label_visibility="collapsed")

# Main Content
if selected_project != "-- Chọn Dự Án --":
    project_path = os.path.join('projects', selected_project)
    master_df = load_master_data(project_path)
    
    if uploaded_file:
        df, missing_keys, all_dates = process_ranking_data(uploaded_file, master_df)
        
        if not df.empty and len(all_dates) > 0:
            curr_date = all_dates[0]
            df_history = calculate_historical_kpi(df, all_dates)
            df_curr = df[df['Date'] == curr_date].copy()
            
            # Calculate trends
            prev_date = all_dates[1] if len(all_dates) > 1 else None
            
            if prev_date is not None:
                prev = df[df['Date'] == prev_date][['Keyword_Join', 'Rank']].copy()
                prev = prev.rename(columns={'Rank': 'Rank_Prev'})
                df_curr = df_curr.merge(prev, on='Keyword_Join', how='left')
            else:
                df_curr['Rank_Prev'] = None
            
            def calc_change(row):
                curr = row['Rank']
                prev = row['Rank_Prev']
                if pd.isna(curr) or pd.isna(prev):
                    return 0
                return int(prev) - int(curr)
            
            df_curr['Change'] = df_curr.apply(calc_change, axis=1)
            
            df_curr['Trend_Info'] = df_curr.apply(
                lambda row: classify_trend_extended(row['Rank'], row['Rank_Prev']), axis=1
            )
            df_curr['Trend_Label'] = df_curr['Trend_Info'].apply(lambda x: x['label'])
            df_curr['Trend_Type'] = df_curr['Trend_Info'].apply(lambda x: x['type'])
            df_curr['Trend_Severity'] = df_curr['Trend_Info'].apply(lambda x: x['severity'])

            # === HEADER ===
            total_kw = len(df_curr)
            top10_count = len(df_curr[df_curr['Rank'].notna() & (df_curr['Rank'] <= 10)])
            
            st.markdown(f"""
            <div class="dashboard-header">
                <h1>📊 Dashboard: {selected_project}</h1>
                <div class="subtitle">
                    <span class="stat-badge">📅 {pd.to_datetime(curr_date).strftime('%d/%m/%Y')}</span>
                    <span class="stat-badge"># {total_kw} keywords</span>
                    <span class="stat-badge">📈 {len(all_dates)} ngày dữ liệu</span>
                    <span class="stat-badge">🎯 {top10_count} trong Top 10</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # === ALERTS ===
            dropped_kw = df_curr[df_curr['Trend_Type'] == 'dropped']
            new_kw = df_curr[df_curr['Trend_Type'] == 'new']
            
            if len(dropped_kw) > 0 or len(new_kw) > 0:
                col_a1, col_a2 = st.columns(2)
                
                with col_a1:
                    if len(dropped_kw) > 0:
                        dropped_list = ', '.join(dropped_kw['Keyword'].head(3).tolist())
                        more = f" và {len(dropped_kw) - 3} keywords khác" if len(dropped_kw) > 3 else ""
                        st.markdown(f"""
                        <div class="alert-box danger">
                            <div class="icon-wrapper">⚠</div>
                            <div class="content">
                                <div class="title">{len(dropped_kw)} từ khóa rớt khỏi Top 100</div>
                                <div class="description">{dropped_list}{more}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
                with col_a2:
                    if len(new_kw) > 0:
                        new_list = ', '.join(new_kw['Keyword'].head(3).tolist())
                        more = f" và {len(new_kw) - 3} keywords khác" if len(new_kw) > 3 else ""
                        st.markdown(f"""
                        <div class="alert-box success">
                            <div class="icon-wrapper">✦</div>
                            <div class="content">
                                <div class="title">{len(new_kw)} từ khóa mới vào Top 100</div>
                                <div class="description">{new_list}{more}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            
            # === KPI SECTION ===
            st.markdown(f"""
            <div class="section-header">
                <div class="icon">📊</div>
                <h2>Phân bổ & KPI</h2>
            </div>
            """, unsafe_allow_html=True)
            
            # Compare selector
            compare_options = get_available_compare_dates(all_dates, curr_date)
            
            col_cmp, col_hist = st.columns([2, 1])
            with col_cmp:
                if compare_options:
                    selected_compare_label = st.selectbox(
                        "📅 So sánh với:",
                        options=list(compare_options.keys()),
                        index=0
                    )
                    compare_date = compare_options[selected_compare_label]
                else:
                    selected_compare_label = None
                    compare_date = None
                    st.info("Chỉ có 1 ngày dữ liệu")
                    
            with col_hist:
                show_history = st.checkbox("📈 Hiển thị lịch sử", value=False)
            
            comparison = calculate_comparison(df_history, curr_date, compare_date) if compare_date else {}
            
            # KPI Cards
            limits = [3, 5, 10, 15, 30, 50, 100]
            cols = st.columns(4)
            
            for i, lim in enumerate(limits[:4]):
                with cols[i]:
                    cnt = len(df_curr[df_curr['Rank'].notna() & (df_curr['Rank'] <= lim)])
                    pct = (cnt / total_kw) * 100 if total_kw > 0 else 0
                    
                    comp_data = comparison.get(f'top{lim}', {})
                    delta = comp_data.get('delta', 0)
                    delta_pct = comp_data.get('delta_pct', 0)
                    
                    if delta > 0:
                        trend_html = f'<div class="trend up">↑ +{delta}</div>'
                        trend_class = "success"
                    elif delta < 0:
                        trend_html = f'<div class="trend down">↓ {delta}</div>'
                        trend_class = "danger"
                    else:
                        trend_html = f'<div class="trend stable">— 0</div>'
                        trend_class = "info"
                    
                    compare_text = f"vs {selected_compare_label}: {delta:+d} ({delta_pct:+.1f}%)" if selected_compare_label else ""
                    
                    target_html = ""
                    if lim in kpi:
                        gap = pct - kpi[lim]
                        if gap >= 0:
                            target_html = f'<div class="target-status met">✓ Đạt +{gap:.1f}%</div>'
                        else:
                            target_html = f'<div class="target-status miss">✗ Thiếu {gap:.1f}%</div>'
                    
                    st.markdown(f"""
                    <div class="kpi-card {trend_class}">
                        <div class="label">Top {lim}</div>
                        <div class="value">{cnt}</div>
                        <div class="percentage">{pct:.1f}%</div>
                        {trend_html}
                        <div class="compare">{compare_text}</div>
                        {target_html}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Second row
            cols2 = st.columns(4)
            
            for i, lim in enumerate(limits[4:7]):
                with cols2[i]:
                    cnt = len(df_curr[df_curr['Rank'].notna() & (df_curr['Rank'] <= lim)])
                    pct = (cnt / total_kw) * 100 if total_kw > 0 else 0
                    
                    comp_data = comparison.get(f'top{lim}', {})
                    delta = comp_data.get('delta', 0)
                    
                    if delta > 0:
                        trend_html = f'<div class="trend up">↑ +{delta}</div>'
                        trend_class = "success"
                    elif delta < 0:
                        trend_html = f'<div class="trend down">↓ {delta}</div>'
                        trend_class = "danger"
                    else:
                        trend_html = f'<div class="trend stable">— 0</div>'
                        trend_class = "info"
                    
                    target_html = ""
                    if lim in kpi:
                        gap = pct - kpi[lim]
                        if gap >= 0:
                            target_html = f'<div class="target-status met">✓ Đạt +{gap:.1f}%</div>'
                        else:
                            target_html = f'<div class="target-status miss">✗ Thiếu {gap:.1f}%</div>'
                    
                    st.markdown(f"""
                    <div class="kpi-card {trend_class}">
                        <div class="label">Top {lim}</div>
                        <div class="value">{cnt}</div>
                        <div class="percentage">{pct:.1f}%</div>
                        {trend_html}
                        {target_html}
                    </div>
                    """, unsafe_allow_html=True)
            
            # OUT > 100 Card
            with cols2[3]:
                cnt_out = len(df_curr[df_curr['Rank'].isna()])
                pct_out = (cnt_out / total_kw * 100) if total_kw > 0 else 0
                net = len(new_kw) - len(dropped_kw)
                
                net_color = "var(--success)" if net >= 0 else "var(--danger)"
                net_symbol = "+" if net >= 0 else ""
                
                st.markdown(f"""
                <div class="kpi-card danger">
                    <div class="label">Out of Top 100</div>
                    <div class="value">{cnt_out}</div>
                    <div class="percentage">{pct_out:.1f}%</div>
                    <div style="margin-top: 12px; font-size: 13px; color: var(--gray-500);">
                        <span style="color: var(--danger);">↓ Rớt: {len(dropped_kw)}</span> &nbsp;|&nbsp; 
                        <span style="color: var(--success);">↑ Mới: {len(new_kw)}</span>
                    </div>
                    <div style="margin-top: 8px; font-weight: 600; font-size: 15px; color: {net_color};">
                        Net: {net_symbol}{net}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # History Table
            if show_history:
                st.markdown(f"""
                <div class="section-header" style="margin-top: 24px;">
                    <div class="icon">📈</div>
                    <h2>Lịch sử xếp hạng</h2>
                </div>
                """, unsafe_allow_html=True)
                
                display_history = df_history.copy()
                display_history['Date'] = pd.to_datetime(display_history['Date']).dt.strftime('%d/%m/%Y')
                
                display_cols = ['Date', 'Total_KW']
                for top_n in [3, 5, 10, 30, 100]:
                    display_cols.append(f'Top{top_n}_count')
                display_cols.append('Out100_count')
                
                rename_map = {'Total_KW': 'Tổng KW', 'Out100_count': 'Out>100'}
                for top_n in [3, 5, 10, 30, 100]:
                    rename_map[f'Top{top_n}_count'] = f'Top {top_n}'
                
                st.dataframe(
                    display_history[display_cols].rename(columns=rename_map),
                    use_container_width=True,
                    hide_index=True
                )

            # === TOPIC HEALTH ===
            st.markdown(f"""
            <div class="section-header">
                <div class="icon">🎯</div>
                <h2>Sức khỏe Topic</h2>
            </div>
            """, unsafe_allow_html=True)
            
            col_th1, col_th2 = st.columns([3, 1])
            with col_th1:
                top_threshold = st.radio(
                    "Phân tích theo ngưỡng:",
                    options=[3, 5, 10, 30, 100],
                    format_func=lambda x: f"Top {x}",
                    horizontal=True,
                    index=2
                )
            
            df_topic_health = calculate_topic_health(df_curr, top_threshold)
            
            # Topic Health Table
            st.dataframe(
                df_topic_health[['Topic', 'Total_KW', 'In_Top', 'In_Top_Pct', 'Up', 'Down', 'Net_Flow']].rename(columns={
                    'Topic': 'Chủ đề',
                    'Total_KW': 'Tổng KW',
                    'In_Top': f'Trong Top {top_threshold}',
                    'In_Top_Pct': f'% Top {top_threshold}',
                    'Up': '↑ Tăng',
                    'Down': '↓ Giảm',
                    'Net_Flow': 'Net Flow'
                }),
                use_container_width=True,
                hide_index=True,
                column_config={
                    'Net Flow': st.column_config.ProgressColumn(
                        'Net Flow',
                        min_value=-10,
                        max_value=10,
                        format='%d'
                    )
                }
            )
            
            total_in_top = df_topic_health['In_Top'].sum()
            total_kw_topic = df_topic_health['Total_KW'].sum()
            st.markdown(f"""
            <div class="stats-bar">
                <div class="stat-item">
                    🎯
                    <span>Tổng quan: <span class="value">{int(total_in_top)}/{int(total_kw_topic)}</span> keywords trong Top {top_threshold}</span>
                </div>
                <div class="stat-item">
                    📊
                    <span>Tỷ lệ: <span class="value">{total_in_top/total_kw_topic*100:.1f}%</span></span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # === WORKSTATION ===
            st.markdown(f"""
            <div class="section-header">
                <div class="icon">⚡</div>
                <h2>Workstation</h2>
            </div>
            """, unsafe_allow_html=True)
            
            # Issue Analysis
            def analyze_issue(row):
                t = clean_url_for_compare(row['Target URL'])
                c = clean_url_for_compare(row['Actual_URL']) if pd.notna(row.get('Actual_URL')) else ""
                if t and c and (t not in c):
                    return "Cannibal"
                if not t:
                    return "Missing Target"
                return "OK"

            df_curr['Issue'] = df_curr.apply(analyze_issue, axis=1)
            
            # Filters
            col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns([2, 1, 1.5, 1.5, 2])
            
            with col_f1:
                sel_top = st.multiselect("Topic", sorted(df_curr['Topic'].unique()))
            with col_f2:
                sel_rnk = st.selectbox("Rank", ["All", "Top 3", "Top 5", "Top 10", "Top 30", "Top 100", "Out > 100"])
            with col_f3:
                trend_options = ["All", "Tăng mạnh", "Tăng", "Đi ngang", "Giảm", "Giảm mạnh", "Rớt Top 100", "Mới vào Top 100"]
                sel_trend = st.selectbox("Xu hướng", trend_options)
            with col_f4:
                sel_issue = st.selectbox("Vấn đề", ["All", "Cannibal", "Missing Target", "OK"])
            with col_f5:
                search_txt = st.text_input("Tìm kiếm", placeholder="Keyword hoặc URL...")

            # Filter logic
            v = df_curr.copy()
            
            if sel_top: 
                v = v[v['Topic'].isin(sel_top)]
            
            if sel_rnk != "All":
                if sel_rnk == "Out > 100": 
                    v = v[v['Rank'].isna()]
                else: 
                    top_val = int(sel_rnk.replace("Top ", ""))
                    v = v[v['Rank'].notna() & (v['Rank'] <= top_val)]
            
            if sel_trend != "All":
                v = v[v['Trend_Label'] == sel_trend]
            
            if sel_issue != "All": 
                v = v[v['Issue'] == sel_issue]
            
            if search_txt:
                s = search_txt.lower()
                v = v[
                    v['Keyword'].str.lower().str.contains(s, na=False) | 
                    v['Actual_URL'].astype(str).str.lower().str.contains(s, na=False)
                ]

            v = v.sort_values(by=['Trend_Severity', 'Rank'], ascending=[False, True])
            
            # Display columns
            v['Rank_Display'] = v['Rank'].apply(lambda x: int(x) if pd.notna(x) else ">100")
            v['Change_Display'] = v['Change'].apply(lambda x: f"{int(x):+d}" if x != 0 else "-")

            # Results header
            st.markdown(f"""
            <div class="data-table-header">
                <div class="title">🔍 Kết quả lọc <span class="count">{len(v)}</span></div>
            </div>
            """, unsafe_allow_html=True)

            st.dataframe(
                v[['Keyword', 'Topic', 'Rank_Display', 'Change_Display', 'Trend_Label', 'Issue', 'Actual_URL', 'Target URL']].rename(columns={
                    'Rank_Display': 'Rank',
                    'Change_Display': 'Δ',
                    'Trend_Label': 'Xu hướng'
                }), 
                use_container_width=True, 
                height=500,
                column_config={
                    "Actual_URL": st.column_config.LinkColumn("Actual URL"), 
                    "Target URL": st.column_config.LinkColumn("Target URL"),
                }
            )
            
            # Stats bar
            st.markdown(f"""
            <div class="stats-bar">
                <div class="stat-item">🚀 Tăng mạnh: <span class="value">{len(v[v['Trend_Type']=='surge'])}</span></div>
                <div class="stat-item">↑ Tăng: <span class="value">{len(v[v['Trend_Type']=='up'])}</span></div>
                <div class="stat-item">↓ Giảm: <span class="value">{len(v[v['Trend_Type']=='down'])}</span></div>
                <div class="stat-item">🔥 Giảm mạnh: <span class="value">{len(v[v['Trend_Type']=='crash'])}</span></div>
                <div class="stat-item">⚠ Rớt: <span class="value">{len(v[v['Trend_Type']=='dropped'])}</span></div>
                <div class="stat-item">✦ Mới: <span class="value">{len(v[v['Trend_Type']=='new'])}</span></div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-state">
            <div style="font-size: 48px; margin-bottom: 16px;">📊</div>
            <div class="title">Chưa có dữ liệu</div>
            <div class="description">Vui lòng upload file ranking ở sidebar để bắt đầu phân tích</div>
        </div>
        """, unsafe_allow_html=True)
else:
    # Welcome screen
    st.markdown(f"""
    <div style="text-align: center; padding: 80px 20px;">
        <div style="font-size: 64px; margin-bottom: 24px;">📊</div>
        <h1 style="font-size: 32px; font-weight: 700; color: var(--gray-800); margin-bottom: 12px;">
            SEO Command Center
        </h1>
        <p style="font-size: 16px; color: var(--gray-500); max-width: 500px; margin: 0 auto 32px auto;">
            Công cụ theo dõi và phân tích thứ hạng từ khóa SEO chuyên nghiệp
        </p>
        <div style="background: white; padding: 32px; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); max-width: 600px; margin: 0 auto; text-align: left;">
            <h3 style="margin-bottom: 16px; color: var(--gray-800);">Bắt đầu nhanh</h3>
            <ol style="color: var(--gray-600); line-height: 2;">
                <li>Tạo folder dự án trong <code>projects/TenDuAn/</code></li>
                <li>Thêm file <code>master.xlsx</code> (Keyword, Topic, Target URL)</li>
                <li>Chọn dự án ở sidebar</li>
                <li>Upload file ranking</li>
            </ol>
        </div>
    </div>
    """, unsafe_allow_html=True)
