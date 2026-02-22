"""
test_topic_title.py — Tests for Topic Title Generation
------------------------------------------------------
Validates topic title generation meets LEXARA constraints.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from topic_intelligence.topic_segmentation.topic_title_generator import (
    generate_topic_title,
    validate_topic_title,
    truncate_to_word_limit,
    UNKNOWN_TITLE,
    MAX_TITLE_WORDS,
    MIN_TITLE_WORDS
)


def test_title_word_limit():
    """Test that titles are within word limit."""
    sample_text = """
    Virtual assistants offer tremendous flexibility and opportunities for remote work.
    You can work from anywhere in the world with just a laptop and internet connection.
    The benefits include flexible schedules, diverse client projects, and work-life balance.
    """
    
    title = generate_topic_title(sample_text)
    word_count = len(title.split())
    
    assert word_count <= MAX_TITLE_WORDS, f"Title has {word_count} words, max is {MAX_TITLE_WORDS}"
    print(f"✅ Title word limit test passed: '{title}' ({word_count} words)")


def test_title_minimum_words():
    """Test that titles have minimum words or are UNKNOWN."""
    sample_text = "Virtual assistants work remotely with flexibility."
    
    title = generate_topic_title(sample_text)
    
    if title != UNKNOWN_TITLE:
        word_count = len(title.split())
        assert word_count >= MIN_TITLE_WORDS, f"Title has {word_count} words, min is {MIN_TITLE_WORDS}"
    
    print(f"✅ Minimum words test passed: '{title}'")


def test_unknown_for_short_text():
    """Test that very short text returns UNKNOWN."""
    short_text = "Hello"
    
    title = generate_topic_title(short_text)
    
    assert title == UNKNOWN_TITLE, f"Expected UNKNOWN for short text, got '{title}'"
    print(f"✅ Short text UNKNOWN test passed")


def test_unknown_for_empty_text():
    """Test that empty text returns UNKNOWN."""
    empty_text = ""
    
    title = generate_topic_title(empty_text)
    
    assert title == UNKNOWN_TITLE, f"Expected UNKNOWN for empty text, got '{title}'"
    print(f"✅ Empty text UNKNOWN test passed")


def test_truncate_function():
    """Test the truncate function."""
    long_title = "This Is A Very Long Title That Should Be Truncated To Ten Words Only"
    
    truncated = truncate_to_word_limit(long_title, 10)
    word_count = len(truncated.split())
    
    assert word_count == 10, f"Expected 10 words, got {word_count}"
    print(f"✅ Truncate function test passed: '{truncated}'")


def test_validate_function():
    """Test the validation function."""
    valid_title = "Discussion on Remote Work Opportunities"
    invalid_short = "Hi"
    unknown = UNKNOWN_TITLE
    
    assert validate_topic_title(valid_title) == True
    assert validate_topic_title(invalid_short) == False
    assert validate_topic_title(unknown) == True  # UNKNOWN is valid
    
    print(f"✅ Validation function test passed")


def test_title_is_human_readable():
    """Test that generated titles are human-readable (basic check)."""
    sample_text = """
    This podcast episode discusses the benefits of meditation and mindfulness.
    Regular practice can reduce stress and improve mental clarity.
    Many successful entrepreneurs incorporate meditation into their daily routines.
    """
    
    title = generate_topic_title(sample_text)
    
    # Basic readability checks
    assert title[0].isupper() or title == UNKNOWN_TITLE, "Title should be capitalized"
    assert not title.startswith("Title:"), "Title should not have prefix"
    
    print(f"✅ Human readability test passed: '{title}'")


if __name__ == "__main__":
    print("=" * 60)
    print("LEXARA Topic Title Generation Tests")
    print("=" * 60)
    
    test_title_word_limit()
    test_title_minimum_words()
    test_unknown_for_short_text()
    test_unknown_for_empty_text()
    test_truncate_function()
    test_validate_function()
    test_title_is_human_readable()
    
    print("=" * 60)
    print("All tests passed! ✅")
    print("=" * 60)
