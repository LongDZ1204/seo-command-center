import streamlit as st
import pandas as pd
import unicodedata
from google.oauth2.service_account import Credentials
import gspread
from io import StringIO

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(
    page_title="SEO Command Center", 
    layout="wide", 
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# === MODERN CSS STYLES ===
st.markdown("""
<style>
    :root {
        --primary: #2563eb;
        --primary-light: #3b82f6;
        --primary-dark: #1d4ed8;
        --primary-bg: #eff6ff;
        --success: #10b981;
        --success-light: #34d399;
        --success-bg: #ecfdf5;
        --warning: #f59e0b;
        --warning-light: #fbbf24;
        --warning-bg: #fffbeb;
        --danger: #ef4444;
        --danger-light: #f87171;
        --danger-bg: #fef2f2;
        --info: #0ea5e9;
        --info-light: #38bdf8;
        --info-bg: #f0f9ff;
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
    }
    
    .stApp { background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); }
    .main .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1400px; }
    
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #1e3a5f 0%, #1e40af 100%); }
    [data-testid="stSidebar"] .stMarkdown { color: var(--gray-300); }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: white !important; }
    [data-testid="stSidebar"] label { color: var(--gray-300) !important; }
    
    .dashboard-header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        padding: 24px 32px; border-radius: var(--radius-xl); margin-bottom: 24px;
        box-shadow: var(--shadow-lg); color: white;
    }
    .dashboard-header h1 { margin: 0; font-size: 28px; font-weight: 700; display: flex; align-items: center; gap: 12px; }
    .dashboard-header .subtitle { margin-top: 8px; opacity: 0.9; font-size: 14px; display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
    .dashboard-header .stat-badge { background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 20px; font-size: 13px; display: inline-flex; align-items: center; gap: 6px; }
    
    .section-header { display: flex; align-items: center; gap: 10px; margin: 32px 0 16px 0; padding-bottom: 12px; border-bottom: 2px solid var(--primary-light); }
    .section-header h2 { margin: 0; font-size: 18px; font-weight: 600; color: var(--gray-800); }
    .section-header .icon { width: 32px; height: 32px; background: var(--primary); border-radius: var(--radius-sm); display: flex; align-items: center; justify-content: center; color: white; font-size: 16px; }
    
    /* GAP ANALYSIS CARD */
    .gap-card {
        background: white; border-radius: var(--radius-lg); padding: 24px;
        box-shadow: var(--shadow-md); border: 1px solid var(--gray-100);
        margin-bottom: 20px;
    }
    .gap-stat { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; padding-bottom: 16px; border-bottom: 1px solid var(--gray-100); }
    .gap-val { font-size: 24px; font-weight: 700; color: var(--primary-dark); }
    .gap-label { font-size: 13px; color: var(--gray-500); text-transform: uppercase; letter-spacing: 0.5px; }
    
    .topic-row {
        display: flex; align-items: center; gap: 12px; padding: 12px; 
        background: var(--gray-50); border-radius: var(--radius-md); margin-bottom: 8px;
        transition: all 0.2s;
    }
    .topic-row:hover { background: white; box-shadow: var(--shadow-sm); transform: translateX(4px); }
    .topic-rank { 
        width: 28px; height: 28px; background: var(--warning); color: white; 
        border-radius: 50%; display: flex; align-items: center; justify-content: center; 
        font-weight: 700; font-size: 14px; flex-shrink: 0;
    }
    .topic-info { flex: 1; min-width: 0; }
    .topic-name { font-weight: 600; font-size: 14px; color: var(--gray-800); margin-bottom: 2px; }
    .topic-desc { font-size: 12px; color: var(--gray-500); display: flex; gap: 10px; }
    .topic-action { 
        font-size: 12px; font-weight: 600; color: var(--primary); 
        background: var(--primary-bg); padding: 4px 10px; border-radius: 12px;
        white-space: nowrap;
    }
    
    .kpi-card {
        background: white; border-radius: var(--radius-lg); padding: 20px;
        box-shadow: var(--shadow-md); border: 1px solid var(--gray-100);
        transition: all 0.2s ease; position: relative; overflow: hidden;
        min-height: 220px; display: flex; flex-direction: column;
    }
    .kpi-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-lg); }
    .kpi-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: var(--primary); }
    .kpi-card.success::before { background: var(--success); }
    .kpi-card.warning::before { background: var(--warning); }
    .kpi-card.danger::before { background: var(--danger); }
    .kpi-card.info::before { background: var(--info); }
    .kpi-card .label { font-size: 12px; font-weight: 600; color: var(--gray-500); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
    .kpi-card .value { font-size: 32px; font-weight: 700; color: var(--gray-900); line-height: 1; margin-bottom: 4px; }
    .kpi-card .percentage { font-size: 14px; color: var(--gray-500); margin-bottom: 12px; }
    .kpi-card .trend { display: inline-flex; align-items: center; gap: 4px; font-size: 13px; font-weight: 600; padding: 4px 10px; border-radius: 20px; }
    .kpi-card .trend.up { background: var(--success-bg); color: var(--success); }
    .kpi-card .trend.down { background: var(--danger-bg); color: var(--danger); }
    .kpi-card .trend.stable { background: var(--gray-100); color: var(--gray-500); }
    .kpi-card .compare { font-size: 12px; color: var(--gray-400); margin-top: 8px; }
    .kpi-card .target-status { margin-top: 12px; padding: 8px 12px; border-radius: var(--radius-sm); font-size: 12px; font-weight: 600; display: flex; align-items: center; gap: 6px; }
    .kpi-card .target-status.met { background: var(--success-bg); color: var(--success); }
    .kpi-card .target-status.miss { background: var(--danger-bg); color: var(--danger); }
    
    .alert-box { padding: 16px 20px; border-radius: var(--radius-md); margin-bottom: 16px; display: flex; align-items: flex-start; gap: 12px; }
    .alert-box.danger { background: var(--danger-bg); border: 1px solid #fecaca; }
    .alert-box.success { background: var(--success-bg); border: 1px solid #a7f3d0; }
    .alert-box.warning { background: var(--warning-bg); border: 1px solid #fde68a; }
    .alert-box.info { background: var(--primary-bg); border: 1px solid #bfdbfe; }
    .alert-box .icon-wrapper { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-size: 18px; }
    .alert-box.danger .icon-wrapper { background: var(--danger); color: white; }
    .alert-box.success .icon-wrapper { background: var(--success); color: white; }
    .alert-box.info .icon-wrapper { background: var(--primary); color: white; }
    .alert-box .content { flex: 1; }
    .alert-box .title { font-weight: 600; font-size: 14px; margin-bottom: 4px; }
    .alert-box.danger .title { color: var(--danger); }
    .alert-box.success .title { color: var(--success); }
    .alert-box.info .title { color: var(--primary); }
    .alert-box .description { font-size: 13px; color: var(--gray-600); }
    
    .stats-bar { display: flex; gap: 24px; padding: 12px 20px; background: var(--primary-bg); border-radius: var(--radius-md); margin-top: 16px; flex-wrap: wrap; border: 1px solid #bfdbfe; }
    .stats-bar .stat-item { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--gray-600); }
    .stats-bar .stat-item .value { font-weight: 600; color: var(--primary-dark); }
    
    .data-table-header { background: var(--primary-bg); padding: 16px 20px; border-bottom: 1px solid #bfdbfe; display: flex; justify-content: space-between; align-items: center; border-radius: var(--radius-lg) var(--radius-lg) 0 0; }
    .data-table-header .title { font-weight: 600; color: var(--primary-dark); display: flex; align-items: center; gap: 8px; }
    .data-table-header .count { background: var(--primary); color: white; padding: 2px 10px; border-radius: 20px; font-size: 12px; }
    .data-table-header .compare-info { font-size: 12px; color: var(--gray-500); background: white; padding: 4px 12px; border-radius: 20px; }
    
    .setup-card { background: white; padding: 32px; border-radius: var(--radius-lg); box-shadow: var(--shadow-md); margin-bottom: 24px; border-top: 4px solid var(--primary); }
    .setup-card h3 { color: var(--primary-dark); margin-bottom: 16px; }
    .setup-card ol { color: var(--gray-600); line-height: 2; }
    .setup-card code { background: var(--primary-bg); padding: 2px 8px; border-radius: 4px; font-size: 13px; color: var(--primary-dark); }
    
    .connection-status { padding: 12px 16px; border-radius: var(--radius-md); margin-bottom: 16px; display: flex; align-items: center; gap: 10px; }
    .connection-status.connected { background: var(--success-bg); color: var(--success); }
    .connection-status.disconnected { background: var(--danger-bg); color: var(--danger); }
    
    .workstation-compare-badge { 
        background: var(--primary-bg); 
        border: 1px solid var(--primary-light); 
        padding: 8px 16px; 
        border-radius: var(--radius-md); 
        margin-bottom: 16px;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 13px;
        color: var(--primary-dark);
    }
</style>
""", unsafe_allow_html=True)

# --- GOOGLE SHEETS CONNECTION ---

@st.cache_resource
def get_google_connection():
    try:
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        )
        client = gspread.authorize(credentials)
        return client
    except Exception as e:
        return None

