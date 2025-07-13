"""
Tests for the news processing system and news item models.
"""
import pytest
from datetime import datetime, timezone
from app.models.conversation import NewsItem


class TestNewsItemCreation:
    """Test news item creation and basic properties."""
    
    def test_news_item_creation(self, news_item_builder):
        """Should create news item with correct properties."""
        news_item = news_item_builder\
            .with_id("test_news_001")\
            .with_headline("Test News Headline")\
            .with_content("Test news content for demonstration purposes.")\
            .with_topics(["test", "demo"])\
            .with_source("Test Source")\
            .with_relevance_score(0.8)\
            .build()
        
        assert news_item.id == "test_news_001"
        assert news_item.headline == "Test News Headline"
        assert news_item.content == "Test news content for demonstration purposes."
        assert news_item.topics == ["test", "demo"]
        assert news_item.source == "Test Source"
        assert news_item.relevance_score == 0.8
        assert news_item.published_at is not None
    
    def test_news_item_with_music_festival_data(self, news_item_builder):
        """Should create news item with music festival data."""
        news_item = news_item_builder\
            .with_id("music_festival")\
            .with_headline("New Puerto Rican Music Festival Announced")\
            .with_content("A major music festival featuring local and international artists will take place in San Juan next month.")\
            .with_topics(["music", "entertainment", "culture"])\
            .with_source("Puerto Rico Daily News")\
            .with_relevance_score(0.9)\
            .build()
        
        assert news_item.id == "music_festival"
        assert "Music Festival" in news_item.headline
        assert "music" in news_item.topics
        assert news_item.relevance_score == 0.9
    
    def test_news_item_with_traffic_data(self, news_item_builder):
        """Should create news item with traffic data."""
        news_item = news_item_builder\
            .with_id("traffic_news")\
            .with_headline("Traffic Chaos in Bayamón")\
            .with_content("Ongoing construction on Highway 22 in Bayamón is causing significant delays.")\
            .with_topics(["traffic", "construction", "bayamón"])\
            .with_source("El Nuevo Día")\
            .with_relevance_score(0.6)\
            .build()
        
        assert news_item.id == "traffic_news"
        assert "Traffic" in news_item.headline
        assert "traffic" in news_item.topics
        assert news_item.relevance_score == 0.6


class TestNewsItemValidation:
    """Test news item validation and edge cases."""
    
    def test_news_item_with_empty_content(self, news_item_builder):
        """Should handle empty content gracefully."""
        news_item = news_item_builder\
            .with_content("")\
            .build()
        
        assert news_item.content == ""
        assert news_item.id is not None
        assert news_item.headline is not None
    
    def test_news_item_with_long_content(self, news_item_builder):
        """Should handle long content."""
        long_content = "A" * 2000  # Very long content
        news_item = news_item_builder\
            .with_content(long_content)\
            .build()
        
        assert news_item.content == long_content
    
    def test_news_item_with_empty_topics(self, news_item_builder):
        """Should handle empty topics list."""
        news_item = news_item_builder\
            .with_topics([])\
            .build()
        
        assert news_item.topics == []
    
    def test_news_item_with_single_topic(self, news_item_builder):
        """Should handle single topic."""
        news_item = news_item_builder\
            .with_topics(["music"])\
            .build()
        
        assert news_item.topics == ["music"]
    
    def test_news_item_with_high_relevance_score(self, news_item_builder):
        """Should handle high relevance scores."""
        news_item = news_item_builder\
            .with_relevance_score(1.0)\
            .build()
        
        assert news_item.relevance_score == 1.0
    
    def test_news_item_with_low_relevance_score(self, news_item_builder):
        """Should handle low relevance scores."""
        news_item = news_item_builder\
            .with_relevance_score(0.1)\
            .build()
        
        assert news_item.relevance_score == 0.1
    
    def test_news_item_with_zero_relevance_score(self, news_item_builder):
        """Should handle zero relevance score."""
        news_item = news_item_builder\
            .with_relevance_score(0.0)\
            .build()
        
        assert news_item.relevance_score == 0.0


class TestNewsItemTopics:
    """Test news item topic handling and categorization."""
    
    def test_news_item_with_music_topics(self, news_item_builder):
        """Should handle music-related topics."""
        music_topics = ["music", "entertainment", "festival", "concert", "artists"]
        news_item = news_item_builder\
            .with_topics(music_topics)\
            .build()
        
        assert len(news_item.topics) == 5
        assert "music" in news_item.topics
        assert "entertainment" in news_item.topics
        assert "festival" in news_item.topics
    
    def test_news_item_with_political_topics(self, news_item_builder):
        """Should handle political topics."""
        political_topics = ["politics", "government", "policy", "election", "democracy"]
        news_item = news_item_builder\
            .with_topics(political_topics)\
            .build()
        
        assert len(news_item.topics) == 5
        assert "politics" in news_item.topics
        assert "government" in news_item.topics
    
    def test_news_item_with_cultural_topics(self, news_item_builder):
        """Should handle cultural topics."""
        cultural_topics = ["culture", "history", "heritage", "tradition", "art"]
        news_item = news_item_builder\
            .with_topics(cultural_topics)\
            .build()
        
        assert len(news_item.topics) == 5
        assert "culture" in news_item.topics
        assert "history" in news_item.topics
    
    def test_news_item_with_daily_life_topics(self, news_item_builder):
        """Should handle daily life topics."""
        daily_topics = ["daily life", "community", "local", "family", "health"]
        news_item = news_item_builder\
            .with_topics(daily_topics)\
            .build()
        
        assert len(news_item.topics) == 5
        assert "daily life" in news_item.topics
        assert "community" in news_item.topics
    
    def test_news_item_with_duplicate_topics(self, news_item_builder):
        """Should handle duplicate topics gracefully."""
        duplicate_topics = ["music", "music", "entertainment", "entertainment"]
        news_item = news_item_builder\
            .with_topics(duplicate_topics)\
            .build()
        
        # Should preserve duplicates as they might be intentional
        assert len(news_item.topics) == 4
        assert news_item.topics.count("music") == 2
        assert news_item.topics.count("entertainment") == 2


