import pandas as pd
import numpy as np
import pydeck as pdk
import streamlit as st
import plotly.graph_objects as go


df = pd.read_excel('data/nsw_crash_data.xlsx')
#df = pd.read_csv('data/nsw_crash_data_clean.csv')
df_2024_plus = df[df['Year of crash'] >= 2024].copy()

# ==========================================
# 1. FORENSIC SANKEY GENERATOR
# ==========================================
def render_conflict_sankey(df):
    """
    Transforms raw crash data into a Plotly Sankey diagram 
    mapping 'Location' to 'Impact Type'.
    """
    # 1. Aggregate the data (Focusing on Severe Outcomes)
    flow_df = df[df['Degree of crash - detailed'].isin(['Fatal', 'Serious Injury'])]
    flow_df = flow_df.groupby(['Type of location', 'First impact type']).size().reset_index(name='Casualties')
    
    # Filter out tiny anomalies to keep the visual clean and focused
    flow_df = flow_df[flow_df['Casualties'] > 5] 

    # 2. Extract Unique Nodes (Left side = Location, Right side = Impact)
    locations = list(flow_df['Type of location'].unique())
    impacts = list(flow_df['First impact type'].unique())
    all_nodes = locations + impacts

    # Create a mapping dictionary { '2-way undivided': 0, 'Right angle': 1, ... }
    node_mapping = {node: i for i, node in enumerate(all_nodes)}

    # 3. Map the Source, Target, and Values for Plotly
    sources = flow_df['Type of location'].map(node_mapping).tolist()
    targets = flow_df['First impact type'].map(node_mapping).tolist()
    values = flow_df['Casualties'].tolist()

    # 4. Color Strategy: Highlight the "Smoking Gun" (Vehicle-Object)
    # Give the worst impact type a bright red node, others neutral
    node_colors = ['#FF4136' if 'Object' in node else '#555555' for node in all_nodes]
    
    # 5. Build the Plotly Figure
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=25,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_nodes,
            color=node_colors
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            # Semi-transparent links for visual clarity
            color="rgba(200, 200, 200, 0.4)" 
        )
    )])

    fig.update_layout(
        title_text="<b>The Conflict Pathway:</b> How Road Design Dictates Impact Type",
        font_size=12,
        height=600,
        # Increased top margin (t=80) to make room for the headers
        margin=dict(t=80, l=20, r=20, b=20), 
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        annotations=[
            # Left Column Header
            dict(
                x=0,
                y=1.05, # Placed slightly above the top node
                xref="paper",
                yref="paper",
                text="<b>ROAD DESIGN</b>",
                showarrow=False,
                font=dict(size=14, color="#AAAAAA"),
                xanchor="left"
            ),
            # Right Column Header
            dict(
                x=1,
                y=1.05,
                xref="paper",
                yref="paper",
                text="<b>IMPACT TYPE</b>",
                showarrow=False,
                font=dict(size=14, color="#AAAAAA"),
                xanchor="right"
            )
        ]
    )
    
    return fig


