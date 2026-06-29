import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

import analytics as a

# ----------------------------------------------------------------------------
# PAGE CONFIG + DESIGN TOKENS
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Chore Bundling Studio | Package Design Dashboard",
    page_icon="🧺",
    layout="wide",
    initial_sidebar_state="expanded",
)

PRIMARY = "#0F5C5C"      # deep teal - trust / clean
SECONDARY = "#3E8E8E"    # mid teal
AQUA = "#8FD8D2"         # soft aqua
ACCENT = "#FF6B5B"       # coral - calls to action / recommendation
AMBER = "#F2B134"        # diagnostic / caution
INK = "#1F2D2D"
PAPER = "#F7F9F8"
GRID = "#E4ECEB"

CHORE_PALETTE = [PRIMARY, SECONDARY, AQUA, ACCENT, AMBER, "#6C8EBF", "#A3C9A8", "#D98E73", "#B0A8B9", "#7FA7A1"]

px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = CHORE_PALETTE

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@500;700&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    color: {INK};
}}
h1, h2, h3 {{
    font-family: 'Fraunces', serif;
    color: {INK};
    letter-spacing: -0.01em;
}}
.hero-card {{
    background: linear-gradient(135deg, {PRIMARY} 0%, {SECONDARY} 100%);
    padding: 28px 32px;
    border-radius: 14px;
    color: white;
    margin-bottom: 18px;
}}
.hero-card h1 {{ color: white; margin-bottom: 4px; font-size: 1.7rem;}}
.hero-card p {{ color: #E6F2F1; margin: 0; font-size: 0.98rem; }}
.kpi-card {{
    background: white;
    border: 1px solid {GRID};
    border-left: 4px solid {PRIMARY};
    border-radius: 10px;
    padding: 14px 16px;
    height: 100%;
}}
.kpi-label {{ font-size: 0.78rem; color: #5C6B6A; text-transform: uppercase; letter-spacing: .04em; font-weight: 600;}}
.kpi-value {{ font-family: 'Fraunces', serif; font-size: 1.65rem; color: {INK}; font-weight: 700; margin-top: 2px;}}
.kpi-sub {{ font-size: 0.78rem; color: #7A8786; }}
.insight-box {{
    background: #FFF4F1;
    border-left: 4px solid {ACCENT};
    padding: 14px 16px;
    border-radius: 8px;
    margin: 10px 0;
    font-size: 0.95rem;
}}
.persona-card {{
    background: white; border: 1px solid {GRID}; border-radius: 12px;
    padding: 18px; margin-bottom: 10px;
}}
.persona-title {{ font-family:'Fraunces', serif; font-size: 1.15rem; font-weight:700; color: {PRIMARY};}}
.tag {{
    display:inline-block; background:{AQUA}33; color:{PRIMARY}; font-weight:600;
    font-size:0.72rem; padding:2px 9px; border-radius:20px; margin-right:5px;
}}
section[data-testid="stSidebar"] {{ background-color: {PAPER}; }}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# DATA LOADING (cached)
# ----------------------------------------------------------------------------
@st.cache_data
def load():
    return a.load_data("data/synthetic_survey_data_bundling_CLEANED.csv")

df_raw = load()

# ----------------------------------------------------------------------------
# SIDEBAR — FILTERS
# ----------------------------------------------------------------------------
st.sidebar.markdown("## 🧺 Filters")
areas = st.sidebar.multiselect("Area of Dubai", sorted(df_raw["area_dubai"].unique()),
                                default=sorted(df_raw["area_dubai"].unique()))
acc_types = st.sidebar.multiselect("Accommodation type", sorted(df_raw["accommodation_type"].unique()),
                                    default=sorted(df_raw["accommodation_type"].unique()))
budget_range = st.sidebar.slider(
    "Monthly cleaning budget (AED)",
    int(df_raw["monthly_budget_aed"].min()), int(df_raw["monthly_budget_aed"].max()),
    (int(df_raw["monthly_budget_aed"].min()), int(df_raw["monthly_budget_aed"].max())),
)
st.sidebar.markdown("---")
k_segments = st.sidebar.slider("Number of student segments (k)", 2, 5, 3,
                                help="K-Means cluster count for the Segments tab")
st.sidebar.markdown("---")
st.sidebar.caption(
    "Methodology stack: Descriptive KPIs → Apriori market-basket rules (diagnostic) "
    "→ K-Means segmentation → Random Forest package-prediction (predictive), "
    "with Robust Scaling applied ahead of distance-based clustering."
)

df = df_raw[
    df_raw["area_dubai"].isin(areas)
    & df_raw["accommodation_type"].isin(acc_types)
    & df_raw["monthly_budget_aed"].between(*budget_range)
].reset_index(drop=True)

if len(df) < 30:
    st.warning("Fewer than 30 respondents match these filters — results may be unstable. Widen the filters in the sidebar.")

# ----------------------------------------------------------------------------
# HERO
# ----------------------------------------------------------------------------
st.markdown(f"""
<div class="hero-card">
<h1>What should the Starter Pack actually contain?</h1>
<p>A data-driven package design study for student cleaning services in Dubai — turning {len(df)} survey
responses into bundle recommendations, so the business stops selling à la carte and starts selling the
package students already want.</p>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs([
    "📋 Brief & Summary",
    "📊 Demand (Descriptive)",
    "🧺 Bundle Discovery (Apriori)",
    "🧑‍🤝‍🧑 Student Segments (Clustering)",
    "🤖 Package Predictor (Classification)",
    "📦 Recommended Packages",
])

# Stash tabs in session for cross-references
import tabs_brief, tabs_descriptive, tabs_bundles, tabs_segments, tabs_predictor, tabs_packages

with tabs[0]:
    tabs_brief.render(df, a)
with tabs[1]:
    tabs_descriptive.render(df, a, CHORE_PALETTE)
with tabs[2]:
    tabs_bundles.render(df, a, PRIMARY, ACCENT)
with tabs[3]:
    tabs_segments.render(df, a, k_segments, CHORE_PALETTE, PRIMARY, ACCENT)
with tabs[4]:
    tabs_predictor.render(df, a, PRIMARY, ACCENT)
with tabs[5]:
    tabs_packages.render(df, a, PRIMARY, ACCENT, AMBER)
