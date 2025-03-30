import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# App title
st.title("🔲 Interactive M-Chart Cross Simulator")

# Initialize session state
if "logs" not in st.session_state:
    st.session_state["logs"] = []

# Sliders for vertical and horizontal dash spacing
vertical_dash_distance = st.slider(
    "Vertical Dash Spacing (° visual angle)",
    min_value=0.0,
    max_value=2.0,
    value=0.0,
    step=0.1,
    key="vertical_dash"
)

horizontal_dash_distance = st.slider(
    "Horizontal Dash Spacing (° visual angle)",
    min_value=0.0,
    max_value=2.0,
    value=0.0,
    step=0.1,
    key="horizontal_dash"
)

# Calculate scores
vertical_score = round((2.0 - vertical_dash_distance) * 50, 1)
horizontal_score = round((2.0 - horizontal_dash_distance) * 50, 1)

# Display current scores
col1, col2 = st.columns(2)
col1.metric("Vertical Line Score", vertical_score)
col2.metric("Horizontal Line Score", horizontal_score)

# Visualization logic
fig, ax = plt.subplots(figsize=(6, 6))

# Define dash styles
v_dash_style = 'solid' if vertical_dash_distance == 0 else (0, (vertical_dash_distance*5, vertical_dash_distance*5))
h_dash_style = 'solid' if horizontal_dash_distance == 0 else (0, (horizontal_dash_distance*5, horizontal_dash_distance*5))

# Draw cross
ax.plot([5, 5], [1, 9], color="black", linewidth=2, linestyle=v_dash_style)  # Vertical line
ax.plot([1, 9], [5, 5], color="black", linewidth=2, linestyle=h_dash_style)  # Horizontal line

ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')
ax.set_aspect('equal')

st.pyplot(fig)

# Confirmation button
def confirm_adjustment():
    entry = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Vertical Dash Spacing": vertical_dash_distance,
        "Vertical Score": vertical_score,
        "Horizontal Dash Spacing": horizontal_dash_distance,
        "Horizontal Score": horizontal_score
    }
    st.session_state["logs"].append(entry)
    st.success("Adjustment recorded!")

if st.button("Confirm Adjustment"):
    confirm_adjustment()

# Display logs
if st.session_state["logs"]:
    df = pd.DataFrame(st.session_state["logs"])
    st.subheader("📝 Interaction History")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Logs as CSV",
        data=csv,
        file_name='mchart_cross_logs.csv',
        mime='text/csv'
    )
