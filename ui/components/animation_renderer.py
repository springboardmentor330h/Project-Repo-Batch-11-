"""
animation_renderer.py — Streamlit Component for 3D Visualization
----------------------------------------------------------------
Wraps the Three.js 3D visualization in a Streamlit component,
injecting animation data for synchronized playback.
"""

import streamlit as st
import streamlit.components.v1 as components
import json
from pathlib import Path
from typing import List, Dict, Any


def render_3d_visualization(
    animation_data: List[Dict[str, Any]],
    height: int = 500,
    show_controls: bool = True
) -> None:
    """
    Render the 3D topic visualization in Streamlit.
    
    Args:
        animation_data: List of animation state dictionaries
        height: Height of the visualization iframe in pixels
        show_controls: Whether to show camera controls
    """
    # Path to the HTML file (visualization folder is at ui/visualization, not ui/components/visualization)
    html_path = Path(__file__).parent.parent / "visualization" / "3d_visualization.html"
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Inject animation data into the HTML
        data_script = f"""
        <script>
            window.animationData = {json.dumps(animation_data)};
        </script>
        """
        
        # Insert data script before closing </head>
        html_content = html_content.replace('</head>', f'{data_script}</head>')
        
        # Render the component
        components.html(
            html_content,
            height=height,
            scrolling=False
        )
        
    except FileNotFoundError:
        st.error("3D visualization file not found. Please check the installation.")
    except Exception as e:
        st.error(f"Error rendering 3D visualization: {str(e)}")


def create_toggle_3d_section(
    animation_data: List[Dict[str, Any]],
    default_expanded: bool = False
) -> None:
    """
    Create a toggleable 3D visualization section.
    
    Args:
        animation_data: List of animation state dictionaries
        default_expanded: Whether to expand by default
    """
    st.markdown("---")
    st.markdown('<div class="step-header"><h2>🎬 3D Topic Visualization</h2></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: #e3f2fd; padding: 1.25rem; border-radius: 10px; margin-bottom: 1.5rem; border-left: 4px solid #2196F3;">
        <p style="margin: 0; color: #1565c0; font-size: 1.05rem; font-weight: 600;">Interactive 3D View: Explore topic flow with animated nodes and connections.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state for toggle
    if '3d_enabled' not in st.session_state:
        st.session_state['3d_enabled'] = default_expanded
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔮 Toggle 3D View", type="primary"):
            st.session_state['3d_enabled'] = not st.session_state['3d_enabled']
            st.rerun()
    
    with col2:
        status = "ON ✅" if st.session_state['3d_enabled'] else "OFF ⭕"
        st.markdown(f"<p style='color:#333333; padding-top: 0.5rem;'>3D Visualization: <strong>{status}</strong></p>", unsafe_allow_html=True)
    
    if st.session_state['3d_enabled']:
        if animation_data:
            render_3d_visualization(animation_data, height=500)
        else:
            st.info("No animation data available. Process audio to generate 3D visualization.")


def format_animation_summary(animation_data: List[Dict[str, Any]]) -> str:
    """
    Generate a text summary of the animation data.
    
    Args:
        animation_data: List of animation state dictionaries
        
    Returns:
        Formatted summary string
    """
    if not animation_data:
        return "No animation data available."
    
    total_segments = len(animation_data)
    total_duration = sum(d.get('Visual_Metadata', {}).get('duration', 0) for d in animation_data)
    
    return f"📊 {total_segments} topic nodes | ⏱️ Total duration: {total_duration:.0f}s"
