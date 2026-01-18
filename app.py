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

tabs = st.tabs(["📖 1. The Concept", "🧪 2. Computing Gini"])

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
        # Static example curve for conceptual clarity
        x_c = np.linspace(0, 1, 100)
        y_c = x_c**2.5 
        fig_concept = go.Figure()
        
        fig_concept.add_trace(go.Scatter(x=[0,1], y=[0,1], name="Equality", line=dict(color="black", dash="dash")))
        fig_concept.add_trace(go.Scatter(x=[0,1,1], y=[0,0,1], name="Inequality", line=dict(color="silver", width=1)))
        
        # Shading Areas
        fig_concept.add_trace(go.Scatter(x=x_c, y=x_c, showlegend=False, line=dict(color='rgba(0,0,0,0)')))
        fig_concept.add_trace(go.Scatter(x=x_c, y=y_c, fill='tonexty', name="Area A", fillcolor='rgba(255, 0, 0, 0.2)', line=dict(color="red")))
        fig_concept.add_trace(go.Scatter(x=x_c, y=y_c, fill='tozeroy', name="Area B", fillcolor='rgba(0, 0, 255, 0.1)', line=dict(color="red")))
        
        fig_concept.add_annotation(x=0.5, y=0.35, text="Area A", showarrow=False, font=dict(size=16, color="red"))
        fig_concept.add_annotation(x=0.7, y=0.15, text="Area B", showarrow=False, font=dict(size=16, color="blue"))
        fig_concept.update_layout(xaxis_title="Cumulative Pop %", yaxis_title="Cumulative Income %", margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig_concept, use_container_width=True)



# --- TAB 2: COMPUTING GINI ---
with tabs[1]:
    st.header("Computing Gini Using Variable Trapezoids")
    st.write("Construct your distribution. Ensure both **Population** and **Income** shares sum to exactly 100%.")
    
    col_ctrl, col_res = st.columns([1, 1.5])
    
    with col_ctrl:
        n_points = st.slider("Number of Population Groups", 2, 20, 5)
        
        # Standard starting values
        init_val = round(100.0/n_points, 1)
        df_input = pd.DataFrame({
            "Group": range(1, n_points+1), 
            "Pop. Share %": [init_val] * n_points,
            "Income Share %": [init_val] * n_points
        })
        
        edited_df = st.data_editor(df_input, hide_index=True, use_container_width=True)
        
        pop_total = round(edited_df["Pop. Share %"].sum(), 2)
        inc_total = round(edited_df["Income Share %"].sum(), 2)
        
        c1, c2 = st.columns(2)
        with c1:
            if pop_total == 100.0: st.success(f"Pop: {pop_total}% ✅")
            else: st.error(f"Pop: {pop_total}% ❌")
        with c2:
            if inc_total == 100.0: st.success(f"Income: {inc_total}% ✅")
            else: st.error(f"Income: {inc_total}% ❌")

    with col_res:
        if pop_total == 100.0 and inc_total == 100.0:
            dx = edited_df["Pop. Share %"].values / 100
            dy = edited_df["Income Share %"].values / 100
            
            x_coords = np.cumsum(np.insert(dx, 0, 0))
            y_coords = np.cumsum(np.insert(dy, 0, 0))
            
            st.write("### 1. Trapezoidal Step-Summation")
            calc_rows = []
            area_b = 0
            for i in range(len(dx)):
                base = dx[i]
                h1, h2 = y_coords[i], y_coords[i+1]
                avg_h = (h1 + h2) / 2
                seg_area = base * avg_h
                area_b += seg_area
                calc_rows.append([f"{base:.2f}", f"{h1:.3f}", f"{h2:.3f}", f"{avg_h:.3f}", f"{seg_area:.4f}"])
            
            math_df = pd.DataFrame(calc_rows, columns=[
                "Base (xᵢ - xᵢ₋₁)", 
                "yᵢ₋₁", 
                "yᵢ", 
                "Avg Height (yᵢ + yᵢ₋₁)/2", 
                "Area (Base × Avg H)"
            ])
            st.table(math_df)
            
            st.write("### 2. Final Summation")
            st.latex(r"Area\ B = \sum Area_{segments} = " + f"{area_b:.4f}")
            gini = (0.5 - area_b) / 0.5
            st.metric("Final Gini (1 - 2B)", round(gini, 4))
            
            fig_man = go.Figure()
            fig_man.add_trace(go.Scatter(x=[0,1], y=[0,1], name="Equality", line=dict(color="black", dash="dash")))
            fig_man.add_trace(go.Scatter(x=x_coords, y=y_coords, mode='lines+markers', name="Lorenz Curve", line=dict(color="red")))
            
            for i in range(len(dx)):
                fig_man.add_trace(go.Scatter(
                    x=[x_coords[i], x_coords[i], x_coords[i+1], x_coords[i+1]],
                    y=[0, y_coords[i], y_coords[i+1], 0],
                    fill="toself", fillcolor='rgba(255,0,0,0.1)', line=dict(width=0), showlegend=False
                ))
                fig_man.add_shape(type="line", x0=x_coords[i+1], y0=0, x1=x_coords[i+1], y1=y_coords[i+1],
                                  line=dict(color="rgba(0,0,0,0.3)", width=1, dash="dot"))

            fig_man.update_layout(title="Visualizing the Sum of Areas", xaxis_title="Cumulative Population Share", yaxis_title="Cumulative Income Share")
            st.plotly_chart(fig_man, use_container_width=True)
            
            
        else:
            st.info("Balance both the Population and Income shares to 100% to calculate the Gini.")

st.divider()
st.caption("Economics Instructional Tool | Standardized for NumPy 2.0+")
