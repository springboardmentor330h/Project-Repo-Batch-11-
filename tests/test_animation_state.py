"""
test_animation_state.py — Tests for 3D Animation State Generation
-----------------------------------------------------------------
Validates animation states map correctly to segment timestamps.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from topic_intelligence.animation.animation_state import (
    generate_animation_states,
    AnimationStateGenerator,
    AnimationNode
)


def test_animation_states_generated():
    """Test that animation states are generated for each topic."""
    sample_topics = [
        {"topic_id": 0, "start": 0, "end": 120, "topic_title": "Introduction"},
        {"topic_id": 1, "start": 120, "end": 300, "topic_title": "Main Topic"},
        {"topic_id": 2, "start": 300, "end": 480, "topic_title": "Conclusion"}
    ]
    
    animation_states = generate_animation_states(sample_topics)
    
    assert len(animation_states) == len(sample_topics), \
        f"Expected {len(sample_topics)} states, got {len(animation_states)}"
    
    print(f"✅ Animation states count test passed: {len(animation_states)} states generated")


def test_segment_id_format():
    """Test that segment IDs have correct format."""
    sample_topics = [
        {"topic_id": 0, "start": 0, "end": 60}
    ]
    
    animation_states = generate_animation_states(sample_topics)
    segment_id = animation_states[0]["Segment_ID"]
    
    assert segment_id.startswith("seg_"), f"Segment ID should start with 'seg_', got '{segment_id}'"
    assert len(segment_id) == 7, f"Segment ID should be 7 chars, got {len(segment_id)}"
    
    print(f"✅ Segment ID format test passed: '{segment_id}'")


def test_sync_timestamp():
    """Test that sync timestamps match topic start times."""
    sample_topics = [
        {"topic_id": 0, "start": 0, "end": 120},
        {"topic_id": 1, "start": 120, "end": 300}
    ]
    
    animation_states = generate_animation_states(sample_topics)
    
    for topic, state in zip(sample_topics, animation_states):
        expected_timestamp = topic["start"]
        actual_timestamp = state["Sync_Timestamp"]
        assert actual_timestamp == expected_timestamp, \
            f"Expected timestamp {expected_timestamp}, got {actual_timestamp}"
    
    print(f"✅ Sync timestamp test passed")


def test_visual_metadata_structure():
    """Test that visual metadata has required fields."""
    sample_topics = [
        {"topic_id": 0, "start": 0, "end": 120}
    ]
    
    animation_states = generate_animation_states(sample_topics)
    metadata = animation_states[0]["Visual_Metadata"]
    
    required_fields = ["node_color", "node_size", "position", "connections", "duration"]
    for field in required_fields:
        assert field in metadata, f"Missing required field: {field}"
    
    assert "x" in metadata["position"], "Position missing x coordinate"
    assert "y" in metadata["position"], "Position missing y coordinate"
    assert "z" in metadata["position"], "Position missing z coordinate"
    
    print(f"✅ Visual metadata structure test passed")


def test_connections_to_previous():
    """Test that nodes connect to previous nodes."""
    sample_topics = [
        {"topic_id": 0, "start": 0, "end": 60},
        {"topic_id": 1, "start": 60, "end": 120},
        {"topic_id": 2, "start": 120, "end": 180}
    ]
    
    animation_states = generate_animation_states(sample_topics)
    
    # First node should have no connections
    assert len(animation_states[0]["Visual_Metadata"]["connections"]) == 0
    
    # Subsequent nodes should connect to previous
    assert "seg_001" in animation_states[1]["Visual_Metadata"]["connections"]
    assert "seg_002" in animation_states[2]["Visual_Metadata"]["connections"]
    
    print(f"✅ Node connections test passed")


def test_animation_types():
    """Test that animation types are assigned correctly."""
    sample_topics = [
        {"topic_id": 0, "start": 0, "end": 60},
        {"topic_id": 1, "start": 60, "end": 120},
        {"topic_id": 2, "start": 120, "end": 180}
    ]
    
    animation_states = generate_animation_states(sample_topics)
    
    assert animation_states[0]["Animation_Type"] == "intro"
    assert animation_states[1]["Animation_Type"] == "topic_transition"
    assert animation_states[2]["Animation_Type"] == "outro"
    
    print(f"✅ Animation types test passed")


def test_empty_topics():
    """Test that empty topic list returns empty states."""
    animation_states = generate_animation_states([])
    
    assert len(animation_states) == 0, "Empty topics should return empty states"
    
    print(f"✅ Empty topics test passed")


def test_node_size_range():
    """Test that node sizes are within valid range."""
    sample_topics = [
        {"topic_id": 0, "start": 0, "end": 30},   # Short
        {"topic_id": 1, "start": 30, "end": 300},  # Long
    ]
    
    animation_states = generate_animation_states(sample_topics)
    
    for state in animation_states:
        size = state["Visual_Metadata"]["node_size"]
        assert 0.5 <= size <= 2.0, f"Node size {size} out of range [0.5, 2.0]"
    
    print(f"✅ Node size range test passed")


if __name__ == "__main__":
    print("=" * 60)
    print("LEXARA 3D Animation State Tests")
    print("=" * 60)
    
    test_animation_states_generated()
    test_segment_id_format()
    test_sync_timestamp()
    test_visual_metadata_structure()
    test_connections_to_previous()
    test_animation_types()
    test_empty_topics()
    test_node_size_range()
    
    print("=" * 60)
    print("All tests passed! ✅")
    print("=" * 60)
