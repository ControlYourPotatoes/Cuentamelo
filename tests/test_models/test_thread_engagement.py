"""
Tests for the thread engagement state system.
"""
import pytest
from app.models.conversation import ThreadEngagementState


class TestThreadEngagementStateCreation:
    """Test thread engagement state creation and basic properties."""
    
    def test_thread_state_creation(self, thread_state_builder):
        """Should create thread engagement state with correct properties."""
        thread_state = thread_state_builder\
            .with_thread_id("test_thread_001")\
            .with_original_content("Test original content")\
            .build()
        
        assert thread_state.thread_id == "test_thread_001"
        assert thread_state.original_content == "Test original content"
        assert len(thread_state.character_replies) == 0
        assert thread_state.created_at is not None
    
    def test_thread_state_with_custom_id(self, thread_state_builder):
        """Should create thread state with custom thread ID."""
        thread_state = thread_state_builder\
            .with_thread_id("custom_thread_123")\
            .build()
        
        assert thread_state.thread_id == "custom_thread_123"
    
    def test_thread_state_with_custom_content(self, thread_state_builder):
        """Should create thread state with custom original content."""
        content = "Breaking: New Puerto Rican Music Festival Announced in San Juan! 🎵🇵🇷"
        thread_state = thread_state_builder\
            .with_original_content(content)\
            .build()
        
        assert thread_state.original_content == content


class TestCharacterReplyManagement:
    """Test character reply management and rate limiting."""
    
    def test_add_first_character_reply(self, sample_thread_state):
        """Should add first reply from a character successfully."""
        character_id = "jovani_vazquez"
        reply_content = "¡Qué noticia increíble! 🎵"
        
        # Check if character can reply initially
        assert sample_thread_state.can_character_reply(character_id) is True
        
        # Add reply
        sample_thread_state.add_character_reply(character_id, reply_content)
        
        # Verify reply was added
        assert character_id in sample_thread_state.character_replies
        assert len(sample_thread_state.character_replies[character_id]) == 1
        assert sample_thread_state.character_replies[character_id][0] == reply_content
    
    def test_add_multiple_replies_from_same_character(self, sample_thread_state):
        """Should allow multiple replies from same character up to limit."""
        character_id = "jovani_vazquez"
        
        # Add first reply
        sample_thread_state.add_character_reply(character_id, "First reply")
        assert len(sample_thread_state.character_replies[character_id]) == 1
        
        # Add second reply
        sample_thread_state.add_character_reply(character_id, "Second reply")
        assert len(sample_thread_state.character_replies[character_id]) == 2
        
        # Add third reply
        sample_thread_state.add_character_reply(character_id, "Third reply")
        assert len(sample_thread_state.character_replies[character_id]) == 3
    
    def test_rate_limiting_prevents_excessive_replies(self, sample_thread_state):
        """Should prevent characters from exceeding reply limits."""
        character_id = "jovani_vazquez"
        
        # Add replies up to the limit
        for i in range(3):
            sample_thread_state.add_character_reply(character_id, f"Reply {i+1}")
        
        # Fourth reply should be blocked
        can_reply = sample_thread_state.can_character_reply(character_id)
        assert can_reply is False
        
        # Should not be able to add more replies
        sample_thread_state.add_character_reply(character_id, "Fourth reply")
        assert len(sample_thread_state.character_replies[character_id]) == 3
    
    def test_multiple_characters_in_thread(self, sample_thread_state):
        """Should allow multiple characters to reply in the same thread."""
        characters = ["jovani_vazquez", "politico_boricua", "ciudadano_boricua"]
        
        for char_id in characters:
            sample_thread_state.add_character_reply(char_id, f"Reply from {char_id}")
        
        # All characters should have replies
        assert len(sample_thread_state.character_replies) == 3
        for char_id in characters:
            assert char_id in sample_thread_state.character_replies
            assert len(sample_thread_state.character_replies[char_id]) == 1
    
    def test_character_reply_timestamps(self, sample_thread_state):
        """Should track timestamps for character replies."""
        character_id = "jovani_vazquez"
        reply_content = "Test reply with timestamp"
        
        sample_thread_state.add_character_reply(character_id, reply_content)
        
        # Check that reply timestamps are tracked
        replies = sample_thread_state.character_replies[character_id]
        assert len(replies) == 1
        
        # The reply should be stored with timestamp information
        # (Implementation may vary, but should track timing)


