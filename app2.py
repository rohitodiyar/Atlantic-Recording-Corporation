import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
import itertools

# ==========================================
# 1. Page Configuration & Custom CSS Injection
# ==========================================
st.set_page_config(
    page_title="UK Top 50 Playlist Market Analysis", 
    page_icon="🎵", 
    layout="wide"
)

# Deep indigo/slate for maximum contrast against sky blue
TEXT_COLOR = "#0F172A"
ACCENT_COLOR = "#4338CA"
BG_COLOR = "#E0F2FE"

st.markdown(
    f"""
    <style>
    /* Force pointer cursor on all selection elements */
    div[data-baseweb="select"], div[data-baseweb="select"] * {{ cursor: pointer !important; }}
    
    /* Main Background - Soft Aesthetic Sky Blue */
    .stApp {{
        background-color: {BG_COLOR};
    }}
    
    /* Global Typography Contrast */
    h1, h2, h3, h4, p, label, .stMarkdown, .stText, .stSelectbox label, .stMultiSelect label {{
        color: {TEXT_COLOR} !important;
    }}
    
    /* FIX: Explicitly force full text visibility for Selected items inside inputs */
    div[data-baseweb="select"] div,
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] p,
    div[data-testid="stMarkdownContainer"] p {{
        color: {TEXT_COLOR} !important;
        font-weight: 600 !important;
    }}
    
    /* Dropdown options contrast alignment */
    ul[role="listbox"] li div {{
        color: {TEXT_COLOR} !important;
    }}

    /* Minimalist Geometric Input Component Box styling */
    div[data-baseweb="select"] > div {{
        background-color: #FFFFFF !important;
        border: 2px solid {TEXT_COLOR} !important;
        border-radius: 0px !important;
    }}
    
    /* Date Input Specific Overrides */
    div[data-baseweb="input"] > div {{
        background-color: #FFFFFF !important;
        border: 2px solid {TEXT_COLOR} !important;
        border-radius: 0px !important;
        color: {TEXT_COLOR} !important;
        font-weight: 600 !important;
    }}
    
    header {{ background: transparent !important; }}
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 2. Data Loading Pipeline
# ==========================================
@st.cache_data
def load_data():
    df = pd.read_csv('Atlantic_United_Kingdom.csv')
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
    df['artists_split'] = df['artist'].apply(lambda x: [a.strip() for a in x.split('&')])
    df['num_artists'] = df['artists_split'].apply(len)
    df['is_collab'] = df['num_artists'] > 1
    df['duration_mins'] = df['duration_ms'] / 60000
    return df

df = load_data()

# ==========================================
# 3. Title & Header Structure
# ==========================================
st.title("UK Top 50 Playlist Market Structure & Analysis")
st.markdown("Structural and cultural intelligence into the UK music market for Atlantic Recording Corporation.")
st.markdown("---")

# ==========================================
# 4. Accessible Main Screen Filter Control Panel
# ==========================================
st.subheader("📊 Dashboard Control Panel")
filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

with filter_col1:
    min_date, max_date = df['date'].min().date(), df['date'].max().date()
    date_range = st.date_input("Date Range Selector", value=(min_date, max_date), min_value=min_date, max_value=max_date)

with filter_col2:
    collab_toggle = st.selectbox("Solo vs Collaboration", ["All Tracks", "Solo Tracks Only", "Collaborations Only"])

with filter_col3:
    album_types = df['album_type'].unique().tolist()
    selected_albums = st.multiselect("Album Type Filter", options=album_types, default=album_types)

# Apply Primary Filter Steps Sequentially
if len(date_range) == 2:
    start_date, end_date = date_range
    mask = (df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)
    filtered_df = df.loc[mask]
else:
    filtered_df = df.copy()

if collab_toggle == "Solo Tracks Only":
    filtered_df = filtered_df[~filtered_df['is_collab']]
elif collab_toggle == "Collaborations Only":
    filtered_df = filtered_df[filtered_df['is_collab']]

filtered_df = filtered_df[filtered_df['album_type'].isin(selected_albums)]

with filter_col4:
    all_artists = sorted(list(set([a for sublist in filtered_df['artists_split'] for a in sublist])))
    selected_artist = st.selectbox("Artist Filter", ["All Artists"] + all_artists)

if selected_artist != "All Artists":
    filtered_df = filtered_df[filtered_df['artists_split'].apply(lambda x: selected_artist in x)]

st.markdown("---")

# ==========================================
# 5. Core KPI Cards (Full Text Wrap Enabled)
# ==========================================
if not filtered_df.empty:
    total_unique_artists = len(set([a for sublist in filtered_df['artists_split'] for a in sublist]))
    collab_ratio = filtered_df['num_artists'].mean()
    explicit_share = (filtered_df['is_explicit'].sum() / len(filtered_df)) * 100
    
    artist_counts = pd.Series([a for sublist in filtered_df['artists_split'] for a in sublist]).value_counts()
    top_5_share = (artist_counts.head(5).sum() / len(filtered_df)) * 100 if len(filtered_df) > 0 else 0

    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    # Minimalist Geometric KPI Cards
    card_style = f"background-color: #FFFFFF; border: 2px solid {TEXT_COLOR}; padding: 1.2rem; box-shadow: 4px 4px 0px {TEXT_COLOR}; min-height: 130px; display: flex; flex-direction: column; justify-content: center;"
    label_style = f"color: {TEXT_COLOR}; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; word-wrap: break-word; white-space: normal; line-height: 1.4; margin-bottom: 0.5rem;"
    value_style = f"color: {ACCENT_COLOR}; font-size: 2rem; font-weight: 900; line-height: 1;"

    with kpi_col1:
        st.markdown(f"""
        <div style="{card_style}">
            <div style="{label_style}">Unique Artist Count</div>
            <div style="{value_style}">{total_unique_artists}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_col2:
        st.markdown(f"""
        <div style="{card_style}">
            <div style="{label_style}">Artist Concentration Index</div>
            <div style="{value_style}">{top_5_share:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_col3:
        st.markdown(f"""
        <div style="{card_style}">
            <div style="{label_style}">Collaboration Ratio</div>
            <div style="{value_style}">{collab_ratio:.2f} avg</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_col4:
        st.markdown(f"""
        <div style="{card_style}">
            <div style="{label_style}">Explicit Content Share</div>
            <div style="{value_style}">{explicit_share:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # FIX: Set the plot font color to a highly visible dark shade
    transparent_layout = dict(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=TEXT_COLOR, size=13, family="Arial, sans-serif")
    )

    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        st.subheader("Artist Dominance Leaderboard")
        top_10_artists = artist_counts.head(10).reset_index()
        top_10_artists.columns = ['Artist', 'Appearances']
        fig_artist = px.bar(
            top_10_artists, x='Appearances', y='Artist', orientation='h', 
            color_discrete_sequence=[ACCENT_COLOR]
        )
        fig_artist.update_layout(yaxis={'categoryorder':'total ascending'}, **transparent_layout)
        st.plotly_chart(fig_artist, use_container_width=True)

    with row1_col2:
        st.subheader("Content Explicitness Analysis")
        explicit_counts = filtered_df['is_explicit'].value_counts().reset_index()
        explicit_counts.columns = ['Is Explicit', 'Count']
        explicit_counts['Is Explicit'] = explicit_counts['Is Explicit'].map({True: 'Explicit', False: 'Clean'})
        fig_explicit = px.pie(
            explicit_counts, values='Count', names='Is Explicit', color='Is Explicit', 
            color_discrete_map={'Clean': '#10B981', 'Explicit': '#E11D48'}, hole=0.4
        )
        fig_explicit.update_layout(**transparent_layout)
        st.plotly_chart(fig_explicit, use_container_width=True)

    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        st.subheader("Release Strategy: Format Dominance")
        album_counts = filtered_df['album_type'].value_counts().reset_index()
        album_counts.columns = ['Album Type', 'Count']
        fig_album = px.pie(
            album_counts, values='Count', names='Album Type', 
            color_discrete_sequence=[ACCENT_COLOR, "#0EA5E9", "#F59E0B"]
        )
        fig_album.update_layout(**transparent_layout)
        st.plotly_chart(fig_album, use_container_width=True)

    with row2_col2:
        st.subheader("Track Duration Distribution")
        fig_duration = px.histogram(
            filtered_df, x='duration_mins', nbins=30, 
            color_discrete_sequence=[ACCENT_COLOR], labels={'duration_mins': 'Duration (Minutes)'}
        )
        fig_duration.update_layout(**transparent_layout)
        st.plotly_chart(fig_duration, use_container_width=True)

    # ==========================================
    # 6. Structurally Spaced Collaboration Network
    # ==========================================
    st.markdown("---")
    st.subheader("Collaboration Network Visualization")
    st.markdown("Structural map showing partnerships among top collaborating artists. Spaced using a structured circular framework to guarantee clear label readability without hovering.")
    
    edges = []
    for artists in filtered_df['artists_split']:
        if len(artists) > 1:
            edges.extend(itertools.combinations(artists, 2))
            
    if edges:
        G = nx.Graph()
        G.add_edges_from(edges)
        
        degree_freq = sorted(G.degree, key=lambda x: x[1], reverse=True)
        # Limit to top 25 nodes to ensure absolutely zero visual crowding
        top_nodes = [n for n, d in degree_freq[:25]]
        G_sub = G.subgraph(top_nodes)
        
        # Clean geometric circular spacing structure to isolate strings perfectly
        pos = nx.circular_layout(G_sub)
        
        edge_x, edge_y = [], []
        for edge in G_sub.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1.5, color='#94A3B8'),
            hoverinfo='none',
            mode='lines'
        )
        
        node_x, node_y, node_text = [], [], []
        for node in G_sub.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)
            
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text', 
            text=node_text,
            textposition='top center',
            textfont={
                'size': 13,
                'color': TEXT_COLOR,
                'family': 'Arial, sans-serif'
            },
            hoverinfo='text',
            marker=dict(
                symbol='square',
                size=18,
                color='#FFFFFF',
                line=dict(color=ACCENT_COLOR, width=3)
            )
        )
        
        fig_network = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                showlegend=False,
                height=850, 
                margin=dict(b=40, l=40, r=40, t=40),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
             )
        )
        st.plotly_chart(fig_network, use_container_width=True)
    else:
        st.info("No collaboration data available for the current filter selection.")

else:
    st.warning("No data available for the selected filters. Please adjust your criteria.")