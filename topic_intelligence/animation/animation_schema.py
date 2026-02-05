"""
animation_schema.py — Animation Configuration Schema
----------------------------------------------------
Defines configuration schema for 3D animation settings.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
import json
from pathlib import Path


@dataclass
class AnimationConfig:
    """
    Configuration for 3D animation visualization.
    """
    enabled: bool = True
    transition_duration_ms: int = 500
    base_radius: float = 3.0
    height_step: float = 0.5
    spiral_factor: float = 0.8
    default_node_size: float = 1.0
    node_colors: List[str] = field(default_factory=lambda: [
        '#2196F3', '#4CAF50', '#FF9800', '#9C27B0',
        '#00BCD4', '#E91E63', '#3F51B5', '#009688'
    ])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "enabled": self.enabled,
            "transition_duration_ms": self.transition_duration_ms,
            "base_radius": self.base_radius,
            "height_step": self.height_step,
            "spiral_factor": self.spiral_factor,
            "default_node_size": self.default_node_size,
            "node_colors": self.node_colors
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnimationConfig':
        """Create from dictionary."""
        return cls(
            enabled=data.get('enabled', True),
            transition_duration_ms=data.get('transition_duration_ms', 500),
            base_radius=data.get('base_radius', 3.0),
            height_step=data.get('height_step', 0.5),
            spiral_factor=data.get('spiral_factor', 0.8),
            default_node_size=data.get('default_node_size', 1.0),
            node_colors=data.get('node_colors', [
                '#2196F3', '#4CAF50', '#FF9800', '#9C27B0',
                '#00BCD4', '#E91E63', '#3F51B5', '#009688'
            ])
        )


def get_animation_config(config_path: str = None) -> AnimationConfig:
    """
    Load animation configuration from config.json.
    
    Args:
        config_path: Optional path to config file
        
    Returns:
        AnimationConfig instance
    """
    if config_path is None:
        config_path = Path(__file__).resolve().parent.parent.parent / "config.json"
    else:
        config_path = Path(config_path)
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            animation_data = data.get('animation', {})
            return AnimationConfig.from_dict(animation_data)
    except (FileNotFoundError, json.JSONDecodeError):
        return AnimationConfig()  # Return defaults