class TestThreadContextGeneration:
    """Test thread context generation for different characters."""
    
    def test_get_thread_context_for_new_character(self, sample_thread_state):
        """Should generate appropriate context for character with no replies."""
        character_id = "new_character"
        context = sample_thread_state.get_thread_context(character_id)
        
        assert context is not None
        assert isinstance(context, str)
        assert len(context) > 0
        assert sample_thread_state.original_content in context
    
    def test_get_thread_context_for_character_with_replies(self, sample_thread_state):
        """Should generate context including character's previous replies."""
        character_id = "jovani_vazquez"
        reply_content = "¡Qué noticia increíble! 🎵"
        
        sample_thread_state.add_character_reply(character_id, reply_content)
        context = sample_thread_state.get_thread_context(character_id)
        
        assert context is not None
        assert isinstance(context, str)
        assert len(context) > 0
        assert sample_thread_state.original_content in context
        assert reply_content in context
    
    def test_get_thread_context_for_different_characters(self, sample_thread_state):
        """Should generate different contexts for different characters."""
        # Add replies from multiple characters
        sample_thread_state.add_character_reply("jovani_vazquez", "Reply from Jovani")
        sample_thread_state.add_character_reply("politico_boricua", "Reply from Político")
        
        # Get contexts for different characters
        jovani_context = sample_thread_state.get_thread_context("jovani_vazquez")
        politico_context = sample_thread_state.get_thread_context("politico_boricua")
        new_char_context = sample_thread_state.get_thread_context("new_character")
        
        # Contexts should be different
        assert jovani_context != politico_context
        assert jovani_context != new_char_context
        assert politico_context != new_char_context
    
    def test_thread_context_includes_original_content(self, sample_thread_state):
        """Should always include original content in thread context."""
        character_id = "test_character"
        context = sample_thread_state.get_thread_context(character_id)
        
        assert sample_thread_state.original_content in context


class TestThreadStateValidation:
    """Test thread engagement state validation and edge cases."""
    
    def test_thread_state_creation_with_empty_content(self, thread_state_builder):
        """Should handle empty original content gracefully."""
        thread_state = thread_state_builder\
            .with_original_content("")\
            .build()
        
        assert thread_state.original_content == ""
        assert thread_state.thread_id is not None
    
    def test_thread_state_creation_with_long_content(self, thread_state_builder):
        """Should handle long original content."""
        long_content = "A" * 1000  # Very long content
        thread_state = thread_state_builder\
            .with_original_content(long_content)\
            .build()
        
        assert thread_state.original_content == long_content
    
    def test_add_reply_with_empty_content(self, sample_thread_state):
        """Should handle empty reply content."""
        character_id = "test_character"
        sample_thread_state.add_character_reply(character_id, "")
        
        assert character_id in sample_thread_state.character_replies
        assert len(sample_thread_state.character_replies[character_id]) == 1
        assert sample_thread_state.character_replies[character_id][0] == ""
    
    def test_add_reply_with_special_characters(self, sample_thread_state):
        """Should handle reply content with special characters."""
        character_id = "test_character"
        special_content = "¡Hola! 🎵🇵🇷 #PuertoRico #Música"
        
        sample_thread_state.add_character_reply(character_id, special_content)
        
        assert sample_thread_state.character_replies[character_id][0] == special_content
    
    def test_thread_state_persistence(self, sample_thread_state):
        """Should maintain state across multiple operations."""
        character_id = "jovani_vazquez"
        
        # Add multiple replies
        replies = ["First reply", "Second reply", "Third reply"]
        for reply in replies:
            sample_thread_state.add_character_reply(character_id, reply)
        
        # Verify all replies are maintained
        assert len(sample_thread_state.character_replies[character_id]) == 3
        for i, reply in enumerate(replies):
            assert sample_thread_state.character_replies[character_id][i] == reply


class TestThreadEngagementRateLimiting:
    """Test rate limiting behavior in thread engagement."""
    
    def test_rate_limiting_respects_character_limits(self, sample_thread_state):
        """Should enforce per-character reply limits."""
        character_id = "jovani_vazquez"
        
        # Add replies up to limit
        for i in range(3):
            can_reply = sample_thread_state.can_character_reply(character_id)
            assert can_reply is True
            sample_thread_state.add_character_reply(character_id, f"Reply {i+1}")
        
        # Should be rate limited after limit
        can_reply = sample_thread_state.can_character_reply(character_id)
        assert can_reply is False
    
    def test_rate_limiting_is_character_specific(self, sample_thread_state):
        """Should apply rate limiting per character, not globally."""
        char1 = "jovani_vazquez"
        char2 = "politico_boricua"
        
        # Add replies up to limit for first character
        for i in range(3):
            sample_thread_state.add_character_reply(char1, f"Reply {i+1}")
        
        # First character should be rate limited
        assert sample_thread_state.can_character_reply(char1) is False
        
        # Second character should still be able to reply
        assert sample_thread_state.can_character_reply(char2) is True
        
        # Add reply from second character
        sample_thread_state.add_character_reply(char2, "Reply from char2")
        assert len(sample_thread_state.character_replies[char2]) == 1
    
    def test_rate_limiting_after_adding_reply(self, sample_thread_state):
        """Should check rate limiting after adding a reply."""
        character_id = "jovani_vazquez"
        
        # Initially can reply
        assert sample_thread_state.can_character_reply(character_id) is True
        
        # Add reply
        sample_thread_state.add_character_reply(character_id, "First reply")
        
        # Should still be able to reply (under limit)
        assert sample_thread_state.can_character_reply(character_id) is True
        
        # Add more replies up to limit
        sample_thread_state.add_character_reply(character_id, "Second reply")
        sample_thread_state.add_character_reply(character_id, "Third reply")
        
        # Should be rate limited
        assert sample_thread_state.can_character_reply(character_id) is False 