def render_lethality_funnel(df):
    """
    Transforms raw crash data into a 3-Tier Plotly Sankey diagram:
    Location -> Impact Type -> Fatal Outcome.
    """
    # 1. Isolate the Worst-Case Scenario: Only look at Fatalities
    fatal_df = df[df['Degree of crash - detailed'] == 'Fatal']
    
    # 2. Aggregate Flow 1: Location -> Impact Type
    flow1 = fatal_df.groupby(['Type of location', 'First impact type']).size().reset_index(name='Count')
    flow1 = flow1[flow1['Count'] > 0] # Clean up zeros
    
    # 3. Aggregate Flow 2: Impact Type -> The 'Fatal' Node
    flow2 = fatal_df.groupby(['First impact type']).size().reset_index(name='Count')
    flow2['Outcome'] = 'Fatal' # Create the final destination node
    flow2 = flow2[flow2['Count'] > 0]
    
    # 4. Extract Unique Nodes for all 3 Tiers
    locations = list(flow1['Type of location'].unique())
    impacts = list(flow1['First impact type'].unique())
    outcomes = ['Fatal']
    
    all_nodes = locations + impacts + outcomes
    node_mapping = {node: i for i, node in enumerate(all_nodes)}
    
    # 5. Map Sources, Targets, and Values
    sources = []
    targets = []
    values = []
    link_colors = []
    
    # Build links for Flow 1 (Location -> Impact)
    for _, row in flow1.iterrows():
        sources.append(node_mapping[row['Type of location']])
        targets.append(node_mapping[row['First impact type']])
        values.append(row['Count'])
        link_colors.append("rgba(150, 150, 150, 0.4)") # Neutral grey for the first step
        
    # Build links for Flow 2 (Impact -> Fatal)
    for _, row in flow2.iterrows():
        sources.append(node_mapping[row['First impact type']])
        targets.append(node_mapping['Fatal'])
        values.append(row['Count'])
        # If it's the "Smoking Gun" (Object impact), make the final flow bright red
        if 'Object' in row['First impact type']:
            link_colors.append("rgba(255, 65, 54, 0.6)") 
        else:
            link_colors.append("rgba(255, 65, 54, 0.2)") # Faded red for other fatalities

    # 6. Color Strategy for Nodes
    node_colors = []
    for node in all_nodes:
        if node == 'Fatal':
            node_colors.append('#8B0000') # Dark Blood Red for the final outcome
        elif 'Object' in node:
            node_colors.append('#FF4136') # Bright Red for the primary threat
        else:
            node_colors.append('#555555') # Grey for locations
            
    # 7. Build the Plotly Figure
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=25,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_nodes,
            color=node_colors
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors
        )
    )])

    # 8. Layout with Column Headers for all 3 Tiers
    fig.update_layout(
        title_text="<b>The Lethality Funnel:</b> Tracing Road Geometry to Fatal Outcomes",
        font_size=12,
        height=650,
        margin=dict(t=80, l=20, r=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        annotations=[
            dict(x=0, y=1.05, xref="paper", yref="paper", text="<b>ROAD DESIGN</b>", showarrow=False, font=dict(size=14, color="#AAAAAA"), xanchor="left"),
            dict(x=0.5, y=1.05, xref="paper", yref="paper", text="<b>IMPACT TYPE</b>", showarrow=False, font=dict(size=14, color="#AAAAAA"), xanchor="center"),
            dict(x=1, y=1.05, xref="paper", yref="paper", text="<b>ULTIMATE OUTCOME</b>", showarrow=False, font=dict(size=14, color="#AAAAAA"), xanchor="right")
        ]
    )
    
    return fig



# ==========================================
# 2. STREAMLIT UI IMPLEMENTATION
# ==========================================
st.title("🛣️ Infrastructure Failure Analysis")
st.markdown("""
By stripping away driver behavior and environmental factors, we isolate the physics of the road itself. 
Follow the flow from **Left to Right** to see how specific road geometries 'funnel' vehicles into highly lethal impact types.
""")

# Render the interactive chart
st.plotly_chart(render_conflict_sankey(df_2024_plus), use_container_width=True)

# The Analyst's "So What" Callout Box
st.error("""
**Investigative Conclusion:** Notice the massive flow from **'2-way undivided'** to **'Vehicle - Object'**. This proves that intersections are not our primary vulnerability. The lack of median separation on suburban arteries forces evasive swerves into unshielded roadside hazards.
""")

# --- Add to your UI ---
st.plotly_chart(render_lethality_funnel(df_2024_plus), use_container_width=True)

# --- THE COGNITIVE BRIDGE ---
st.markdown("### The Forensic Synthesis")
st.markdown("""
The Lethality Funnel isolated our primary vulnerability: **2-way undivided roads leading to Vehicle-Object impacts.** But data only shows us *what* is happening. To intervene, we must understand *why*.

**The Mechanics of the Anomaly:**
1. **The Catalyst:** Drivers on narrow, undivided suburban arteries (50-60 km/h) drift across the center line due to distraction, fatigue, or minor merging conflicts.
2. **The Reaction:** Facing an oncoming vehicle, the driver executes a sharp, evasive swerve to the right.
3. **The Fatal Flaw:** Unlike highways, suburban roads lack a "Clear Zone." The shoulder is immediately bordered by unyielding, unprotected infrastructure (power poles, heavy trees, parked trucks).
""")

st.info("""
**The Policy Pivot:** Speed enforcement does not fix a geometry problem. To break the Lethality Funnel, we must physically separate opposing traffic. By installing **Concrete Medians**, we eliminate the oncoming threat, thereby eliminating the deadly evasive swerve into the shoulder.
""")
st.divider()
# --- END BRIDGE ---

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

st.title("Interactive Forensic Simulator")
st.markdown("""
**The 2024 Undivided Road Hazard:**
Use the controls below to observe the baseline crash mechanics. Then, toggle the **Concrete Median** to prove how infrastructure directly mitigates the fatality.
""")

# The HTML, CSS, and JavaScript for the interactive simulator
simulator_html = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { 
      margin: 0; display: flex; flex-direction: column; 
      align-items: center; font-family: sans-serif; 
      background: #0E1117; color: white; /* Matches Streamlit dark mode */
  }
  canvas { 
      background: #8F9779; /* Green Shoulder */
      border-radius: 8px; margin-top: 10px; 
      box-shadow: 0 4px 6px rgba(0,0,0,0.3);
  }
  .controls { 
      margin-top: 15px; display: flex; gap: 15px; 
      align-items: center; background: #262730;
      padding: 15px; border-radius: 8px;
  }
  button { 
      padding: 10px 20px; cursor: pointer; font-weight: bold; 
      border-radius: 4px; border: none; font-size: 14px;
  }
  #playBtn { background: #4CAF50; color: white; }
  #playBtn:hover { background: #45a049; }
  #resetBtn { background: #f44336; color: white; }
  #resetBtn:hover { background: #da190b; }
  .toggle-container { 
      display: flex; align-items: center; gap: 8px; 
      font-weight: bold; font-size: 16px;
  }
  input[type="checkbox"] { transform: scale(1.5); cursor: pointer; }
</style>
</head>
<body>
  <div class="controls">
    <button id="playBtn">▶ Play Scenario</button>
    <button id="resetBtn">↻ Reset</button>
    <div class="toggle-container">
      <input type="checkbox" id="medianToggle">
      <label for="medianToggle" style="color:#FFD700;">Install Concrete Median</label>
    </div>
  </div>
  
  <canvas id="simCanvas" width="400" height="600"></canvas>

<script>
  const canvas = document.getElementById('simCanvas');
  const ctx = canvas.getContext('2d');
  let animationId;
  let isPlaying = false;
  
  // Entities State
  let van = {};
  let sedan = {};
  let medianInstalled = false;
  let eventMessage = "";
  let messageColor = "white";
  
  document.getElementById('medianToggle').addEventListener('change', (e) => {
    medianInstalled = e.target.checked;
    resetSim();
  });
  
  document.getElementById('playBtn').addEventListener('click', () => {
    if(!isPlaying && !sedan.crashed && !van.crashed) { 
        isPlaying = true; 
        animate(); 
    }
  });
  
  document.getElementById('resetBtn').addEventListener('click', resetSim);
  
  function resetSim() {
    isPlaying = false;
    cancelAnimationFrame(animationId);
    // Initial conditions: Van drifting slightly right (vx: 0.8)
    van = { x: 135, y: -80, vx: 0.8, vy: 4, color: '#FF4136', crashed: false }; 
    sedan = { x: 230, y: 680, vx: 0, vy: -4.5, color: '#0074D9', crashed: false, swerving: false };
    eventMessage = "";
    messageColor = "white";
    draw();
  }
  
  function drawCar(car, isMovingDown) {
    // Body
    ctx.fillStyle = car.color;
    ctx.beginPath();
    ctx.roundRect(car.x, car.y, 35, 60, 5);
    ctx.fill();
    
    // Windshield to indicate direction
    ctx.fillStyle = 'rgba(0,0,0,0.6)';
    if(isMovingDown) {
        ctx.fillRect(car.x + 5, car.y + 40, 25, 12); // Front window
        ctx.fillRect(car.x + 5, car.y + 5, 25, 8);   // Back window
    } else {
        ctx.fillRect(car.x + 5, car.y + 8, 25, 12);  // Front window
        ctx.fillRect(car.x + 5, car.y + 47, 25, 8);  // Back window
    }
  }
  
  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // 1. Draw Road Surface
    ctx.fillStyle = '#555555';
    ctx.fillRect(80, 0, 240, 600);
    
    // 2. Draw Edge Lines
    ctx.fillStyle = 'white';
    ctx.fillRect(85, 0, 3, 600);
    ctx.fillRect(312, 0, 3, 600);
    
    // 3. Draw Center Line or Concrete Median
    if(medianInstalled) {
      ctx.fillStyle = '#D3D3D3'; // Concrete Barrier
      ctx.fillRect(190, 0, 20, 600);
      
      // Barrier texture lines
      ctx.fillStyle = '#A9A9A9';
      for(let i=0; i<600; i+=40) ctx.fillRect(190, i, 20, 2);
    } else {
      ctx.fillStyle = '#FFD700'; // Double Yellow Lines
      ctx.fillRect(196, 0, 3, 600);
      ctx.fillRect(202, 0, 3, 600);
    }
    
    // 4. Draw Utility Pole (The Hazard)
    ctx.fillStyle = '#8B4513';
    ctx.beginPath();
    ctx.arc(345, 300, 10, 0, Math.PI * 2);
    ctx.fill();
    ctx.lineWidth = 2;
    ctx.strokeStyle = '#5c2e0b';
    ctx.stroke();
    
    // 5. Draw Vehicles
    drawCar(van, true);
    drawCar(sedan, false);
    
    // 6. Draw UI Messaging
    if(eventMessage) {
      ctx.fillStyle = 'rgba(0,0,0,0.7)';
      ctx.fillRect(10, 10, 380, 40);
      ctx.fillStyle = messageColor;
      ctx.font = 'bold 16px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(eventMessage, canvas.width/2, 36);
    }
    
    // 7. Draw Crash Effect
    if(sedan.crashed && !medianInstalled) {
       ctx.fillStyle = 'rgba(255, 65, 54, 0.6)';
       ctx.beginPath();
       ctx.arc(345, 300, 45, 0, Math.PI*2);
       ctx.fill();
       
       ctx.fillStyle = '#FF4136';
       ctx.font = 'bold 20px sans-serif';
       ctx.textAlign = 'left';
       ctx.fillText("FATAL IMPACT", 210, 310);
    }
  }
  
  function update() {
    if(!isPlaying) return;
    
    // Van Physics
    if(!van.crashed) {
      van.y += van.vy;
      van.x += van.vx; // Drifting towards center
    }
    
    // Median Collision Logic (The Solution)
    if(medianInstalled && van.x + 35 >= 190 && van.y > 100) {
      van.vx = -1.5; // Deflect back into lane
      van.color = '#ff857f'; // Show scrape
      eventMessage = "Barrier Deflection: Fatality Prevented";
      messageColor = "#4CAF50"; // Green success text
    }
    
    // Sedan Physics
    if(!sedan.crashed) {
      sedan.y += sedan.vy;
      sedan.x += sedan.vx;
    }
    
    // No Median Logic (The Disaster)
    if(!medianInstalled) {
      // Trigger Swerve when van crosses center
      if(van.y > 180 && van.x > 155 && !sedan.swerving) {
         sedan.swerving = true;
         sedan.vx = 4; // Sharp swerve to the right
         eventMessage = "Event 1: Angle Threat triggers evasive swerve";
         messageColor = "#FFDC00"; // Yellow warning text
      }
      
      // Sedan hits the utility pole
      if(sedan.swerving && sedan.x > 310 && sedan.y < 340) {
         sedan.crashed = true;
         sedan.vx = 0;
         sedan.vy = 0;
         van.crashed = true; // Stop van to freeze scene
         van.vx = 0;
         van.vy = 0;
         eventMessage = "Event 2: No Clear Zone available.";
         messageColor = "#FF4136"; // Red fatal text
         isPlaying = false;
      }
    }
    
    // Auto-stop when cars safely exit frame
    if(sedan.y < -100 || van.y > 700) {
        isPlaying = false;
        if(medianInstalled) {
            eventMessage = "Scenario Complete: Both drivers survive.";
            messageColor = "#4CAF50";
        }
    }
  }
  
  function animate() {
    update();
    draw();
    if(isPlaying) {
        animationId = requestAnimationFrame(animate);
    }
  }
  
  resetSim(); // Initialize canvas
</script>
</body>
</html>
"""

# Inject the HTML into Streamlit
components.html(simulator_html, height=700)