import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from utils import format_int


def render_decision_summary_tab(
    filtered_df: pd.DataFrame,
    scenario_reduction: int,
) -> None:
    st.markdown(
        '<div class="section-title">5. Decision summary and intervention logic</div>',
        unsafe_allow_html=True,
    )

    total_crashes = len(filtered_df)
    estimated_prevented = int(total_crashes * scenario_reduction / 100)
    remaining_crashes = total_crashes - estimated_prevented

    s1, s2, s3 = st.columns(3)

    s1.metric("Current crash load", format_int(total_crashes))

    s2.metric(
        f"Estimated prevented / improved ({scenario_reduction}%)",
        format_int(estimated_prevented),
    )

    s3.metric("Projected remaining", format_int(remaining_crashes))

    st.markdown(
        f"""
        <div class="action-box">
        <h3>What-if scenario interpretation</h3>
        A <b>{scenario_reduction}%</b> improvement scenario is useful as an ambitious target for hotspot-based intervention.
        It should not be read only as “fewer crashes”. It can also represent a broader road-network benefit:
        safer intersections, better signal timing, smoother travel flow, fewer disruption points, and more reliable routes for drivers,
        buses, pedestrians, and school-zone users.
        <br><br>
        Under the current filters, this scenario suggests approximately <b>{estimated_prevented:,}</b> crashes or disruption events could be prevented or reduced,
        leaving around <b>{remaining_crashes:,}</b> remaining incidents in the selected view.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="insight-box">
        <b>Suggested call to action:</b> Prioritise the LGAs and time windows where crash volume,
        casualty rate, school-zone exposure, and repeated temporal concentration overlap.
        Due to dashboards, it supports decision-making for safer and more efficient movement across NSW roads.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # stimulation
    st.set_page_config(layout="wide")

    st.header("Interactive Forensic Simulator")
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