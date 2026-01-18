import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(page_title="Lorenz Curves and Gini Coefficients", layout="wide")

# --- STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- LOGIC ENGINE ---
def get_lorenz_coords(n_points, p_value):
    """Generates coordinates using NumPy 2.0 vectorized operations"""
    x = np.linspace(0, 1, n_points + 1)
    y = x**p_value
    return x, y

def calc_gini_details(x, y):
    """Calculates trapezoid areas and returns a breakdown for the manual lab"""
    details = []
    area_b = 0
    for i in range(1, len(x)):
        width = x[i] - x[i-1]
        h1 = y[i-1]
        h2 = y[i]
        avg_h = (h1 + h2) / 2
        trap_area = width * avg_h
        area_b += trap_area
        details.append({
            "Segment": i,
            "Width": round(width, 3),
            "Avg Height": round(avg_h, 4),
            "Area": round(trap_area, 4)
        })
    gini = (0.5 - area_b) / 0.5
    return max(0, round(gini, 4)), area_b, details

# --- HEADER ---
st.title("📊 Lorenz Curves and Gini Coefficients")
st.subheader("An Interdisciplinary Tool for Macroeconomics")

tabs = st.tabs(["📖 1. The Concept", "🧪 2. Manual Lab", "🎮 3. The Simulator"])

# --- TAB 1: THE CONCEPT ---
with tabs[0]:
    st.header("What is a Lorenz Curve?")
    col1, col2 = st.columns([3, 2])
    with col1:
        st.write("""
        The **Lorenz Curve** is a graphical representation of the distribution of income or wealth. 
        It was developed by Max O. Lorenz in 1905.
        
        - **The Diagonal Line (45°):** Represents **Perfect Equality**. 
        - **The Lorenz Curve:** Shows the actual cumulative share of income earned by the bottom *x%* of the population.
        
        ### The Gini Coefficient
        The Gini Coefficient is a numerical measure of inequality. It is the ratio of the area between the 
        line of equality and the Lorenz curve (**Area A**) to the total area of the triangle below the line of equality.
        """)
        st.latex(r"Gini = \frac{Area\ A}{Area\ A + Area\ B}")
    with col2:
        st.info("""
        **Economic Interpretation:**
        A Gini of **0** represents perfect equality (everyone has the same income). 
        A Gini of **1** represents perfect inequality (one person has all the income).
        """)

# --- TAB 2: MANUAL LAB ---
with tabs[1]:
    st.header("The Trapezoid Lab")
    st.write("Calculate the Gini Coefficient using the Trapezoidal Rule.")
    
    col_c1, col_c2 = st.columns([1, 3])
    with col_c1:
        target_ineq = st.radio("Select Distribution:", ["Low Inequality", "Moderate", "High"])
        powers = {"Low Inequality": 1.5, "Moderate": 3.0, "High": 6.0}
        p = powers[target_ineq]
        
        n_groups = st.select_slider("Number of Data Groups (n):", options=[5, 10, 20, 50])
        st.caption(f"Splitting the population into {n_groups} segments.")

    x_disc, y_disc = get_lorenz_coords(n_groups, p)
    gini_disc, area_b_val, trap_data = calc_gini_details(x_disc, y_disc)

    col_g1, col_g2 = st.columns([2, 1])
    with col_g1:
        fig_disc = go.Figure()
        x_s, y_s = get_lorenz_coords(100, p)
        fig_disc.add_trace(go.Scatter(x=x_s, y=y_s, name="Actual Curve", line=dict(color='rgba(31, 119, 180, 0.2)')))
        fig_disc.add_trace(go.Scatter(x=x_disc, y=y_disc, mode='lines+markers', name="Trapezoids", line=dict(color='red')))
        fig_disc.add_trace(go.Scatter(x=[0,1], y=[0,1], name="Equality", line=dict(dash='dash', color='black')))
        fig_disc.update_layout(xaxis_title="Cumulative Population %", yaxis_title="Cumulative Income %")
        st.plotly_chart(fig_disc, use_container_width=True)

    with col_g2:
        st.metric("Calculated Gini", gini_disc)
        st.write("**Area Breakdown**")
        st.dataframe(pd.DataFrame(trap_data), height=300, hide_index=True)
        st.write(f"Total Area B = **{area_b_val:.4f}**")

# --- TAB 3: THE SIMULATOR ---
with tabs[2]:
    st.header("The Function Simulator")
    st.write("Adjust the shape of the distribution to see how the Gini coefficient reacts.")
    
    col_s1, col_s2 = st.columns([1, 2])
    with col_s1:
        n_exp = st.slider("Inequality Intensity (n)", 1.0, 15.0, 2.0, 0.1)
        st.latex(r"L(x) = x^n")
        st.write("---")
        st.write("**Economic Benchmarks:**")
        if n_exp < 1.8: st.write("✅ Low (Nordic Model)")
        elif n_exp < 3.0: st.write("⚠️ Moderate (US/UK)")
        else: st.write("🚨 High (Extreme Concentration)")
        
    with col_s2:
        x_sim, y_sim = get_lorenz_coords(100, n_exp)
        
        # STANDARDIZED: Using the NumPy 2.0 trapezoid function
        area_sim = np.trapezoid(y_sim, x_sim)
            
        gini_sim = (0.5 - area_sim) / 0.5
        
        fig_sim = go.Figure()
        fig_sim.add_trace(go.Scatter(x=x_sim, y=y_sim, fill='tonexty', name="Lorenz Curve", line=dict(color='green')))
        fig_sim.add_trace(go.Scatter(x=[0,1], y=[0,1], line=dict(color='black', dash='dash'), name="Equality"))
        fig_sim.update_layout(title=f"Gini Coefficient: {max(0, round(gini_sim, 3))}")
        st.plotly_chart(fig_sim, use_container_width=True)

st.divider()
st.caption("Math Tip: The Gini Coefficient is the ratio of Area A to the total area of the triangle (0.5).")

# --- END OF FILE BUFFER ---
# -------------------------------------------------------------------------
# Version 3.0: Standardized for NumPy 2.0+ (using np.trapezoid).
# This code is modern, concise, and follows current Python best practices.
# -------------------------------------------------------------------------
# [EOF]
