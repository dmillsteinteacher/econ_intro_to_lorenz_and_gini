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
        * **Line of Perfect Inequality (Grey):** One person has 100% of the income ($y=0$ until $x=1$).
        * **Area A:** The 'Gap' between equality and reality.
        * **Area B:** The area underneath the Lorenz curve.
        
        Since the total area below the line of equality is exactly **0.5**, we calculate the Gini as:
        """)
        st.latex(r"Gini = \frac{Area\ A}{Area\ A + Area\ B} = \frac{0.5 - B}{0.5} = 1 - 2B")
    
    with col2:
        x_c = np.linspace(0, 1, 100)
        y_c = x_c**2.5 
        fig_concept = go.Figure()
        
        fig_concept.add_trace(go.Scatter(x=[0,1], y=[0,1], name="Equality", line=dict(color="black", dash="dash")))
        fig_concept.add_trace(go.Scatter(x=[0,1,1], y=[0,0,1], name="Inequality", line=dict(color="silver", width=1)))
        
        # Area A (Sandwiched)
        fig_concept.add_trace(go.Scatter(x=x_c, y=x_c, showlegend=False, line=dict(color='rgba(0,0,0,0)')))
        fig_concept.add_trace(go.Scatter(x=x_c, y=y_c, fill='tonexty', name="Area A", fillcolor='rgba(255, 0, 0, 0.2)', line=dict(color="red")))
        
        # Area B
        fig_concept.add_trace(go.Scatter(x=x_c, y=y_c, fill='tozeroy', name="Area B", fillcolor='rgba(0, 0, 255, 0.1)', line=dict(color="red")))
        
        fig_concept.add_annotation(x=0.5, y=0.35, text="Area A", showarrow=False, font=dict(size=16, color="red"))
        fig_concept.add_annotation(x=0.7, y=0.15, text="Area B", showarrow=False, font=dict(size=16, color="blue"))
        fig_concept.update_layout(xaxis_title="Cumulative Pop %", yaxis_title="Cumulative Income %", margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig_concept, use_container_width=True)



# --- TAB 2: MANUAL LAB ---
with tabs[1]:
    st.header("Computing Gini Using Trapezoids")
    
    col_ctrl, col_res = st.columns([1, 2])
    
    with col_ctrl:
        n_points = st.select_slider("Select Number of Data Points", options=[5, 10, 20], value=5)
        st.write("**Enter Income Shares for each segment:**")
        
        # Setup initial state
        init_shares = [round(100.0/n_points, 1)] * n_points
        df_input = pd.DataFrame({"Segment": range(1, n_points+1), "Income Share": init_shares})
        edited_df = st.data_editor(df_input, hide_index=True, use_container_width=True)
        
        current_total = round(edited_df["Income Share"].sum(), 2)
        
        if current_total == 100.0:
            st.success(f"✅ Total: {current_total}%")
        else:
            st.error(f"❌ Total: {current_total}%")
            st.info("The economy is out of balance. Adjust the shares to sum to exactly 100% to calculate the Gini.")
        
        if current_total == 100.0:
            shares = edited_df["Income Share"].values
            cum_y = np.cumsum(np.insert(shares/100, 0, 0))
            x_coords = np.linspace(0, 1, n_points + 1)
            
            st.write("### The Math of Area B")
            calc_data = []
            area_b = 0
            base = 1/n_points
            for i in range(n_points):
                h1, h2 = cum_y[i], cum_y[i+1]
                avg_h = (h1 + h2) / 2
                seg_area = base * avg_h
                area_b += seg_area
                calc_data.append([f"{h1:.3f}", f"{h2:.3f}", f"{avg_h:.3f}", f"{seg_area:.4f}"])
            
            calc_df = pd.DataFrame(calc_data, columns=[
                "Height 1 (yᵢ₋₁)", 
                "Height 2 (yᵢ)", 
                "Avg Height (H₁+H₂)/2", 
                f"Area (Base {base:.2f} × Avg H)"
            ])
            st.table(calc_df)

    with col_res:
        if current_total == 100.0:
            gini = (0.5 - area_b) / 0.5
            st.metric("Gini Coefficient (1 - 2B)", round(gini, 4))
            st.write(f"Sum of Area B: **{area_b:.4f}**")
            
            fig_man = go.Figure()
            fig_man.add_trace(go.Scatter(x=[0,1], y=[0,1], name="Equality", line=dict(color="black", dash="dash")))
            fig_man.add_trace(go.Scatter(x=x_coords, y=cum_y, mode='lines+markers', name="Trapezoid Fit", line=dict(color="red")))
            
            for i in range(n_points):
                fig_man.add_trace(go.Scatter(
                    x=[x_coords[i], x_coords[i], x_coords[i+1], x_coords[i+1]],
                    y=[0, cum_y[i], cum_y[i+1], 0],
                    fill="toself", fillcolor='rgba(255,0,0,0.1)', line=dict(color="rgba(255,0,0,0.1)"),
                    showlegend=False
                ))
            fig_man.update_layout(title="Trapezoid Rule in Action", xaxis_title="Population Share", yaxis_title="Income Share")
            st.plotly_chart(fig_man, use_container_width=True)
        else:
            st.image("https://via.placeholder.com/600x400.png?text=Awaiting+Valid+100%+Distribution", use_container_width=True)



# --- TAB 3: THE SIMULATOR ---
with tabs[2]:
    st.header("The Function Simulator")
    n_exp = st.slider("Inequality Intensity (Exponent n)", 1.0, 10.0, 2.0, 0.1)
    
    x_sim, y_sim = get_lorenz_coords(100, n_exp)
    area_sim = np.trapezoid(y_sim, x_sim)
    g_sim = (0.5 - area_sim) / 0.5
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.latex(r"L(x) = x^{" + f"{n_exp:.1f}" + r"}")
        st.write(f"""
        ### Continuous Model Analysis:
        * **Area B** (Integral of $x^n$): **{area_sim:.4f}**
        * **Gini** (1 - 2B): **{round(g_sim, 3)}**
        
        The power function mimics real-world Pareto distributions. As **n** grows, the "bend" in the curve sharpens, representing a higher concentration of income at the top percentiles.
        """)
        st.metric("Simulated Gini", round(g_sim, 3))
    
    with c2:
        fig_sim = go.Figure()
        fig_sim.add_trace(go.Scatter(x=x_sim, y=y_sim, fill='tonexty', name="Lorenz Curve", line=dict(color="green")))
        fig_sim.add_trace(go.Scatter(x=[0,1], y=[0,1], line=dict(color="black", dash="dash")))
        fig_sim.update_layout(xaxis_title="Population Share", yaxis_title="Income Share")
        st.plotly_chart(fig_sim, use_container_width=True)

st.divider()
st.caption("Standardized for NumPy 2.0+ and Streamlit Cloud")
