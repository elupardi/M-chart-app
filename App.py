import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

# App title
st.title("🔲 Interactive M-Chart Simulator")

# Initialize session state
if "logs" not in st.session_state:
    st.session_state["logs"] = []

if "direction" not in st.session_state:
    st.session_state["direction"] = "Horizontal"  # Start with horizontal line

direction = st.session_state["direction"]

# Confirm adjustment and switch direction immediately
def confirm_and_switch(temp_dash_distance):
    score = round((2.0 - temp_dash_distance) * 50, 1)
    entry = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Direction": direction,
        "Dash Spacing": temp_dash_distance,
        "Score": score
    }
    st.session_state["logs"].append(entry)
    st.success(f"{direction} adjustment recorded (Score: {score})!")
    
    # Switch direction immediately
    st.session_state["direction"] = "Horizontal" if direction == "Vertical" else "Vertical"

# Display the current direction
st.subheader(f"Adjust Dash Spacing: **{direction} Lines**")

# Slider uses direction-dependent key to force reset
temp_dash_distance = st.slider(
    "Dash spacing (° visual angle)",
    min_value=0.0,
    max_value=2.0,
    value=0.0,
    step=0.1,
    key=f"slider_{direction}"
)

# Display current score based on temporary slider value
current_score = round((2.0 - temp_dash_distance) * 50, 1)
st.metric("Current Score", current_score)

# Visualization logic
fig, ax = plt.subplots(figsize=(6, 6))
line_positions = np.linspace(1, 9, 9)

# Conditional dash pattern based on dash_distance
if temp_dash_distance == 0:
    dash_style = 'solid'
elif temp_dash_distance <= 0.2:
    dash_style = (0, (0.5, temp_dash_distance*5))
else:
    dash_style = (0, (temp_dash_distance*5, temp_dash_distance*5))

if direction == "Vertical":
    for x in line_positions:
        ax.plot([x, x], [1, 9], color="black", linewidth=2, linestyle=dash_style)
else:
    for y in line_positions:
        ax.plot([1, 9], [y, y], color="black", linewidth=2, linestyle=dash_style)

ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')
ax.set_aspect('equal')

st.pyplot(fig)

# Confirmation button
if st.button(f"Confirm {direction} Adjustment"):
    confirm_and_switch(temp_dash_distance)
    st.rerun()  # force immediate update after switching

# Display logs
if st.session_state["logs"]:
    df = pd.DataFrame(st.session_state["logs"])
    st.subheader("📝 Interaction History")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Logs as CSV",
        data=csv,
        file_name='mchart_interaction_logs.csv',
        mime='text/csv'
    )