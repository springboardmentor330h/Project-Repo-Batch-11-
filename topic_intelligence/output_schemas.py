"""
output_schemas.py — Structured Output Definitions for LEXARA
---------------------------------------------------------------
Defines deterministic, machine-consumable schemas for transcription
and animation outputs. Ensures modular, validated data structures.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from enum import Enum
import json


# =========================
# ENUMS
# =========================

class AnimationType(Enum):
    """Types of animations for topic visualization."""
    TOPIC_TRANSITION = "topic_transition"
    HIGHLIGHT = "highlight"
    FLOW = "flow"
    IDLE = "idle"


class AnimationState(Enum):
    """States of animation for a segment."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    TRANSITIONING = "transitioning"
    PENDING = "pending"


# =========================
# TRANSCRIPTION OUTPUT
# =========================

@dataclass
class TranscriptionOutput:
    """
    Structured output for a single transcription segment.
    
    Attributes:
        segment_id: Unique identifier for the segment (e.g., seg_001)
        start_time: Start time in seconds
        end_time: End time in seconds
        topic_title: Context-aware title (max 8-10 words) or UNKNOWN
        transcript_text: Full transcript text for this segment
    """
    segment_id: str
    start_time: float
    end_time: float
    topic_title: str
    transcript_text: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def validate(self) -> bool:
        """Validate the transcription output."""
        if not self.segment_id:
            return False
        if self.start_time < 0 or self.end_time < 0:
            return False
        if self.start_time >= self.end_time:
            return False
        if not self.topic_title:
            return False
        return True


@dataclass
class VisualMetadata:
    """
    Metadata for 3D visualization of a segment.
    
    Attributes:
        node_color: Hex color code for the node
        node_size: Size multiplier for the node
        position: 3D position coordinates
        connections: List of connected segment IDs
    """
    node_color: str = "#2196F3"
    node_size: float = 1.0
    position: Dict[str, float] = field(default_factory=lambda: {"x": 0, "y": 0, "z": 0})
    connections: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


# =========================
# ANIMATION OUTPUT
# =========================

@dataclass
class AnimationOutput:
    """
    Structured output for 3D animation state per segment.
    
    Attributes:
        segment_id: Unique identifier matching TranscriptionOutput
        animation_type: Type of animation (transition, highlight, flow)
        animation_state: Current state (active, inactive, etc.)
        sync_timestamp: Timestamp for synchronization with audio
        visual_metadata: 3D visualization parameters
    """
    segment_id: str
    animation_type: str
    animation_state: str
    sync_timestamp: float
    visual_metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def validate(self) -> bool:
        """Validate the animation output."""
        if not self.segment_id:
            return False
        if self.sync_timestamp < 0:
            return False
        if not self.animation_type:
            return False
        if not self.animation_state:
            return False
        return True


# =========================
# COMBINED OUTPUT
# =========================

@dataclass
class LexaraOutput:
    """
    Complete structured output for LEXARA processing.
    
    Attributes:
        project_title: Fixed project title
        audio_file: Source audio file name
        transcription_outputs: List of transcription segments
        animation_outputs: List of animation states
    """
    project_title: str = "LEXARA: Automated Podcast Transcription & Insights"
    audio_file: str = ""
    transcription_outputs: List[TranscriptionOutput] = field(default_factory=list)
    animation_outputs: List[AnimationOutput] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with nested structures."""
        return {
            "Project_Title": self.project_title,
            "audio_file": self.audio_file,
            "Transcription_Output": [t.to_dict() for t in self.transcription_outputs],
            "3D_Animation_Output": [a.to_dict() for a in self.animation_outputs]
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def validate(self) -> Dict[str, Any]:
        """
        Validate the complete output.
        
        Returns:
            Dict with validation status and any errors found.
        """
        errors = []
        
        # Check each segment has exactly one topic title
        for t in self.transcription_outputs:
            if not t.validate():
                errors.append(f"Invalid transcription segment: {t.segment_id}")
        
        # Check animation states map correctly to segments
        transcription_ids = {t.segment_id for t in self.transcription_outputs}
        animation_ids = {a.segment_id for a in self.animation_outputs}
        
        missing_animations = transcription_ids - animation_ids
        if missing_animations:
            errors.append(f"Missing animation states for segments: {missing_animations}")
        
        orphan_animations = animation_ids - transcription_ids
        if orphan_animations:
            errors.append(f"Orphan animation states: {orphan_animations}")
        
        # Check for overlapping segments
        sorted_segments = sorted(self.transcription_outputs, key=lambda x: x.start_time)
        for i in range(1, len(sorted_segments)):
            prev = sorted_segments[i-1]
            curr = sorted_segments[i]
            if prev.end_time > curr.start_time:
                errors.append(f"Overlapping segments: {prev.segment_id} and {curr.segment_id}")
        
        # Check for missing segments (gaps)
        # Note: Gaps may be intentional (silence), so we just warn
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }


# =========================
# FACTORY FUNCTIONS
# =========================

def create_transcription_output(
    topic_id: int,
    start: float,
    end: float,
    title: str,
    text: str
) -> TranscriptionOutput:
    """
    Factory function to create a TranscriptionOutput.
    """
    segment_id = f"seg_{topic_id + 1:03d}"
    return TranscriptionOutput(
        segment_id=segment_id,
        start_time=start,
        end_time=end,
        topic_title=title,
        transcript_text=text
    )


def create_animation_output(
    topic_id: int,
    start: float,
    node_color: str,
    position_x: float = 0,
    position_y: float = 0,
    position_z: float = 0,
    node_size: float = 1.0,
    prev_segment_id: Optional[str] = None
) -> AnimationOutput:
    """
    Factory function to create an AnimationOutput.
    """
    segment_id = f"seg_{topic_id + 1:03d}"
    
    connections = []
    if prev_segment_id:
        connections.append(prev_segment_id)
    
    visual_metadata = VisualMetadata(
        node_color=node_color,
        node_size=node_size,
        position={"x": position_x, "y": position_y, "z": position_z},
        connections=connections
    )
    
    return AnimationOutput(
        segment_id=segment_id,
        animation_type=AnimationType.TOPIC_TRANSITION.value,
        animation_state=AnimationState.ACTIVE.value,
        sync_timestamp=start,
        visual_metadata=visual_metadata.to_dict()
    )
