import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(page_title="Lorenz Curves and Gini Coefficients", layout="wide")

# --- LOGIC ENGINE ---
def get_lorenz_coords(n_points, p_value):
    x = np.linspace(0, 1, n_points + 1)
    y = x**p_value
    return x, y

def calculate_gini_from_dataframe(df):
    """Calculates Gini based on user-edited income shares"""
    # Normalize shares to ensure they sum to 1
    shares = df['Income Share'].values
    total = np.sum(shares)
    if total == 0: return 0, [0]*len(shares)
    
    norm_shares = shares / total
    cum_shares = np.cumsum(np.insert(norm_shares, 0, 0))
    x = np.linspace(0, 1, len(cum_shares))
    
    # Trapezoid Rule: Area B
    area_b = np.trapezoid(cum_shares, x)
    gini = (0.5 - area_b) / 0.5
    return max(0, round(gini, 4)), cum_shares

# --- HEADER ---
st.title("📊 Lorenz Curves and Gini Coefficients")
st.subheader("Interactive Economics Laboratory")

tabs = st.tabs(["📖 1. The Concept", "🧪 2. Manual Lab", "🎮 3. The Simulator"])

# --- TAB 1: THE CONCEPT ---
with tabs[0]:
    st.header("Understanding the Geometry of Inequality")
    col1, col2 = st.columns([3, 2])
    with col1:
        st.write("""
        The **Lorenz Curve** visualizes how a nation's total income is distributed across its population.
        
        * **Line of Perfect Equality:** A 45° diagonal line. If everyone earned the same, the bottom 20% would own exactly 20% of the income.
        * **Line of Perfect Inequality:** An L-shaped line where one person earns 100% of everything and everyone else earns 0%.
        * **Area A:** The gap between the Equality Line and the Lorenz Curve.
        * **Area B:** The area underneath the Lorenz Curve.
        """)
        st.latex(r"Gini = \frac{Area\ A}{Area\ A + Area\ B}")
    with col2:
        # Requesting a diagram with Areas A and B, plus Equality/Inequality lines
        

# --- TAB 2: MANUAL LAB ---
with tabs[1]:
    st.header("The Trapezoid Lab")
    st.write("Edit the **Income Share** column below to see how different distributions change the Gini Coefficient.")
    
    # Initialize default quintile data
    default_data = pd.DataFrame({
        "Quintile": ["Bottom 20%", "Second 20%", "Third 20%", "Fourth 20%", "Top 20%"],
        "Income Share": [5.0, 10.0, 15.0, 25.0, 45.0]
    })
    
    col_edit, col_plot = st.columns([1, 2])
    
    with col_edit:
        st.write("### 1. Input Income Shares")
        edited_df = st.data_editor(default_data, num_rows="fixed", hide_index=True)
        gini_val, cum_y = calculate_gini_from_dataframe(edited_df)
        st.metric("Resulting Gini Coefficient", gini_val)
        
        st.write("### 2. The Computation")
        st.write(f"Area B (Under Curve) ≈ {0.5 - (gini_val * 0.5):.4f}")
        st.write(f"Area A (The Gap) ≈ {gini_val * 0.5:.4f}")

    with col_plot:
        x_vals = np.linspace(0, 1, len(cum_y))
        fig = go.Figure()
        
        # Perfect Equality
        fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], name="Perfect Equality", line=dict(color="black", dash="dash")))
        
        # Trapezoid Visualization (The 'Rule' in action)
        fig.add_trace(go.Scatter(x=x_vals, y=cum_y, fill='tozeroy', mode='lines+markers', 
                                 name="Lorenz Curve (Trapezoid Fit)", line=dict(color="red", width=3)))
        
        # Draw vertical lines to show the trapezoid segments
        for xv, yv in zip(x_vals, cum_y):
            fig.add_shape(type="line", x0=xv, y0=0, x1=xv, y1=yv, line=dict(color="gray", width=1, dash="dot"))

        fig.update_layout(title="Visualizing the Trapezoidal Approximation", xaxis_title="Cumulative Population %", yaxis_title="Cumulative Income %")
        st.plotly_chart(fig, use_container_width=True)

# --- TAB 3: THE SIMULATOR ---
with tabs[2]:
    st.header("The Power of Concentration")
    
    col_sim_text, col_sim_plot = st.columns([1, 2])
    
    with col_sim_text:
        st.write("""
        ### Why the Power Function?
        In this simulator, we use the function $L(x) = x^n$ to model the curve.
        
        * **When $n=1$:** The curve is a straight line (Perfect Equality).
        * **When $n$ increases:** The curve 'bows' deeper. This simulates a economy where income is increasingly concentrated at the very top.
        
        As the exponent grows, the "gravity" of wealth pulls the curve closer to the bottom-right corner.
        """)
        n_exp = st.slider("Select Inequality Intensity (n)", 1.0, 10.0, 2.0, 0.1)
        
        x_sim, y_sim = get_lorenz_coords(100, n_exp)
        area_sim = np.trapezoid(y_sim, x_sim)
        g_sim = (0.5 - area_sim) / 0.5
        st.metric("Simulated Gini", round(g_sim, 3))

    with col_sim_plot:
        fig_sim = go.Figure()
        fig_sim.add_trace(go.Scatter(x=x_sim, y=y_sim, fill='tonexty', name="Simulated Curve", line=dict(color="green")))
        fig_sim.add_trace(go.Scatter(x=[0, 1], y=[0, 1], line=dict(color="black", dash="dash"), name="Equality"))
        fig_sim.update_layout(xaxis_title="Population", yaxis_title="Income Share")
        st.plotly_chart(fig_sim, use_container_width=True)

st.divider()
st.caption("Developed for Economics Instruction - Built with NumPy 2.0 & Streamlit")
