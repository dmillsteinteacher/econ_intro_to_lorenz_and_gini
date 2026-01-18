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
    shares = df['Income Share'].values
    total = np.sum(shares)
    
    # Validation: prevent division by zero
    if total <= 0:
        return 0.0, np.zeros(len(shares) + 1), 0.0
    
    norm_shares = shares / total
    cum_shares = np.cumsum(np.insert(norm_shares, 0, 0))
    x = np.linspace(0, 1, len(cum_shares))
    
    # Trapezoid Rule using NumPy 2.0 syntax
    area_b = np.trapezoid(cum_shares, x)
    gini = (0.5 - area_b) / 0.5
    return max(0, round(gini, 4)), cum_shares, total

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
        
        * **Line of Perfect Equality:** A 45° diagonal line. Every person earns exactly the same.
        * **Line of Perfect Inequality:** An 'L' shape. One person earns 100% of the income; everyone else earns 0%.
        * **Area A:** The gap between the Equality Line and the Lorenz Curve.
        * **Area B:** The area underneath the Lorenz Curve.
        """)
        st.latex(r"Gini = \frac{Area\ A}{Area\ A + Area\ B} = \frac{Area\ A}{0.5}")
    with col2:
        st.write("### Visual Reference")
        # Direct instruction for the user to visualize the areas
        st.write("""
        On a Lorenz graph:
        1. The **Top Triangle** above the curve is Area A.
        2. The **Bottom Shape** under the curve is Area B.
        3. The Gini is the ratio of that top gap to the entire bottom half of the square.
        """)
        

# --- TAB 2: MANUAL LAB ---
with tabs[1]:
    st.header("The Trapezoid Lab")
    st.write("Edit the **Income Share** column. The app will normalize your inputs to 100% automatically.")
    
    default_data = pd.DataFrame({
        "Quintile": ["Bottom 20%", "Second 20%", "Third 20%", "Fourth 20%", "Top 20%"],
        "Income Share": [5.0, 10.0, 15.0, 25.0, 45.0]
    })
    
    col_edit, col_plot = st.columns([1, 2])
    
    with col_edit:
        st.write("### 1. Input Data")
        edited_df = st.data_editor(default_data, num_rows="fixed", hide_index=True)
        gini_val, cum_y, current_total = calculate_gini_from_dataframe(edited_df)
        
        if abs(current_total - 100) > 0.1:
            st.warning(f"Note: Your shares sum to {current_total}%. We have normalized them to 100% for the calculation.")
        
        st.metric("Gini Coefficient", gini_val)
        
        st.write("### 2. The Computation")
        area_a = round(gini_val * 0.5, 4)
        area_b = round(0.5 - area_a, 4)
        st.write(f"**Area A (The Gap):** {area_a}")
        st.write(f"**Area B (Under Curve):** {area_b}")
        st.write(f"**Total Area (A + B):** 0.5")

    with col_plot:
        x_vals = np.linspace(0, 1, len(cum_y))
        fig = go.Figure()
        
        # Perfect Equality & Inequality
        fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], name="Perfect Equality", line=dict(color="black", dash="dash")))
        fig.add_trace(go.Scatter(x=[0, 1, 1], y=[0, 0, 1], name="Perfect Inequality", line=dict(color="silver", dash="dot")))
        
        # The Trapezoidal Fit
        fig.add_trace(go.Scatter(x=x_vals, y=cum_y, fill='tozeroy', mode='lines+markers', 
                                 name="Lorenz Curve", line=dict(color="red", width=3)))
        
        # Show Trapezoid Segments
        for xv, yv in zip(x_vals, cum_y):
            fig.add_shape(type="line", x0=xv, y0=0, x1=xv, y1=yv, line=dict(color="rgba(255,0,0,0.2)", width=1))

        fig.update_layout(title="Trapezoidal Rule Approximation", xaxis_title="Population Share", yaxis_title="Income Share")
        st.plotly_chart(fig, use_container_width=True)
        

# --- TAB 3: THE SIMULATOR ---
with tabs[2]:
    st.header("The Power of Concentration")
    col_sim_text, col_sim_plot = st.columns([1, 2])
    
    with col_sim_text:
        st.write("""
        ### Why the Power Function?
        We use $L(x) = x^n$ to simulate different economies.
        * **n = 1.0:** Perfect Equality.
        * **n = 2.0:** Moderate (Typical developed nation).
        * **n > 5.0:** Extreme concentration of wealth.
        """)
        n_exp = st.slider("Inequality Intensity (n)", 1.0, 10.0, 2.0, 0.1)
        
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
st.caption("Version 3.1 - Built for Macroeconomics Instruction")
