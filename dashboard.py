import streamlit as st
import pandas as pd
import plotly.express as px
from runner import get_candidate_odds  # Assuming runner.py is in the same directory

# Fetch the data
df = get_candidate_odds()

# Enhance with custom CSS for a more beautiful, modern look
st.markdown("""
    <style>
    .stApp {
        background-color: #1E1E1E;  /* Dark background */
        color: white;
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #2D2D2D;
    }
    .stTabs [data-baseweb="tab"] {
        color: white;
        background-color: #3D3D3D;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4D4D4D;
    }
    h1, h2, h3 {
        color: #00BFFF;  /* Tech blue accent */
    }
    .metric-card {
        background-color: #2D2D2D;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# Dashboard Title with icon
st.title(":chart_with_upwards_trend: PolyElection Dashboard: 2028 Presidential Odds")
st.subheader("Powered by Polymarket API :rocket:")

# Key Metrics at the top for visual appeal
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="metric-card"><h3>Top Dem Odds</h3><p>' + str(df['Dem Primary %'].max()) + '%</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-card"><h3>Top GOP Odds</h3><p>' + str(df['GOP Primary %'].max()) + '%</p></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="metric-card"><h3>Top President Odds</h3><p>' + str(df['President %'].max()) + '%</p></div>', unsafe_allow_html=True)

# Modern layout with tabs for different views
tab1, tab2, tab3 = st.tabs(["Overview Table", "Top Democrats", "Top Republicans"])

with tab1:
    st.write("Full Candidate Odds (Sorted by Presidency Probability)")
    # Interactive table
    st.dataframe(df.style.background_gradient(cmap='viridis', subset=['President %']))

with tab2:
    st.write(":blue_book: Top Democratic Candidates")
    dem_df = df[df['party'] == 'DEM'].head(10)  # Top 10
    fig_dem = px.bar(dem_df, x=dem_df.index, y='President %',
                     color='Dem Primary %', 
                     title="Democrats: Presidency % vs Primary %",
                     labels={'index': 'Candidate'},
                     color_continuous_scale='blues')
    fig_dem.update_layout(template='plotly_dark', plot_bgcolor='#1E1E1E', paper_bgcolor='#1E1E1E')
    st.plotly_chart(fig_dem)

with tab3:
    st.write(":red_book: Top Republican Candidates")
    gop_df = df[df['party'] == 'GOP'].head(10)  # Top 10
    fig_gop = px.bar(gop_df, x=gop_df.index, y='President %',
                     color='GOP Primary %', 
                     title="Republicans: Presidency % vs Primary %",
                     labels={'index': 'Candidate'},
                     color_continuous_scale='reds')
    fig_gop.update_layout(template='plotly_dark', plot_bgcolor='#1E1E1E', paper_bgcolor='#1E1E1E')
    st.plotly_chart(fig_gop)

# Additional section for conditional probabilities
st.subheader("Conditional Probabilities")
st.write("Probability of Winning Presidency Given Winning Primary")
cond_fig = px.scatter(df, x='President %', y='P(President | Win Primary) %',
                      color='party', hover_name=df.index,
                      title="Scatter: Presidency % vs Conditional %",
                      color_discrete_map={'DEM': 'blue', 'GOP': 'red'})
cond_fig.update_layout(template='plotly_dark', plot_bgcolor='#1E1E1E', paper_bgcolor='#1E1E1E', 
                       legend_title_text='Party', 
                       xaxis_title='Presidency %', 
                       yaxis_title='Conditional %')
cond_fig.update_traces(marker=dict(size=12, opacity=0.8, line=dict(width=2, color='DarkSlateGrey')))
st.plotly_chart(cond_fig)

# Add expander for full data
with st.expander("View Full Data Table", expanded=False):
    st.dataframe(df.style.background_gradient(cmap='coolwarm', subset=['President %']))

# Refresh button
if st.button("Refresh Data"):
    st.experimental_rerun()

# Footer
st.markdown("---")
st.caption(":clock1: Data fetched from Polymarket API. Last updated: " + pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'))