@st.cache_data(ttl=300)
def load_projects_from_sheet(_client, spreadsheet_url):
    try:
        spreadsheet = _client.open_by_url(spreadsheet_url)
        settings_sheet = spreadsheet.worksheet("Settings")
        data = settings_sheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Lỗi load Settings: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_master_from_sheet(_client, spreadsheet_url, project_name):
    try:
        spreadsheet = _client.open_by_url(spreadsheet_url)
        master_sheet = spreadsheet.worksheet(f"Master_{project_name}")
        data = master_sheet.get_all_records()
        df = pd.DataFrame(data)
        
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
        st.error(f"Lỗi load Master_{project_name}: {e}")
        return None

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

# --- DATA PROCESSING ---

def process_ranking_data(raw_df, master_df):
    try:
        df = raw_df.copy()
        
        rank_cols_lower = [str(c).lower().strip() for c in df.columns]
        key_col, url_col = None, None
        
        for idx, c in enumerate(rank_cols_lower):
            if 'keyword' in c: key_col = df.columns[idx]
            if 'url' in c and 'target' not in c: url_col = df.columns[idx]
            
        if not key_col:
            st.error("Dữ liệu thiếu cột Keyword!")
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

        if master_df is not None and not master_df.empty:
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
        st.error(f"Lỗi xử lý dữ liệu: {e}")
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
        date_str = pd.to_datetime(date).strftime('%d/%m/%Y')
        
        if days_diff == 1:
            label = f"Hôm qua ({date_str})"
        else:
            label = f"{days_diff} ngày trước ({date_str})"
        
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

