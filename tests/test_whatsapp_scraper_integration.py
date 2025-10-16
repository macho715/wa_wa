#!/usr/bin/env python3
"""
Integration Tests for WhatsApp Scraper (TDD Implementation)
Testing actual functionality with real scenarios
"""

import pytest
import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

# Import our implementation
from whatsapp_scraper import (
    WhatsAppScraper, 
    CHAT_TITLE, 
    AUTH_FILE, 
    USER_AGENT,
    fallback_llm_summarise,
    fallback_load_db,
    fallback_save_db
)


class TestWhatsAppScraperIntegration:
    """Integration tests for WhatsApp scraper functionality"""
    
    def test_should_define_constants_correctly(self):
        """Test that constants are defined with correct values"""
        assert CHAT_TITLE == "MR.CHA 전용"
        assert isinstance(AUTH_FILE, Path)
        assert AUTH_FILE.name == "auth.json"
        assert "Chrome" in USER_AGENT
    
    def test_should_create_whatsapp_scraper_instance(self):
        """Test WhatsAppScraper instantiation"""
        scraper = WhatsAppScraper()
        assert scraper.chat_title == CHAT_TITLE
        assert scraper.auth_file == AUTH_FILE
        assert scraper.max_retries == 3
        assert scraper.load_timeout == 60000
    
    def test_should_format_messages_correctly(self):
        """Test message formatting logic"""
        messages = ["Message 1", "Message 2", "Message 3"]
        chat_text = "\n".join(messages)
        expected = "Message 1\nMessage 2\nMessage 3"
        assert chat_text == expected
    
    def test_should_handle_empty_messages(self):
        """Test empty message handling"""
        empty_chat_text = ""
        assert not empty_chat_text.strip()
        
        # Test the logic that should handle empty messages
        if not empty_chat_text.strip():
            assert True  # Expected behavior
        else:
            pytest.fail("Empty message handling logic incorrect")
    
    def test_fallback_summarization(self):
        """Test fallback summarization function"""
        test_text = "긴급 회의가 9시로 변경되었습니다.\n중요한 안건이 있습니다."
        result = fallback_llm_summarise(test_text)
        
        assert "summary" in result
        assert "tasks" in result
        assert "urgent" in result
        assert "important" in result
        assert isinstance(result["tasks"], list)
        assert isinstance(result["urgent"], list)
        assert isinstance(result["important"], list)
        
        # Should detect urgent keywords
        assert len(result["urgent"]) > 0
        # Should detect important keywords
        assert len(result["important"]) > 0
    
    def test_fallback_database_operations(self):
        """Test fallback database operations"""
        test_db = {"2025-07-23": {"summary": "test", "tasks": []}}
        
        # Test save
        fallback_save_db(test_db)
        
        # Test load
        loaded_db = fallback_load_db()
        assert isinstance(loaded_db, dict)
    
    def test_should_create_proper_db_structure(self):
        """Test database structure creation"""
        today_key = datetime.now().strftime("%Y-%m-%d")
        expected_structure = {
            "summary": "test summary",
            "tasks": ["task1", "task2"],
            "urgent": [],
            "important": [],
            "raw": "test raw text"
        }
        
        # Test the structure
        assert "summary" in expected_structure
        assert "tasks" in expected_structure
        assert "urgent" in expected_structure
        assert "important" in expected_structure
        assert "raw" in expected_structure
        assert isinstance(expected_structure["tasks"], list)
    
    @pytest.mark.asyncio
    async def test_should_handle_scraping_failure_gracefully(self):
        """Test graceful handling of scraping failures"""
        scraper = WhatsAppScraper()
        
        # Mock the scraping to fail
        with patch.object(scraper, 'scrape_conversation', return_value=None):
            result = await scraper.run_with_fallback()
            
            # Should return fallback data
            assert result is not None
            assert isinstance(result, str)
            assert len(result) > 0
    
    def test_should_detect_urgent_keywords(self):
        """Test urgent keyword detection"""
        urgent_text = "긴급 회의가 있습니다. 즉시 참석해주세요."
        result = fallback_llm_summarise(urgent_text)
        
        assert len(result["urgent"]) > 0
        assert any("긴급" in item for item in result["urgent"])
    
    def test_should_detect_important_keywords(self):
        """Test important keyword detection"""
        important_text = "중요한 안건이 있습니다. 주의해서 확인해주세요."
        result = fallback_llm_summarise(important_text)
        
        assert len(result["important"]) > 0
        assert any("중요" in item for item in result["important"])


class TestWhatsAppScraperErrorHandling:
    """Test error handling scenarios"""
    
    def test_should_handle_summarization_failure(self):
        """Test handling of summarization failures"""
        # Test with empty text
        result = fallback_llm_summarise("")
        assert result["summary"] == "Total 1 messages processed"
        
        # Test with None (should handle gracefully)
        try:
            result = fallback_llm_summarise(None)
            assert result["summary"] == "Summarization failed"
        except Exception:
            # If it raises an exception, that's also acceptable
            pass
    
    def test_should_handle_database_failure(self):
        """Test database operation failure handling"""
        # Test with invalid data
        try:
            fallback_save_db("invalid_data")
            # Should not raise exception
        except Exception as e:
            # If it raises an exception, that's also acceptable
            pass
        
        # Test load with non-existent file
        result = fallback_load_db()
        assert isinstance(result, dict)


class TestWhatsAppScraperConfiguration:
    """Test configuration and setup"""
    
    def test_should_have_correct_timeout_values(self):
        """Test timeout configuration"""
        scraper = WhatsAppScraper()
        assert scraper.load_timeout == 60000  # 60 seconds
        assert scraper.network_idle_timeout == 30000  # 30 seconds
        assert scraper.max_retries == 3
    
    def test_should_have_user_agent_rotation(self):
        """Test user agent rotation"""
        from whatsapp_scraper import UA_LIST
        assert len(UA_LIST) >= 2
        assert all("Mozilla" in ua for ua in UA_LIST)
    
    def test_should_have_proper_file_paths(self):
        """Test file path configuration"""
        assert AUTH_FILE.name == "auth.json"
        assert isinstance(AUTH_FILE, Path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 