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

# --- HEADER ---
st.title("📊 Lorenz Curves and Gini Coefficients")
st.subheader("Interactive Economics Laboratory")

tabs = st.tabs(["📖 1. The Concept", "🧪 2. Manual Lab", "🎮 3. The Simulator"])

# --- TAB 1: THE CONCEPT ---
with tabs[0]:
    st.header("The Geometry of Distribution")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.write("""
        The **Lorenz Curve** maps the cumulative share of income against the cumulative share of the population.
        
        * **Line of Perfect Equality (Black Dash):** Every person has the same income ($y = x$).
        * **Line of Perfect Inequality (Grey):** One person has everything; the curve follows the bottom and right axes.
        * **Area A:** The 'Gap' of inequality.
        * **Area B:** The area under the actual distribution curve.
        """)
        st.latex(r"Gini = \frac{Area\ A}{Area\ A + Area\ B} = \frac{Area\ A}{0.5}")
    
    with col2:
        # Annotated Concept Plot
        x_c = np.linspace(0, 1, 100)
        y_c = x_c**2.5
        fig_concept = go.Figure()
        fig_concept.add_trace(go.Scatter(x=[0,1], y=[0,1], name="Equality", line=dict(color="black", dash="dash")))
        fig_concept.add_trace(go.Scatter(x=[0,1,1], y=[0,0,1], name="Inequality", line=dict(color="silver", width=1)))
        fig_concept.add_trace(go.Scatter(x=x_c, y=y_c, fill='tonexty', name="Area A", fillcolor='rgba(255, 0, 0, 0.2)', line=dict(color="red")))
        fig_concept.add_trace(go.Scatter(x=x_c, y=y_c, fill='tozeroy', name="Area B", fillcolor='rgba(0, 0, 255, 0.1)', line=dict(color="red")))
        
        fig_concept.add_annotation(x=0.4, y=0.6, text="Area A", showarrow=False, font=dict(size=16, color="red"))
        fig_concept.add_annotation(x=0.7, y=0.2, text="Area B", showarrow=False, font=dict(size=16, color="blue"))
        fig_concept.update_layout(xaxis_title="Cumulative Pop %", yaxis_title="Cumulative Income %", margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig_concept, use_container_width=True)



# --- TAB 2: MANUAL LAB ---
with tabs[1]:
    st.header("The Trapezoid Lab")
    
    col_ctrl, col_res = st.columns([1, 2])
    
    with col_ctrl:
        n_points = st.select_slider("Select Number of Data Points", options=[5, 10, 20], value=5)
        st.write("Edit the **Income Share** for each segment below:")
        
        # Create an editable dataframe based on selected points
        init_shares = [100/n_points] * n_points
        df_input = pd.DataFrame({"Segment": range(1, n_points+1), "Income Share": init_shares})
        edited_df = st.data_editor(df_input, hide_index=True)
        
        # Calculate Logic
        shares = edited_df["Income Share"].values
        total = np.sum(shares)
        norm_shares = shares / total if total > 0 else shares
        cum_y = np.cumsum(np.insert(norm_shares, 0, 0))
        x_coords = np.linspace(0, 1, n_points + 1)
        
        # Display Math Computation
        st.write("### Trapezoid Calculations")
        calc_data = []
        area_b = 0
        w = 1/n_points
        for i in range(n_points):
            h1, h2 = cum_y[i], cum_y[i+1]
            seg_area = w * (h1 + h2) / 2
            area_b += seg_area
            calc_data.append([f"{h1:.2f}", f"{h2:.2f}", f"{seg_area:.4f}"])
        
        calc_df = pd.DataFrame(calc_data, columns=["Height 1", "Height 2", "Area"])
        st.table(calc_df)
        
    with col_res:
        gini = (0.5 - area_b) / 0.5
        st.metric("Gini Coefficient", round(gini, 4))
        
        fig_man = go.Figure()
        fig_man.add_trace(go.Scatter(x=[0,1], y=[0,1], name="Equality", line=dict(color="black", dash="dash")))
        fig_man.add_trace(go.Scatter(x=x_coords, y=cum_y, mode='lines+markers', name="Trapezoid Fit", line=dict(color="red")))
        
        # Visualize the Trapezoids
        for i in range(n_points):
            fig_man.add_trace(go.Scatter(
                x=[x_coords[i], x_coords[i], x_coords[i+1], x_coords[i+1]],
                y=[0, cum_y[i], cum_y[i+1], 0],
                fill="toself", fillcolor='rgba(255,0,0,0.1)', line=dict(color="rgba(255,0,0,0.2)"),
                showlegend=False
            ))
            
        fig_man.update_layout(title="Geometric Approximation", xaxis_title="Population", yaxis_title="Income")
        st.plotly_chart(fig_man, use_container_width=True)



# --- TAB 3: THE SIMULATOR ---
with tabs[2]:
    st.header("The Function Simulator")
    st.write("How does a mathematical function translate to inequality?")
    
    n_exp = st.slider("Inequality Intensity (Exponent n)", 1.0, 10.0, 2.0, 0.1)
    
    x_sim, y_sim = get_lorenz_coords(100, n_exp)
    area_sim = np.trapezoid(y_sim, x_sim)
    g_sim = (0.5 - area_sim) / 0.5
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.write(f"Using $L(x) = x^{{{n_exp}}}$")
        st.write("""
        When we use a power function, the exponent determines how quickly income 'piles up' at the end of the distribution.
        
        A higher **n** creates a deeper curve, meaning the bottom percentages have almost no income, while the top percentage has nearly all of it.
        """)
        st.metric("Simulated Gini", round(g_sim, 3))
    
    with c2:
        fig_sim = go.Figure()
        fig_sim.add_trace(go.Scatter(x=x_sim, y=y_sim, fill='tonexty', name="Lorenz Curve", line=dict(color="green")))
        fig_sim.add_trace(go.Scatter(x=[0,1], y=[0,1], line=dict(color="black", dash="dash")))
        st.plotly_chart(fig_sim, use_container_width=True)

st.divider()
st.caption("Standardized for NumPy 2.0+ and Streamlit Cloud")
