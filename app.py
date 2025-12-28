"""
SEO Command Center v2.0 - Google Sheets Integration
Streamlit App với Google Sheets làm database cho Master Data
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import io

# Google Sheets imports
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="SEO Command Center",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    /* Main container */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.2rem;
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        margin-bottom: 1rem;
    }
    
    .metric-card.green {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        box-shadow: 0 4px 15px rgba(17, 153, 142, 0.3);
    }
    
    .metric-card.orange {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        box-shadow: 0 4px 15px rgba(245, 87, 108, 0.3);
    }
    
    .metric-card.blue {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3);
    }
    
    .metric-title {
        font-size: 0.85rem;
        opacity: 0.9;
        margin-bottom: 0.3rem;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    .metric-delta {
        font-size: 0.8rem;
        margin-top: 0.3rem;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .status-top3 { background: #d4edda; color: #155724; }
    .status-top10 { background: #cce5ff; color: #004085; }
    .status-top20 { background: #fff3cd; color: #856404; }
    .status-below { background: #f8d7da; color: #721c24; }
    
    /* Progress bar */
    .progress-container {
        background: #e9ecef;
        border-radius: 10px;
        overflow: hidden;
        height: 24px;
        margin: 0.5rem 0;
    }
    
    .progress-bar {
        height: 100%;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
        font-size: 0.8rem;
        transition: width 0.5s ease;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        padding-top: 1rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Table styling */
    .dataframe {
        font-size: 0.85rem !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


# ==================== GOOGLE SHEETS FUNCTIONS ====================

def init_google_sheets():
    """Khởi tạo kết nối Google Sheets từ Streamlit secrets"""
    if not GSPREAD_AVAILABLE:
        return None, "Thư viện gspread chưa được cài đặt"
    
    try:
        # Đọc credentials từ Streamlit secrets
        if "gcp_service_account" not in st.secrets:
            return None, "Chưa cấu hình Google Sheets credentials trong Streamlit secrets"
        
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        )
        client = gspread.authorize(credentials)
        return client, None
    except Exception as e:
        return None, f"Lỗi kết nối: {str(e)}"


def get_projects_from_sheets(client, spreadsheet_url):
    """Lấy danh sách projects từ Google Sheets"""
    try:
        spreadsheet = client.open_by_url(spreadsheet_url)
        # Đọc sheet "Settings" để lấy danh sách projects
        try:
            settings_sheet = spreadsheet.worksheet("Settings")
            projects = settings_sheet.col_values(1)[1:]  # Bỏ header
            return [p for p in projects if p.strip()], None
        except gspread.exceptions.WorksheetNotFound:
            # Nếu không có Settings sheet, lấy từ tên các worksheet
            worksheets = spreadsheet.worksheets()
            projects = [ws.title for ws in worksheets if ws.title.startswith("Master_")]
            projects = [p.replace("Master_", "") for p in projects]
            return projects, None
    except Exception as e:
        return [], f"Lỗi đọc projects: {str(e)}"


def get_master_data_from_sheets(client, spreadsheet_url, project_name):
    """Lấy master data của một project từ Google Sheets"""
    try:
        spreadsheet = client.open_by_url(spreadsheet_url)
        worksheet = spreadsheet.worksheet(f"Master_{project_name}")
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        return df, None
    except gspread.exceptions.WorksheetNotFound:
        return None, f"Không tìm thấy sheet Master_{project_name}"
    except Exception as e:
        return None, f"Lỗi đọc master data: {str(e)}"


def save_master_data_to_sheets(client, spreadsheet_url, project_name, df):
    """Lưu master data lên Google Sheets"""
    try:
        spreadsheet = client.open_by_url(spreadsheet_url)
        
        # Tạo hoặc lấy worksheet
        try:
            worksheet = spreadsheet.worksheet(f"Master_{project_name}")
            worksheet.clear()
        except gspread.exceptions.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(
                title=f"Master_{project_name}",
                rows=len(df) + 100,
                cols=len(df.columns) + 5
            )
        
        # Cập nhật data
        worksheet.update([df.columns.tolist()] + df.values.tolist())
        
        # Cập nhật Settings sheet
        update_settings_sheet(client, spreadsheet_url, project_name)
        
        return True, None
    except Exception as e:
        return False, f"Lỗi lưu data: {str(e)}"


def update_settings_sheet(client, spreadsheet_url, project_name):
    """Cập nhật Settings sheet với project mới"""
    try:
        spreadsheet = client.open_by_url(spreadsheet_url)
        
        try:
            settings_sheet = spreadsheet.worksheet("Settings")
        except gspread.exceptions.WorksheetNotFound:
            settings_sheet = spreadsheet.add_worksheet(title="Settings", rows=100, cols=10)
            settings_sheet.update_cell(1, 1, "Project Name")
            settings_sheet.update_cell(1, 2, "Created Date")
        
        # Kiểm tra project đã tồn tại chưa
        existing_projects = settings_sheet.col_values(1)[1:]
        if project_name not in existing_projects:
            next_row = len(existing_projects) + 2
            settings_sheet.update_cell(next_row, 1, project_name)
            settings_sheet.update_cell(next_row, 2, datetime.now().strftime("%Y-%m-%d"))
        
        return True
    except Exception as e:
        return False


# ==================== DATA PROCESSING FUNCTIONS ====================

def process_ranking_data(ranking_df, master_df):
    """Xử lý và merge ranking data với master data"""
    
    # Chuẩn hóa tên cột
    ranking_df.columns = ranking_df.columns.str.strip().str.lower()
    master_df.columns = master_df.columns.str.strip().str.lower()
    
    # Tìm cột keyword
    keyword_cols = ['keyword', 'keywords', 'từ khóa', 'tu khoa', 'query']
    ranking_kw_col = None
    master_kw_col = None
    
    for col in keyword_cols:
        if col in ranking_df.columns:
            ranking_kw_col = col
            break
    
    for col in keyword_cols:
        if col in master_df.columns:
            master_kw_col = col
            break
    
    if not ranking_kw_col or not master_kw_col:
        return None, "Không tìm thấy cột Keyword trong file"
    
    # Tìm cột ranking
    rank_cols = ['rank', 'position', 'ranking', 'vị trí', 'vi tri', 'pos']
    rank_col = None
    for col in rank_cols:
        if col in ranking_df.columns:
            rank_col = col
            break
    
    if not rank_col:
        return None, "Không tìm thấy cột Rank/Position trong file ranking"
    
    # Chuẩn hóa keyword để merge
    ranking_df['keyword_clean'] = ranking_df[ranking_kw_col].astype(str).str.strip().str.lower()
    master_df['keyword_clean'] = master_df[master_kw_col].astype(str).str.strip().str.lower()
    
    # Merge data
    merged = pd.merge(
        master_df,
        ranking_df[[ranking_kw_col, rank_col, 'keyword_clean']],
        on='keyword_clean',
        how='left',
        suffixes=('', '_ranking')
    )
    
    # Rename và clean columns
    merged = merged.rename(columns={rank_col: 'current_rank'})
    merged['current_rank'] = pd.to_numeric(merged['current_rank'], errors='coerce')
    
    # Tìm cột target
    target_cols = ['target', 'target_rank', 'mục tiêu', 'muc tieu', 'target rank']
    target_col = None
    for col in target_cols:
        if col in merged.columns:
            target_col = col
            break
    
    if target_col:
        merged['target_rank'] = pd.to_numeric(merged[target_col], errors='coerce').fillna(10)
    else:
        merged['target_rank'] = 10
    
    # Tìm cột topic
    topic_cols = ['topic', 'chủ đề', 'chu de', 'category', 'nhóm', 'nhom', 'group']
    topic_col = None
    for col in topic_cols:
        if col in merged.columns:
            topic_col = col
            break
    
    if topic_col:
        merged['topic'] = merged[topic_col].fillna('Uncategorized')
    else:
        merged['topic'] = 'Uncategorized'
    
    # Tạo các cột phân tích
    merged['status'] = merged['current_rank'].apply(classify_rank)
    merged['on_target'] = merged['current_rank'] <= merged['target_rank']
    merged['gap'] = merged['current_rank'] - merged['target_rank']
    
    # Clean up
    merged = merged.drop(columns=['keyword_clean'], errors='ignore')
    
    return merged, None


def classify_rank(rank):
    """Phân loại rank thành các nhóm"""
    if pd.isna(rank) or rank == 0:
        return 'Not Ranked'
    elif rank <= 3:
        return 'Top 3'
    elif rank <= 10:
        return 'Top 10'
    elif rank <= 20:
        return 'Top 20'
    elif rank <= 50:
        return 'Top 50'
    else:
        return 'Below 50'


def calculate_metrics(df):
    """Tính toán các metrics chính"""
    total_keywords = len(df)
    ranked_keywords = df['current_rank'].notna().sum()
    
    metrics = {
        'total_keywords': total_keywords,
        'ranked_keywords': ranked_keywords,
        'not_ranked': total_keywords - ranked_keywords,
        'top_3': (df['current_rank'] <= 3).sum(),
        'top_10': (df['current_rank'] <= 10).sum(),
        'top_20': (df['current_rank'] <= 20).sum(),
        'on_target': df['on_target'].sum() if 'on_target' in df.columns else 0,
        'avg_rank': df['current_rank'].mean(),
        'median_rank': df['current_rank'].median(),
    }
    
    # Tính % đạt target
    metrics['target_rate'] = (metrics['on_target'] / total_keywords * 100) if total_keywords > 0 else 0
    metrics['top_10_rate'] = (metrics['top_10'] / total_keywords * 100) if total_keywords > 0 else 0
    
    return metrics


# ==================== VISUALIZATION FUNCTIONS ====================

def create_status_distribution_chart(df):
    """Tạo biểu đồ phân bố ranking status"""
    status_counts = df['status'].value_counts()
    
    colors = {
        'Top 3': '#10b981',
        'Top 10': '#3b82f6',
        'Top 20': '#f59e0b',
        'Top 50': '#f97316',
        'Below 50': '#ef4444',
        'Not Ranked': '#6b7280'
    }
    
    fig = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        color=status_counts.index,
        color_discrete_map=colors,
        hole=0.4
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2),
        margin=dict(t=20, b=20, l=20, r=20),
        height=350
    )
    
    return fig


def create_topic_performance_chart(df):
    """Tạo biểu đồ performance theo topic"""
    if 'topic' not in df.columns:
        return None
    
    topic_stats = df.groupby('topic').agg({
        'current_rank': ['mean', 'count'],
        'on_target': 'sum'
    }).round(1)
    
    topic_stats.columns = ['avg_rank', 'total', 'on_target']
    topic_stats['target_rate'] = (topic_stats['on_target'] / topic_stats['total'] * 100).round(1)
    topic_stats = topic_stats.reset_index()
    
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "bar"}, {"type": "bar"}]],
        subplot_titles=("Avg Rank by Topic", "Target Achievement Rate")
    )
    
    # Avg Rank chart
    fig.add_trace(
        go.Bar(
            x=topic_stats['topic'],
            y=topic_stats['avg_rank'],
            marker_color='#6366f1',
            name='Avg Rank'
        ),
        row=1, col=1
    )
    
    # Target Rate chart
    fig.add_trace(
        go.Bar(
            x=topic_stats['topic'],
            y=topic_stats['target_rate'],
            marker_color='#10b981',
            name='Target Rate %'
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        showlegend=False,
        height=350,
        margin=dict(t=40, b=20, l=20, r=20)
    )
    
    return fig


def create_rank_distribution_chart(df):
    """Tạo biểu đồ phân bố ranking"""
    ranked_df = df[df['current_rank'].notna() & (df['current_rank'] > 0)]
    
    fig = px.histogram(
        ranked_df,
        x='current_rank',
        nbins=20,
        color_discrete_sequence=['#6366f1']
    )
    
    fig.update_layout(
        xaxis_title="Ranking Position",
        yaxis_title="Number of Keywords",
        showlegend=False,
        height=300,
        margin=dict(t=20, b=40, l=40, r=20)
    )
    
    return fig


def create_gap_analysis_chart(df):
    """Tạo biểu đồ phân tích gap vs target"""
    gap_df = df[df['current_rank'].notna()].copy()
    gap_df['gap_category'] = pd.cut(
        gap_df['gap'],
        bins=[-float('inf'), -10, -5, 0, 5, 10, float('inf')],
        labels=['Vượt >10', 'Vượt 5-10', 'Đạt target', 'Thiếu <5', 'Thiếu 5-10', 'Thiếu >10']
    )
    
    gap_counts = gap_df['gap_category'].value_counts()
    
    colors = ['#10b981', '#34d399', '#6ee7b7', '#fcd34d', '#f97316', '#ef4444']
    
    fig = px.bar(
        x=gap_counts.index,
        y=gap_counts.values,
        color=gap_counts.index,
        color_discrete_sequence=colors
    )
    
    fig.update_layout(
        xaxis_title="Gap Category",
        yaxis_title="Number of Keywords",
        showlegend=False,
        height=300,
        margin=dict(t=20, b=40, l=40, r=20)
    )
    
    return fig


# ==================== UI COMPONENTS ====================

def render_metric_card(title, value, delta=None, color="purple"):
    """Render một metric card"""
    color_class = {
        "purple": "",
        "green": "green",
        "orange": "orange",
        "blue": "blue"
    }.get(color, "")
    
    delta_html = f'<div class="metric-delta">{delta}</div>' if delta else ''
    
    st.markdown(f"""
    <div class="metric-card {color_class}">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def render_progress_bar(value, max_value=100, label=""):
    """Render progress bar với label"""
    percentage = min(value / max_value * 100, 100) if max_value > 0 else 0
    
    if percentage >= 80:
        color = "#10b981"
    elif percentage >= 60:
        color = "#3b82f6"
    elif percentage >= 40:
        color = "#f59e0b"
    else:
        color = "#ef4444"
    
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-bar" style="width: {percentage}%; background: {color};">
            {label if label else f'{percentage:.1f}%'}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_status_badge(status):
    """Render status badge"""
    badge_class = {
        'Top 3': 'status-top3',
        'Top 10': 'status-top10',
        'Top 20': 'status-top20',
        'Top 50': 'status-below',
        'Below 50': 'status-below',
        'Not Ranked': 'status-below'
    }.get(status, 'status-below')
    
    return f'<span class="status-badge {badge_class}">{status}</span>'