# === NEW FEATURE: KPI GAP FILLER ===
def calculate_kpi_gap_actions(df_curr, kpi_settings):
    results = {}
    
    # Định nghĩa vùng Striking Distance cho từng KPI
    striking_ranges = {
        3: (4, 10),
        5: (6, 10),
        10: (11, 20),
        30: (31, 40)
    }
    
    total_kw = len(df_curr)
    
    for kpi_level, target_pct in kpi_settings.items():
        if kpi_level not in striking_ranges: continue
        
        # 1. Tính Gap
        current_count = len(df_curr[df_curr['Rank'].notna() & (df_curr['Rank'] <= kpi_level)])
        target_count = int(total_kw * target_pct / 100)
        gap_count = target_count - current_count
        
        if gap_count <= 0:
            results[kpi_level] = {'status': 'met', 'gap': 0, 'data': pd.DataFrame()}
            continue
            
        # 2. Tìm Topic cứu tinh
        min_rank, max_rank = striking_ranges[kpi_level]
        striking_keywords = df_curr[(df_curr['Rank'] >= min_rank) & (df_curr['Rank'] <= max_rank)]
        
        if striking_keywords.empty:
            results[kpi_level] = {'status': 'miss', 'gap': gap_count, 'data': pd.DataFrame()}
            continue
            
        # Gom nhóm theo Topic
        topic_analysis = striking_keywords.groupby('Topic').agg({
            'Keyword': 'count',
            'Target URL': lambda x: x.mode()[0] if not x.mode().empty else 'N/A' # Tìm URL phổ biến nhất trong nhóm này
        }).reset_index().rename(columns={'Keyword': 'Striking_Count', 'Target URL': 'Best_URL'})
        
        topic_analysis['Fill_Pct'] = (topic_analysis['Striking_Count'] / gap_count * 100).clip(upper=100)
        topic_analysis = topic_analysis.sort_values('Striking_Count', ascending=False).head(5)
        
        results[kpi_level] = {
            'status': 'miss',
            'gap': gap_count,
            'data': topic_analysis
        }
        
    return results

