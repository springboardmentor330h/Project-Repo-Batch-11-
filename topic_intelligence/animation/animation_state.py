"""
animation_state.py — 3D Animation State Generation for LEXARA
----------------------------------------------------------------
Generates animation states for each topic segment, synchronized
with transcript timestamps for real-time 3D visualization.
"""

import math
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Node colors for segments
SEGMENT_COLORS = [
    '#2196F3', '#4CAF50', '#FF9800', '#9C27B0',
    '#00BCD4', '#E91E63', '#3F51B5', '#009688'
]


@dataclass
class AnimationNode:
    """Represents a single 3D node for a topic segment."""
    segment_id: str
    animation_type: str
    animation_state: str
    sync_timestamp: float
    node_color: str
    node_size: float
    position: Dict[str, float]
    connections: List[str]
    duration: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for JSON output."""
        return {
            "Segment_ID": self.segment_id,
            "Animation_Type": self.animation_type,
            "Animation_State": self.animation_state,
            "Sync_Timestamp": self.sync_timestamp,
            "Visual_Metadata": {
                "node_color": self.node_color,
                "node_size": self.node_size,
                "position": self.position,
                "connections": self.connections,
                "duration": self.duration
            }
        }


class AnimationStateGenerator:
    """
    Generates 3D animation states for podcast topic segments.
    
    Positions nodes in a spiral pattern for visual clarity,
    with connecting lines between consecutive segments.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the animation state generator.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.base_radius = self.config.get('base_radius', 3.0)
        self.height_step = self.config.get('height_step', 0.5)
        self.spiral_factor = self.config.get('spiral_factor', 0.8)
        self.default_node_size = self.config.get('default_node_size', 1.0)
    
    def calculate_position(self, index: int, total: int) -> Dict[str, float]:
        """
        Calculate 3D position for a node using spiral layout.
        
        Args:
            index: Index of the current segment
            total: Total number of segments
            
        Returns:
            Dictionary with x, y, z coordinates
        """
        # Spiral layout for visual distribution
        angle = (2 * math.pi * index) / max(total, 1) * self.spiral_factor
        radius = self.base_radius + (index * 0.3)
        
        x = radius * math.cos(angle)
        y = index * self.height_step
        z = radius * math.sin(angle)
        
        return {
            "x": round(x, 2),
            "y": round(y, 2),
            "z": round(z, 2)
        }
    
    def calculate_node_size(self, duration: float, total_duration: float) -> float:
        """
        Calculate node size based on segment duration.
        
        Args:
            duration: Duration of this segment in seconds
            total_duration: Total podcast duration in seconds
            
        Returns:
            Size multiplier for the node
        """
        if total_duration <= 0:
            return self.default_node_size
        
        # Size proportional to duration (0.5 to 2.0 range)
        proportion = duration / total_duration
        size = 0.5 + (proportion * 10)  # Scale up
        return min(max(size, 0.5), 2.0)  # Clamp to range
    
    def generate_node(
        self,
        topic: Dict[str, Any],
        index: int,
        total: int,
        total_duration: float,
        prev_segment_id: Optional[str] = None
    ) -> AnimationNode:
        """
        Generate animation node for a single topic segment.
        
        Args:
            topic: Topic data dictionary
            index: Index of this topic
            total: Total number of topics
            total_duration: Total podcast duration
            prev_segment_id: ID of the previous segment for connections
            
        Returns:
            AnimationNode instance
        """
        segment_id = f"seg_{index + 1:03d}"
        start_time = topic.get("start", 0)
        end_time = topic.get("end", 0)
        duration = end_time - start_time
        
        # Determine animation type based on position
        if index == 0:
            animation_type = "intro"
        elif index == total - 1:
            animation_type = "outro"
        else:
            animation_type = "topic_transition"
        
        # All nodes start as active
        animation_state = "active"
        
        # Get color (cycling through palette)
        node_color = SEGMENT_COLORS[index % len(SEGMENT_COLORS)]
        
        # Calculate position
        position = self.calculate_position(index, total)
        
        # Calculate size based on duration
        node_size = self.calculate_node_size(duration, total_duration)
        
        # Connections to previous node
        connections = [prev_segment_id] if prev_segment_id else []
        
        return AnimationNode(
            segment_id=segment_id,
            animation_type=animation_type,
            animation_state=animation_state,
            sync_timestamp=start_time,
            node_color=node_color,
            node_size=round(node_size, 2),
            position=position,
            connections=connections,
            duration=round(duration, 2)
        )
    
    def generate_all(self, topics: List[Dict[str, Any]]) -> List[AnimationNode]:
        """
        Generate animation nodes for all topics.
        
        Args:
            topics: List of topic dictionaries
            
        Returns:
            List of AnimationNode instances
        """
        if not topics:
            return []
        
        # Calculate total duration
        total_duration = max(t.get("end", 0) for t in topics) if topics else 0
        
        nodes = []
        prev_segment_id = None
        
        for i, topic in enumerate(topics):
            node = self.generate_node(
                topic=topic,
                index=i,
                total=len(topics),
                total_duration=total_duration,
                prev_segment_id=prev_segment_id
            )
            nodes.append(node)
            prev_segment_id = node.segment_id
        
        return nodes


def generate_animation_states(topics: List[Dict[str, Any]], config: Optional[Dict] = None) -> List[Dict[str, Any]]:
    """
    Main entry point for generating animation states.
    
    Args:
        topics: List of topic dictionaries from segmentation
        config: Optional configuration settings
        
    Returns:
        List of animation state dictionaries
    """
    generator = AnimationStateGenerator(config)
    nodes = generator.generate_all(topics)
    return [node.to_dict() for node in nodes]
