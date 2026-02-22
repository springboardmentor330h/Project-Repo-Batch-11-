"""
Animation module for LEXARA 3D visualization.
"""

from .animation_state import generate_animation_states, AnimationStateGenerator
from .animation_schema import AnimationConfig, get_animation_config

__all__ = [
    'generate_animation_states',
    'AnimationStateGenerator',
    'AnimationConfig',
    'get_animation_config'
]