# === MAIN APP ===

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="padding: 20px 0; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 20px;">
        <div style="font-size: 24px; font-weight: 700; color: white; display: flex; align-items: center; justify-content: center; gap: 10px;">
            📊 SEO Center
        </div>
        <div style="font-size: 12px; color: rgba(255,255,255,0.5); margin-top: 4px;">Version 12.0 - Gap Filler</div>
    </div>
    """, unsafe_allow_html=True)
    
    gc = get_google_connection()
    
    raw_df_input = None 
    kpi_settings = {} 

    if gc:
        st.markdown("""
        <div class="connection-status connected">
            ✓ Đã kết nối Google Sheets
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='color: white; margin-bottom: 8px;'>📋 <strong>Google Sheet URL</strong></div>", unsafe_allow_html=True)
        
        spreadsheet_url = st.text_input(
            "Spreadsheet URL",
            value=st.secrets.get("spreadsheet_url", ""),
            label_visibility="collapsed",
            placeholder="Paste Google Sheet URL..."
        )
        
        if spreadsheet_url:
            projects_df = load_projects_from_sheet(gc, spreadsheet_url)
            
            if not projects_df.empty and 'project_name' in projects_df.columns:
                project_list = projects_df['project_name'].tolist()
                
                st.markdown("<div style='color: white; margin: 16px 0 8px 0;'>📁 <strong>Project</strong></div>", unsafe_allow_html=True)
                selected_project = st.selectbox("Chọn dự án", ["-- Chọn Dự Án --"] + project_list, label_visibility="collapsed")
                
                if selected_project != "-- Chọn Dự Án --":
                    project_settings = projects_df[projects_df['project_name'] == selected_project].iloc[0]
                    
                    # === KPI SETTINGS (MANUAL INPUT RETURNED) ===
                    st.markdown("<div style='color: white; margin: 16px 0 8px 0;'>🎯 <strong>KPI Targets (%)</strong></div>", unsafe_allow_html=True)
                    
                    col_k1, col_k2 = st.columns(2)
                    with col_k1:
                         kpi_3 = st.number_input("Top 3", value=int(project_settings.get('kpi_top3', 30)), min_value=0, max_value=100)
                         kpi_10 = st.number_input("Top 10", value=int(project_settings.get('kpi_top10', 70)), min_value=0, max_value=100)
                    with col_k2:
                         kpi_5 = st.number_input("Top 5", value=int(project_settings.get('kpi_top5', 50)), min_value=0, max_value=100)
                         kpi_30 = st.number_input("Top 30", value=int(project_settings.get('kpi_top30', 90)), min_value=0, max_value=100)

                    kpi_settings = {3: kpi_3, 5: kpi_5, 10: kpi_10, 30: kpi_30}
                    
                    # === INPUT METHOD ===
                    st.markdown("<div style='color: white; margin: 24px 0 8px 0;'>📥 <strong>Input Ranking</strong></div>", unsafe_allow_html=True)
                    input_method = st.radio("Chọn phương thức:", ["Upload Excel", "Paste Data"], label_visibility="collapsed")
                    
                    if input_method == "Upload Excel":
                        uploaded_file = st.file_uploader("Upload file", type=['xlsx', 'xls'], label_visibility="collapsed")
                        if uploaded_file:
                            try:
                                raw_df_input = pd.read_excel(uploaded_file)
                            except Exception as e:
                                st.error(f"Lỗi đọc file: {e}")
                    else:
                        paste_data = st.text_area("Dán dữ liệu Excel vào đây", height=150, placeholder="Copy từ Excel bao gồm cả Header...")
                        if paste_data:
                            try:
                                raw_df_input = pd.read_csv(StringIO(paste_data), sep='\t')
                            except Exception as e:
                                st.error(f"Lỗi đọc dữ liệu paste: {e}")

            else:
                st.warning("Không tìm thấy tab 'Settings'")
                selected_project = "-- Chọn Dự Án --"
        else:
            st.info("Nhập URL Google Sheet")
            selected_project = "-- Chọn Dự Án --"
    else:
        st.markdown("""
        <div class="connection-status disconnected">
            ✗ Chưa kết nối Google Sheets
        </div>
        """, unsafe_allow_html=True)
        st.info("Cần cấu hình secrets.toml")
        selected_project = "-- Chọn Dự Án --"