class TestNewsItemRelevanceScoring:
    """Test news item relevance scoring and categorization."""
    
    def test_high_relevance_news_item(self, news_item_builder):
        """Should handle high relevance news items."""
        news_item = news_item_builder\
            .with_relevance_score(0.9)\
            .with_headline("Breaking: Major Event in Puerto Rico")\
            .build()
        
        assert news_item.relevance_score >= 0.8
        assert "Breaking" in news_item.headline
    
    def test_medium_relevance_news_item(self, news_item_builder):
        """Should handle medium relevance news items."""
        news_item = news_item_builder\
            .with_relevance_score(0.6)\
            .with_headline("Local Traffic Update in Bayamón")\
            .build()
        
        assert 0.4 <= news_item.relevance_score <= 0.7
    
    def test_low_relevance_news_item(self, news_item_builder):
        """Should handle low relevance news items."""
        news_item = news_item_builder\
            .with_relevance_score(0.2)\
            .with_headline("Minor Update on Local Weather")\
            .build()
        
        assert news_item.relevance_score <= 0.3
    
    def test_relevance_score_bounds(self, news_item_builder):
        """Should handle relevance scores within valid bounds."""
        # Test minimum bound
        min_news = news_item_builder\
            .with_relevance_score(0.0)\
            .build()
        assert min_news.relevance_score >= 0.0
        
        # Test maximum bound
        max_news = news_item_builder\
            .with_relevance_score(1.0)\
            .build()
        assert max_news.relevance_score <= 1.0


class TestNewsItemSources:
    """Test news item source handling."""
    
    def test_news_item_with_puerto_rico_sources(self, news_item_builder):
        """Should handle Puerto Rico news sources."""
        pr_sources = [
            "Puerto Rico Daily News",
            "El Nuevo Día",
            "Caribbean Business",
            "Primera Hora"
        ]
        
        for source in pr_sources:
            news_item = news_item_builder\
                .with_source(source)\
                .build()
            assert news_item.source == source
    
    def test_news_item_with_international_sources(self, news_item_builder):
        """Should handle international news sources."""
        intl_sources = [
            "Reuters",
            "Associated Press",
            "BBC News",
            "CNN"
        ]
        
        for source in intl_sources:
            news_item = news_item_builder\
                .with_source(source)\
                .build()
            assert news_item.source == source
    
    def test_news_item_with_empty_source(self, news_item_builder):
        """Should handle empty source."""
        news_item = news_item_builder\
            .with_source("")\
            .build()
        
        assert news_item.source == ""


class TestNewsItemTimestamps:
    """Test news item timestamp handling."""
    
    def test_news_item_has_timestamp(self, news_item_builder):
        """Should have a timestamp when created."""
        news_item = news_item_builder.build()
        
        assert news_item.published_at is not None
        assert isinstance(news_item.published_at, datetime)
    
    def test_news_item_timestamp_is_recent(self, news_item_builder):
        """Should have a recent timestamp."""
        news_item = news_item_builder.build()
        
        now = datetime.now(timezone.utc)
        time_diff = abs((now - news_item.published_at).total_seconds())
        
        # Should be within the last minute
        assert time_diff < 60


class TestSampleNewsItems:
    """Test the sample news items fixture."""
    
    def test_sample_news_items_structure(self, sample_news_items):
        """Should have correct structure for sample news items."""
        assert len(sample_news_items) == 3
        
        for news_item in sample_news_items:
            assert news_item.id is not None
            assert news_item.headline is not None
            assert news_item.content is not None
            assert isinstance(news_item.topics, list)
            assert news_item.source is not None
            assert 0 <= news_item.relevance_score <= 1
    
    def test_sample_news_items_have_different_topics(self, sample_news_items):
        """Should have different topics for different news items."""
        all_topics = []
        for news_item in sample_news_items:
            all_topics.extend(news_item.topics)
        
        # Should have variety in topics
        unique_topics = set(all_topics)
        assert len(unique_topics) > 5  # Should have several different topics
    
    def test_sample_news_items_have_different_relevance_scores(self, sample_news_items):
        """Should have different relevance scores."""
        scores = [news.relevance_score for news in sample_news_items]
        
        # Should have some variation in relevance scores
        assert len(set(scores)) > 1 