# ==================== MAIN APP ====================

def main():
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h1 style="color: #6366f1; margin-bottom: 0.5rem;">🎯 SEO Command Center</h1>
        <p style="color: #6b7280;">Keyword Ranking Analysis Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Cấu hình")
        
        # Data source selection
        data_source = st.radio(
            "Nguồn dữ liệu Master:",
            ["📤 Upload File", "📊 Google Sheets"],
            index=0
        )
        
        st.markdown("---")
        
        # Variables để lưu data
        master_df = None
        ranking_df = None
        project_name = "Default"
        
        if data_source == "📊 Google Sheets":
            st.markdown("#### Google Sheets Setup")
            
            # Check if gspread is available
            if not GSPREAD_AVAILABLE:
                st.warning("⚠️ Cần cài đặt gspread. Thêm vào requirements.txt")
                st.code("gspread\ngoogle-auth")
            else:
                # Check credentials
                if "gcp_service_account" not in st.secrets:
                    st.warning("⚠️ Chưa cấu hình credentials")
                    
                    with st.expander("📖 Hướng dẫn setup"):
                        st.markdown("""
                        **Bước 1:** Tạo Google Cloud Project
                        1. Vào [console.cloud.google.com](https://console.cloud.google.com)
                        2. Tạo project mới
                        3. Enable Google Sheets API
                        
                        **Bước 2:** Tạo Service Account
                        1. Vào IAM & Admin → Service Accounts
                        2. Create Service Account
                        3. Download JSON key
                        
                        **Bước 3:** Cấu hình Streamlit
                        1. Vào App Settings trên Streamlit Cloud
                        2. Thêm secret với format:
                        ```toml
                        [gcp_service_account]
                        type = "service_account"
                        project_id = "your-project"
                        private_key_id = "..."
                        private_key = "-----BEGIN PRIVATE KEY-----..."
                        client_email = "...@...iam.gserviceaccount.com"
                        ...
                        ```
                        
                        **Bước 4:** Share Spreadsheet
                        - Share với email của Service Account
                        """)
                else:
                    # Connect to Google Sheets
                    client, error = init_google_sheets()
                    
                    if error:
                        st.error(f"❌ {error}")
                    else:
                        st.success("✅ Đã kết nối Google Sheets")
                        
                        spreadsheet_url = st.text_input(
                            "URL Spreadsheet:",
                            placeholder="https://docs.google.com/spreadsheets/d/..."
                        )
                        
                        if spreadsheet_url:
                            projects, error = get_projects_from_sheets(client, spreadsheet_url)
                            
                            if error:
                                st.error(f"❌ {error}")
                            elif projects:
                                project_name = st.selectbox(
                                    "Chọn Project:",
                                    projects
                                )
                                
                                if st.button("📥 Load Master Data"):
                                    master_df, error = get_master_data_from_sheets(
                                        client, spreadsheet_url, project_name
                                    )
                                    if error:
                                        st.error(f"❌ {error}")
                                    else:
                                        st.session_state['master_df'] = master_df
                                        st.session_state['project_name'] = project_name
                                        st.success(f"✅ Đã load {len(master_df)} keywords")
                            else:
                                st.info("Chưa có project nào. Upload master file để tạo mới.")
                        
                        # Option to create new project
                        with st.expander("➕ Tạo Project mới"):
                            new_project = st.text_input("Tên project mới:")
                            new_master_file = st.file_uploader(
                                "Upload Master Excel:",
                                type=['xlsx', 'xls', 'csv'],
                                key="new_master"
                            )
                            
                            if new_project and new_master_file and st.button("Tạo Project"):
                                try:
                                    if new_master_file.name.endswith('.csv'):
                                        new_master_df = pd.read_csv(new_master_file)
                                    else:
                                        new_master_df = pd.read_excel(new_master_file)
                                    
                                    success, error = save_master_data_to_sheets(
                                        client, spreadsheet_url, new_project, new_master_df
                                    )
                                    
                                    if success:
                                        st.success(f"✅ Đã tạo project {new_project}")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {error}")
                                except Exception as e:
                                    st.error(f"❌ Lỗi: {str(e)}")
        
        else:  # Upload File mode
            st.markdown("#### Upload Files")
            
            master_file = st.file_uploader(
                "📋 Master File (Keywords + Topics):",
                type=['xlsx', 'xls', 'csv'],
                key="master"
            )
            
            if master_file:
                try:
                    if master_file.name.endswith('.csv'):
                        master_df = pd.read_csv(master_file)
                    else:
                        master_df = pd.read_excel(master_file)
                    st.success(f"✅ {len(master_df)} keywords loaded")
                    st.session_state['master_df'] = master_df
                except Exception as e:
                    st.error(f"❌ Lỗi đọc file: {str(e)}")
        
        st.markdown("---")
        
        # Ranking file upload (common for both modes)
        st.markdown("#### 📊 Ranking Data")
        ranking_file = st.file_uploader(
            "Upload Ranking File:",
            type=['xlsx', 'xls', 'csv'],
            key="ranking"
        )
        
        if ranking_file:
            try:
                if ranking_file.name.endswith('.csv'):
                    ranking_df = pd.read_csv(ranking_file)
                else:
                    ranking_df = pd.read_excel(ranking_file)
                st.success(f"✅ {len(ranking_df)} rows loaded")
                st.session_state['ranking_df'] = ranking_df
            except Exception as e:
                st.error(f"❌ Lỗi đọc file: {str(e)}")
        
        # Process button
        st.markdown("---")
        if st.button("🚀 Phân tích", use_container_width=True, type="primary"):
            master_df = st.session_state.get('master_df')
            ranking_df = st.session_state.get('ranking_df')
            
            if master_df is None:
                st.error("❌ Chưa có Master data")
            elif ranking_df is None:
                st.error("❌ Chưa upload Ranking file")
            else:
                with st.spinner("Đang xử lý..."):
                    result_df, error = process_ranking_data(ranking_df, master_df)
                    
                    if error:
                        st.error(f"❌ {error}")
                    else:
                        st.session_state['result_df'] = result_df
                        st.session_state['metrics'] = calculate_metrics(result_df)
                        st.success("✅ Phân tích hoàn tất!")
    
    # Main content
    result_df = st.session_state.get('result_df')
    metrics = st.session_state.get('metrics')
    
    if result_df is not None and metrics is not None:
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            render_metric_card(
                "Total Keywords",
                f"{metrics['total_keywords']:,}",
                f"Ranked: {metrics['ranked_keywords']:,}",
                "purple"
            )
        
        with col2:
            render_metric_card(
                "Top 10 Rate",
                f"{metrics['top_10_rate']:.1f}%",
                f"{metrics['top_10']:,} keywords",
                "green"
            )
        
        with col3:
            render_metric_card(
                "Target Achievement",
                f"{metrics['target_rate']:.1f}%",
                f"{metrics['on_target']:,} on target",
                "blue"
            )
        
        with col4:
            render_metric_card(
                "Avg Rank",
                f"{metrics['avg_rank']:.1f}",
                f"Median: {metrics['median_rank']:.0f}",
                "orange"
            )
        
        st.markdown("---")
        
        # Charts
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Overview",
            "📈 By Topic",
            "🔍 Keyword Details",
            "📥 Export"
        ])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### Ranking Distribution")
                fig = create_status_distribution_chart(result_df)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("##### Rank Position Histogram")
                fig = create_rank_distribution_chart(result_df)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("##### Gap Analysis (vs Target)")
            fig = create_gap_analysis_chart(result_df)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            if 'topic' in result_df.columns:
                fig = create_topic_performance_chart(result_df)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                
                # Topic breakdown table
                st.markdown("##### Topic Summary")
                topic_summary = result_df.groupby('topic').agg({
                    'current_rank': ['count', 'mean'],
                    'on_target': 'sum'
                }).round(1)
                topic_summary.columns = ['Total KWs', 'Avg Rank', 'On Target']
                topic_summary['Target Rate'] = (topic_summary['On Target'] / topic_summary['Total KWs'] * 100).round(1)
                topic_summary = topic_summary.sort_values('Target Rate', ascending=False)
                
                st.dataframe(topic_summary, use_container_width=True)
            else:
                st.info("Không có dữ liệu Topic trong file master")
        
        with tab3:
            # Filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                status_filter = st.multiselect(
                    "Status:",
                    result_df['status'].unique(),
                    default=result_df['status'].unique()
                )
            
            with col2:
                if 'topic' in result_df.columns:
                    topic_filter = st.multiselect(
                        "Topic:",
                        result_df['topic'].unique(),
                        default=result_df['topic'].unique()
                    )
                else:
                    topic_filter = None
            
            with col3:
                target_filter = st.radio(
                    "Target Status:",
                    ["All", "On Target", "Off Target"],
                    horizontal=True
                )
            
            # Apply filters
            filtered_df = result_df[result_df['status'].isin(status_filter)]
            
            if topic_filter is not None:
                filtered_df = filtered_df[filtered_df['topic'].isin(topic_filter)]
            
            if target_filter == "On Target":
                filtered_df = filtered_df[filtered_df['on_target'] == True]
            elif target_filter == "Off Target":
                filtered_df = filtered_df[filtered_df['on_target'] == False]
            
            st.markdown(f"##### Showing {len(filtered_df):,} keywords")
            
            # Display table
            display_cols = ['keyword', 'topic', 'current_rank', 'target_rank', 'gap', 'status', 'on_target']
            display_cols = [c for c in display_cols if c in filtered_df.columns]
            
            # Find keyword column
            keyword_col = None
            for col in ['keyword', 'keywords', 'từ khóa', 'tu khoa', 'query']:
                if col in filtered_df.columns:
                    keyword_col = col
                    break
            
            if keyword_col and keyword_col != 'keyword':
                filtered_df = filtered_df.rename(columns={keyword_col: 'keyword'})
            
            st.dataframe(
                filtered_df[display_cols].sort_values('current_rank'),
                use_container_width=True,
                height=500
            )
        
        with tab4:
            st.markdown("##### Export Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Export full report
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    result_df.to_excel(writer, sheet_name='Full Report', index=False)
                    
                    # Summary sheet
                    summary_data = {
                        'Metric': ['Total Keywords', 'Ranked', 'Top 3', 'Top 10', 'Top 20', 'On Target', 'Avg Rank'],
                        'Value': [
                            metrics['total_keywords'],
                            metrics['ranked_keywords'],
                            metrics['top_3'],
                            metrics['top_10'],
                            metrics['top_20'],
                            metrics['on_target'],
                            round(metrics['avg_rank'], 1)
                        ]
                    }
                    pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
                
                output.seek(0)
                
                st.download_button(
                    label="📥 Download Full Report (Excel)",
                    data=output,
                    file_name=f"seo_report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            with col2:
                # Export CSV
                csv = result_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"seo_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                )
    
    else:
        # Welcome screen
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background: #f8fafc; border-radius: 12px; margin: 2rem 0;">
            <h2 style="color: #6366f1;">👋 Chào mừng đến SEO Command Center</h2>
            <p style="color: #64748b; font-size: 1.1rem;">
                Công cụ phân tích keyword ranking toàn diện
            </p>
            <br>
            <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
                <div style="text-align: left; max-width: 250px;">
                    <h4>📋 Bước 1</h4>
                    <p>Upload Master File hoặc kết nối Google Sheets</p>
                </div>
                <div style="text-align: left; max-width: 250px;">
                    <h4>📊 Bước 2</h4>
                    <p>Upload Ranking File từ tool tracking</p>
                </div>
                <div style="text-align: left; max-width: 250px;">
                    <h4>🚀 Bước 3</h4>
                    <p>Click "Phân tích" và xem kết quả</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Sample data format
        with st.expander("📖 Xem format file mẫu"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Master File Format:**")
                sample_master = pd.DataFrame({
                    'Keyword': ['seo là gì', 'học seo', 'công cụ seo'],
                    'Topic': ['Cơ bản', 'Học tập', 'Tools'],
                    'Target': [10, 5, 10]
                })
                st.dataframe(sample_master)
            
            with col2:
                st.markdown("**Ranking File Format:**")
                sample_ranking = pd.DataFrame({
                    'Keyword': ['seo là gì', 'học seo', 'công cụ seo'],
                    'Rank': [5, 12, 8]
                })
                st.dataframe(sample_ranking)


if __name__ == "__main__":
    main()