# Main Content
if gc and spreadsheet_url and selected_project != "-- Chọn Dự Án --":
    master_df = load_master_from_sheet(gc, spreadsheet_url, selected_project)
    
    # Process Data if Input exists
    if raw_df_input is not None and not raw_df_input.empty:
        df, missing_keys, all_dates = process_ranking_data(raw_df_input, master_df)
        
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
                if pd.isna(curr) or pd.isna(prev): return 0
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
                    <span class="stat-badge">🎯 {top10_count} trong Top 10</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # === ACTION CENTER (KPI GAP FILLER) ===
            st.markdown("""
            <div class="section-header">
                <div class="icon">⚡</div>
                <h2>Action Center (Lấp đầy KPI)</h2>
            </div>
            """, unsafe_allow_html=True)
            
            gap_analysis = calculate_kpi_gap_actions(df_curr, kpi_settings)
            
            tab3, tab5, tab10, tab30 = st.tabs(["🎯 Top 3", "🎯 Top 5", "🎯 Top 10", "🎯 Top 30"])
            
            def render_gap_tab(kpi_lvl):
                info = gap_analysis.get(kpi_lvl)
                if not info: 
                    st.info("Chưa có cấu hình cho KPI này")
                    return
                
                if info['status'] == 'met':
                    st.markdown(f"""
                    <div class="alert-box success">
                        <div class="icon-wrapper">✓</div>
                        <div class="content">
                            <div class="title">Tuyệt vời! Đã đạt KPI Top {kpi_lvl}</div>
                            <div class="description">Hãy duy trì phong độ hiện tại.</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    gap = info['gap']
                    st.markdown(f"""
                    <div class="gap-card">
                        <div class="gap-stat">
                            <div class="gap-label">Mục tiêu còn thiếu</div>
                            <div class="gap-val" style="color:var(--danger);">{gap} Keywords</div>
                        </div>
                        <div style="margin-bottom:12px; font-weight:600; font-size:14px;">🏆 Top Topic "Cứu Tinh" (Striking Distance):</div>
                    """, unsafe_allow_html=True)
                    
                    topic_df = info['data']
                    if not topic_df.empty:
                        for idx, row in topic_df.iterrows():
                            fill_pct = row['Fill_Pct']
                            count = row['Striking_Count']
                            url_short = str(row['Best_URL'])[-40:] if len(str(row['Best_URL'])) > 40 else str(row['Best_URL'])
                            
                            st.markdown(f"""
                            <div class="topic-row">
                                <div class="topic-rank">{idx+1}</div>
                                <div class="topic-info">
                                    <div class="topic-name">{row['Topic']}</div>
                                    <div class="topic-desc">
                                        <span title="Best URL to push">🔗 ...{url_short}</span>
                                    </div>
                                </div>
                                <div class="topic-action" title="Số keyword ở ngưỡng cửa">
                                    +{count} KWs (Lấp {fill_pct:.0f}% Gap)
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.warning(f"Không tìm thấy từ khóa nào ở ngưỡng cửa (Striking Distance) để đẩy vào Top {kpi_lvl}.")
                    
                    st.markdown("</div>", unsafe_allow_html=True)

            with tab3: render_gap_tab(3)
            with tab5: render_gap_tab(5)
            with tab10: render_gap_tab(10)
            with tab30: render_gap_tab(30)


            # === KPI SECTION (Keep Existing) ===
            st.markdown("""
            <div class="section-header">
                <div class="icon">📊</div>
                <h2>Phân bổ & KPI</h2>
            </div>
            """, unsafe_allow_html=True)
            
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
                    compare_date_str = pd.to_datetime(compare_date).strftime('%d/%m/%Y')
                else:
                    compare_date = None
                    compare_date_str = None
                    st.info("Chỉ có 1 ngày dữ liệu")
                    
            with col_hist:
                show_history = st.checkbox("📈 Hiển thị lịch sử", value=False)
            
            comparison = calculate_comparison(df_history, curr_date, compare_date) if compare_date else {}
            
            limits = [3, 5, 10, 15, 30, 50, 100]
            cols = st.columns(4)
            
            for i, lim in enumerate(limits[:4]):
                with cols[i]:
                    cnt = len(df_curr[df_curr['Rank'].notna() & (df_curr['Rank'] <= lim)])
                    pct = (cnt / total_kw) * 100 if total_kw > 0 else 0
                    
                    comp_data = comparison.get(f'top{lim}', {})
                    comp_count = comp_data.get('compare', cnt)
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
                    
                    compare_text = f"vs {compare_date_str}: {delta:+d} ({delta_pct:+.1f}%)" if compare_date_str else ""
                    
                    target_html = ""
                    if lim in kpi_settings:
                        target_kw = int(total_kw * kpi_settings[lim] / 100)
                        gap_kw = cnt - target_kw
                        gap_pct = pct - kpi_settings[lim]
                        
                        if gap_pct >= 0:
                            target_html = f'<div class="target-status met">✓ Đạt +{gap_pct:.1f}% (+{gap_kw} KW)</div>'
                        else:
                            target_html = f'<div class="target-status miss">✗ Thiếu {abs(gap_pct):.1f}% ({gap_kw} KW)</div>'
                    
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
                    if lim in kpi_settings:
                        target_kw = int(total_kw * kpi_settings[lim] / 100)
                        gap_kw = cnt - target_kw
                        gap_pct = pct - kpi_settings[lim]
                        
                        if gap_pct >= 0:
                            target_html = f'<div class="target-status met">✓ Đạt +{gap_pct:.1f}% (+{gap_kw} KW)</div>'
                        else:
                            target_html = f'<div class="target-status miss">✗ Thiếu {abs(gap_pct):.1f}% ({gap_kw} KW)</div>'
                    
                    st.markdown(f"""
                    <div class="kpi-card {trend_class}">
                        <div class="label">Top {lim}</div>
                        <div class="value">{cnt}</div>
                        <div class="percentage">{pct:.1f}%</div>
                        {trend_html}
                        {target_html}
                    </div>
                    """, unsafe_allow_html=True)
            
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
                st.markdown("""
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
            st.markdown("""
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
            st.markdown("""
            <div class="section-header">
                <div class="icon">⚡</div>
                <h2>Workstation</h2>
            </div>
            """, unsafe_allow_html=True)
            
            ws_compare_options = get_available_compare_dates(all_dates, curr_date)
            
            if ws_compare_options:
                ws_col1, ws_col2 = st.columns([1, 3])
                with ws_col1:
                    ws_selected_compare = st.selectbox(
                        "📅 So sánh với:",
                        options=list(ws_compare_options.keys()),
                        index=0,
                        key="workstation_compare"
                    )
                    ws_compare_date = ws_compare_options[ws_selected_compare]
                    ws_compare_date_str = pd.to_datetime(ws_compare_date).strftime('%d/%m/%Y')
                
                ws_prev = df[df['Date'] == ws_compare_date][['Keyword_Join', 'Rank']].copy()
                ws_prev = ws_prev.rename(columns={'Rank': 'Rank_Prev_WS'})
                df_curr = df_curr.merge(ws_prev, on='Keyword_Join', how='left')
                
                def calc_change_ws(row):
                    curr = row['Rank']
                    prev = row['Rank_Prev_WS']
                    if pd.isna(curr) or pd.isna(prev):
                        return 0
                    return int(prev) - int(curr)
                
                df_curr['Change_WS'] = df_curr.apply(calc_change_ws, axis=1)
                
                df_curr['Trend_Info_WS'] = df_curr.apply(
                    lambda row: classify_trend_extended(row['Rank'], row['Rank_Prev_WS']), axis=1
                )
                df_curr['Trend_Label_WS'] = df_curr['Trend_Info_WS'].apply(lambda x: x['label'])
                df_curr['Trend_Type_WS'] = df_curr['Trend_Info_WS'].apply(lambda x: x['type'])
                df_curr['Trend_Severity_WS'] = df_curr['Trend_Info_WS'].apply(lambda x: x['severity'])
                
                curr_date_str = pd.to_datetime(curr_date).strftime('%d/%m/%Y')
                with ws_col2:
                    st.markdown(f"""
                    <div class="workstation-compare-badge" style="margin-top: 28px;">
                        📊 Đang xem: <strong>{curr_date_str}</strong> so với <strong>{ws_compare_date_str}</strong>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                df_curr['Change_WS'] = df_curr['Change']
                df_curr['Trend_Label_WS'] = df_curr['Trend_Label']
                df_curr['Trend_Type_WS'] = df_curr['Trend_Type']
                df_curr['Trend_Severity_WS'] = df_curr['Trend_Severity']
                st.info("Chỉ có 1 ngày dữ liệu")
            
            def analyze_issue(row):
                t = clean_url_for_compare(row['Target URL'])
                c = clean_url_for_compare(row['Actual_URL']) if pd.notna(row.get('Actual_URL')) else ""
                if t and c and (t not in c):
                    return "Cannibal"
                if not t:
                    return "Missing Target"
                return "OK"

            df_curr['Issue'] = df_curr.apply(analyze_issue, axis=1)
            
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
                v = v[v['Trend_Label_WS'] == sel_trend]
            
            if sel_issue != "All": 
                v = v[v['Issue'] == sel_issue]
            
            if search_txt:
                s = search_txt.lower()
                v = v[
                    v['Keyword'].str.lower().str.contains(s, na=False) | 
                    v['Actual_URL'].astype(str).str.lower().str.contains(s, na=False)
                ]

            v = v.sort_values(by=['Trend_Severity_WS', 'Rank'], ascending=[False, True])
            
            v['Rank_Display'] = v['Rank'].apply(lambda x: int(x) if pd.notna(x) else ">100")
            v['Change_Display'] = v['Change_WS'].apply(lambda x: f"{int(x):+d}" if x != 0 else "-")

            st.markdown(f"""
            <div class="data-table-header">
                <div class="title">🔍 Kết quả lọc <span class="count">{len(v)}</span></div>
            </div>
            """, unsafe_allow_html=True)

            st.dataframe(
                v[['Keyword', 'Topic', 'Rank_Display', 'Change_Display', 'Trend_Label_WS', 'Issue', 'Actual_URL', 'Target URL']].rename(columns={
                    'Rank_Display': 'Rank',
                    'Change_Display': 'Δ',
                    'Trend_Label_WS': 'Xu hướng'
                }), 
                use_container_width=True, 
                height=500,
                column_config={
                    "Actual_URL": st.column_config.LinkColumn("Actual URL"), 
                    "Target URL": st.column_config.LinkColumn("Target URL"),
                }
            )
            
            st.markdown(f"""
            <div class="stats-bar">
                <div class="stat-item">🚀 Tăng mạnh: <span class="value">{len(v[v['Trend_Type_WS']=='surge'])}</span></div>
                <div class="stat-item">↑ Tăng: <span class="value">{len(v[v['Trend_Type_WS']=='up'])}</span></div>
                <div class="stat-item">↓ Giảm: <span class="value">{len(v[v['Trend_Type_WS']=='down'])}</span></div>
                <div class="stat-item">🔥 Giảm mạnh: <span class="value">{len(v[v['Trend_Type_WS']=='crash'])}</span></div>
                <div class="stat-item">⚠ Rớt: <span class="value">{len(v[v['Trend_Type_WS']=='dropped'])}</span></div>
                <div class="stat-item">✦ Mới: <span class="value">{len(v[v['Trend_Type_WS']=='new'])}</span></div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 60px 20px; background: white; border-radius: 16px; margin-top: 20px; border-top: 4px solid #2563eb;">
            <div style="font-size: 48px; margin-bottom: 16px;">📤</div>
            <h3 style="color: #1e40af; margin-bottom: 8px;">Chưa có dữ liệu ranking</h3>
            <p style="color: #6b7280;">Vui lòng upload file ranking hoặc paste dữ liệu ở sidebar</p>
        </div>
        """, unsafe_allow_html=True)
else:
    # Welcome / Setup screen (Keep Existing)
    st.markdown("""
    <div style="text-align: center; padding: 40px 20px;">
        <div style="font-size: 64px; margin-bottom: 24px;">📊</div>
        <h1 style="font-size: 32px; font-weight: 700; color: #1e40af; margin-bottom: 12px;">
            SEO Command Center
        </h1>
        <p style="font-size: 16px; color: #6b7280; max-width: 500px; margin: 0 auto 32px auto;">
            Công cụ theo dõi và phân tích thứ hạng từ khóa SEO chuyên nghiệp
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="setup-card">
            <h3>📋 Bước 1: Tạo Google Sheet</h3>
            <ol>
                <li>Tạo Google Sheet mới</li>
                <li>Tạo tab <code>Settings</code> với các cột:
                    <br>• project_name
                    <br>• kpi_top3, kpi_top5, kpi_top10, kpi_top30
                </li>
                <li>Tạo tab <code>Master_[TenProject]</code> cho mỗi project với các cột:
                    <br>• Keyword
                    <br>• Topic  
                    <br>• Target URL
                </li>
                <li>Share sheet với Service Account email</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="setup-card">
            <h3>🔑 Bước 2: Cấu hình Secrets</h3>
            <ol>
                <li>Tạo Google Cloud Project</li>
                <li>Enable Google Sheets API</li>
                <li>Tạo Service Account & download JSON key</li>
                <li>Trong Streamlit Cloud, thêm vào Secrets:
                    <br><code>[gcp_service_account]</code>
                    <br><code>type = "service_account"</code>
                    <br><code>project_id = "..."</code>
                    <br><code>private_key = "..."</code>
                    <br><code>client_email = "..."</code>
                    <br>...
                </li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
