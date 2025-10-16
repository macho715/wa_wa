"""
TDD 테스트: 멀티 그룹 WhatsApp 스크래퍼
Kent Beck TDD 원칙 준수: Red → Green → Refactor
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import tempfile
import yaml

# 테스트 대상 모듈 import
from macho_gpt.async_scraper.group_config import (
    GroupConfig,
    ScraperSettings,
    AIIntegrationSettings,
    MultiGroupConfig,
)
from macho_gpt.async_scraper.async_scraper import AsyncGroupScraper
from macho_gpt.async_scraper.multi_group_manager import MultiGroupManager


class TestGroupConfig:
    """GroupConfig 클래스 테스트"""

    def test_should_create_group_config_with_valid_data(self):
        """유효한 데이터로 GroupConfig 생성 테스트"""
        config = GroupConfig(
            name="Test Group",
            save_file="test.json",
            scrape_interval=60,
            priority="HIGH",
        )

        assert config.name == "Test Group"
        assert config.save_file == "test.json"
        assert config.scrape_interval == 60
        assert config.priority == "HIGH"

    def test_should_raise_error_for_invalid_scrape_interval(self):
        """잘못된 scrape_interval에 대한 오류 테스트"""
        with pytest.raises(ValueError, match="scrape_interval은 최소 10초 이상"):
            GroupConfig(
                name="Test Group", save_file="test.json", scrape_interval=5  # 10초 미만
            )

    def test_should_raise_error_for_invalid_priority(self):
        """잘못된 priority에 대한 오류 테스트"""
        with pytest.raises(ValueError, match="유효하지 않은 priority"):
            GroupConfig(name="Test Group", save_file="test.json", priority="INVALID")

    def test_should_raise_error_for_empty_name_or_save_file(self):
        """빈 name이나 save_file에 대한 오류 테스트"""
        with pytest.raises(ValueError, match="name과 save_file은 필수입니다"):
            GroupConfig(name="", save_file="test.json")

        with pytest.raises(ValueError, match="name과 save_file은 필수입니다"):
            GroupConfig(name="Test Group", save_file="")


class TestScraperSettings:
    """ScraperSettings 클래스 테스트"""

    def test_should_create_scraper_settings_with_valid_data(self):
        """유효한 데이터로 ScraperSettings 생성 테스트"""
        settings = ScraperSettings(
            chrome_data_dir="chrome-data",
            headless=True,
            timeout=30000,
            max_parallel_groups=5,
        )

        assert settings.chrome_data_dir == "chrome-data"
        assert settings.headless is True
        assert settings.timeout == 30000
        assert settings.max_parallel_groups == 5

    def test_should_raise_error_for_invalid_timeout(self):
        """잘못된 timeout에 대한 오류 테스트"""
        with pytest.raises(ValueError, match="timeout은 최소 5000ms 이상"):
            ScraperSettings(timeout=1000)  # 5000ms 미만

    def test_should_raise_error_for_invalid_max_parallel_groups(self):
        """잘못된 max_parallel_groups에 대한 오류 테스트"""
        with pytest.raises(ValueError, match="max_parallel_groups는 1~10 사이"):
            ScraperSettings(max_parallel_groups=0)  # 1 미만

        with pytest.raises(ValueError, match="max_parallel_groups는 1~10 사이"):
            ScraperSettings(max_parallel_groups=15)  # 10 초과


class TestAIIntegrationSettings:
    """AIIntegrationSettings 클래스 테스트"""

    def test_should_create_ai_settings_with_valid_data(self):
        """유효한 데이터로 AIIntegrationSettings 생성 테스트"""
        settings = AIIntegrationSettings(
            enabled=True, summarize_on_extraction=True, confidence_threshold=0.90
        )

        assert settings.enabled is True
        assert settings.summarize_on_extraction is True
        assert settings.confidence_threshold == 0.90

    def test_should_raise_error_for_invalid_confidence_threshold(self):
        """잘못된 confidence_threshold에 대한 오류 테스트"""
        with pytest.raises(ValueError, match="confidence_threshold는 0.0~1.0 사이"):
            AIIntegrationSettings(confidence_threshold=1.5)  # 1.0 초과

        with pytest.raises(ValueError, match="confidence_threshold는 0.0~1.0 사이"):
            AIIntegrationSettings(confidence_threshold=-0.1)  # 0.0 미만


class TestMultiGroupConfig:
    """MultiGroupConfig 클래스 테스트"""

    def test_should_load_config_from_yaml_file(self):
        """YAML 파일에서 설정 로드 테스트"""
        # 임시 YAML 파일 생성
        yaml_content = """
whatsapp_groups:
  - name: "Test Group 1"
    save_file: "test1.json"
    scrape_interval: 60
    priority: "HIGH"
  - name: "Test Group 2"
    save_file: "test2.json"
    scrape_interval: 120
    priority: "MEDIUM"

scraper_settings:
  chrome_data_dir: "chrome-data"
  headless: true
  timeout: 30000
  max_parallel_groups: 3

ai_integration:
  enabled: true
  summarize_on_extraction: true
  confidence_threshold: 0.90
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            temp_path = f.name

        try:
            config = MultiGroupConfig.load_from_yaml(temp_path)

            assert len(config.whatsapp_groups) == 2
            assert config.whatsapp_groups[0].name == "Test Group 1"
            assert config.whatsapp_groups[1].name == "Test Group 2"
            assert config.scraper_settings.timeout == 30000
            assert config.ai_integration.enabled is True

        finally:
            Path(temp_path).unlink()

    def test_should_raise_error_for_missing_config_file(self):
        """존재하지 않는 설정 파일에 대한 오류 테스트"""
        with pytest.raises(FileNotFoundError):
            MultiGroupConfig.load_from_yaml("nonexistent.yaml")

    def test_should_raise_error_for_empty_groups(self):
        """빈 그룹 리스트에 대한 오류 테스트"""
        yaml_content = """
whatsapp_groups: []
scraper_settings:
  chrome_data_dir: "chrome-data"
ai_integration:
  enabled: true
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            temp_path = f.name

        try:
            with pytest.raises(
                ValueError, match="최소 1개 이상의 WhatsApp 그룹이 필요합니다"
            ):
                MultiGroupConfig.load_from_yaml(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_should_validate_duplicate_group_names(self):
        """중복된 그룹 이름 검증 테스트"""
        config = MultiGroupConfig()

        # 중복된 그룹 이름 추가
        config.whatsapp_groups = [
            GroupConfig(name="Test Group", save_file="test1.json"),
            GroupConfig(name="Test Group", save_file="test2.json"),  # 중복 이름
        ]

        with pytest.raises(ValueError, match="중복된 그룹 이름이 있습니다"):
            config.validate()

    def test_should_validate_duplicate_save_files(self):
        """중복된 save_file 경로 검증 테스트"""
        config = MultiGroupConfig()

        # 중복된 save_file 추가
        config.whatsapp_groups = [
            GroupConfig(name="Group 1", save_file="test.json"),
            GroupConfig(name="Group 2", save_file="test.json"),  # 중복 파일
        ]

        with pytest.raises(ValueError, match="중복된 save_file 경로가 있습니다"):
            config.validate()

    def test_should_validate_max_parallel_groups_limit(self):
        """max_parallel_groups 제한 검증 테스트"""
        config = MultiGroupConfig()

        # 그룹 수가 max_parallel_groups를 초과하는 경우
        config.whatsapp_groups = [
            GroupConfig(name=f"Group {i}", save_file=f"test{i}.json")
            for i in range(6)  # 6개 그룹
        ]
        config.scraper_settings.max_parallel_groups = 5  # 최대 5개

        with pytest.raises(
            ValueError, match="그룹 수.*max_parallel_groups.*를 초과합니다"
        ):
            config.validate()


class TestAsyncGroupScraper:
    """AsyncGroupScraper 클래스 테스트"""

    @pytest.fixture
    def mock_group_config(self):
        """테스트용 GroupConfig 픽스처"""
        return GroupConfig(
            name="Test Group",
            save_file="test.json",
            scrape_interval=60,
            priority="HIGH",
        )

    def test_should_initialize_async_scraper(self, mock_group_config):
        """AsyncGroupScraper 초기화 테스트"""
        scraper = AsyncGroupScraper(
            group_config=mock_group_config, chrome_data_dir="chrome-data", headless=True
        )

        assert scraper.group_config.name == "Test Group"
        assert scraper.chrome_data_dir == "chrome-data"
        assert scraper.headless is True

    @pytest.mark.asyncio
    async def test_should_initialize_browser_context(self, mock_group_config):
        """브라우저 컨텍스트 초기화 테스트"""
        scraper = AsyncGroupScraper(
            group_config=mock_group_config, chrome_data_dir="chrome-data", headless=True
        )

        with patch("playwright.async_api.async_playwright") as mock_playwright:
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value.chromium.launch.return_value = (
                mock_browser
            )
            mock_browser.new_context.return_value = mock_context
            mock_context.new_page.return_value = mock_page

            await scraper.initialize()

            assert scraper.browser is not None
            assert scraper.context is not None
            assert scraper.page is not None

    @pytest.mark.asyncio
    async def test_should_scrape_messages_from_whatsapp(self, mock_group_config):
        """WhatsApp에서 메시지 스크래핑 테스트"""
        scraper = AsyncGroupScraper(
            group_config=mock_group_config, chrome_data_dir="chrome-data", headless=True
        )

        # Mock 설정
        mock_page = AsyncMock()
        mock_page.wait_for_selector.return_value = None

        # 메시지 요소들 Mock - text_content를 직접 AsyncMock으로 설정
        mock_text_element1 = AsyncMock()
        mock_text_element1.text_content = AsyncMock(return_value="Test message 1")

        mock_time_element1 = AsyncMock()
        mock_time_element1.text_content = AsyncMock(return_value="10:30")

        mock_sender_element1 = AsyncMock()
        mock_sender_element1.text_content = AsyncMock(return_value="User1")

        mock_text_element2 = AsyncMock()
        mock_text_element2.text_content = AsyncMock(return_value="Test message 2")

        mock_time_element2 = AsyncMock()
        mock_time_element2.text_content = AsyncMock(return_value="10:31")

        mock_sender_element2 = AsyncMock()
        mock_sender_element2.text_content = AsyncMock(return_value="User2")

        mock_msg1 = Mock()
        mock_msg1.query_selector.side_effect = lambda selector: {
            '[data-testid="msg-text"]': mock_text_element1,
            '[data-testid="msg-meta"]': mock_time_element1,
            '[data-testid="msg-sender"]': mock_sender_element1,
        }.get(selector, None)

        mock_msg2 = Mock()
        mock_msg2.query_selector.side_effect = lambda selector: {
            '[data-testid="msg-text"]': mock_text_element2,
            '[data-testid="msg-meta"]': mock_time_element2,
            '[data-testid="msg-sender"]': mock_sender_element2,
        }.get(selector, None)

        mock_page.query_selector_all.return_value = [mock_msg1, mock_msg2]
        scraper.page = mock_page

        messages = await scraper.scrape_messages()

        assert len(messages) == 2
        assert any("Test message 1" in msg["text"] for msg in messages)
        assert any("Test message 2" in msg["text"] for msg in messages)

    @pytest.mark.asyncio
    async def test_should_handle_scraping_errors_gracefully(self, mock_group_config):
        """스크래핑 오류 처리 테스트"""
        scraper = AsyncGroupScraper(
            group_config=mock_group_config, chrome_data_dir="chrome-data", headless=True
        )

        # Mock에서 오류 발생
        mock_page = AsyncMock()
        mock_page.wait_for_selector.side_effect = Exception("Network error")
        scraper.page = mock_page

        # 오류가 발생해도 빈 리스트를 반환해야 함
        messages = await scraper.scrape_messages()
        assert messages == []


class TestMultiGroupManager:
    """MultiGroupManager 클래스 테스트"""

    @pytest.fixture
    def mock_group_configs(self):
        """테스트용 그룹 설정 리스트 픽스처"""
        return [
            GroupConfig(name="Group 1", save_file="test1.json"),
            GroupConfig(name="Group 2", save_file="test2.json"),
            GroupConfig(name="Group 3", save_file="test3.json"),
        ]

    def test_should_initialize_multi_group_manager(self, mock_group_configs):
        """MultiGroupManager 초기화 테스트"""
        manager = MultiGroupManager(
            group_configs=mock_group_configs, max_parallel_groups=3
        )

        assert len(manager.group_configs) == 3
        assert manager.max_parallel_groups == 3
        assert len(manager.scrapers) == 0  # 아직 스크래퍼 생성 안됨

    @pytest.mark.asyncio
    async def test_should_create_individual_scrapers_per_group(
        self, mock_group_configs
    ):
        """그룹별 개별 스크래퍼 생성 테스트"""
        manager = MultiGroupManager(
            group_configs=mock_group_configs, max_parallel_groups=3
        )

        # start_all_scrapers는 실제로 스크래퍼를 생성하므로 직접 확인
        await manager.start_all_scrapers()

        assert len(manager.scrapers) == 3
        assert "Group 1" in manager.scrapers
        assert "Group 2" in manager.scrapers
        assert "Group 3" in manager.scrapers

    @pytest.mark.asyncio
    async def test_should_run_scrapers_in_parallel(self, mock_group_configs):
        """스크래퍼 병렬 실행 테스트"""
        manager = MultiGroupManager(
            group_configs=mock_group_configs, max_parallel_groups=3
        )

        # Mock _scrape_group 메서드
        async def mock_scrape_group(group_config):
            return {
                "group_name": group_config.name,
                "success": True,
                "messages_scraped": 5,
                "error": None,
            }

        manager._scrape_group = mock_scrape_group

        results = await manager.run_all_scrapers()

        assert len(results) == 3
        assert all(result["success"] for result in results)
        assert all(result["messages_scraped"] == 5 for result in results)

    @pytest.mark.asyncio
    async def test_should_handle_group_scraping_failure(self, mock_group_configs):
        """그룹 스크래핑 실패 처리 테스트"""
        manager = MultiGroupManager(
            group_configs=mock_group_configs, max_parallel_groups=3
        )

        # Mock _scrape_group 메서드 - 일부 실패
        async def mock_scrape_group(group_config):
            if group_config.name == "Group 2":
                raise Exception("Scraping failed")
            return {
                "group_name": group_config.name,
                "success": True,
                "messages_scraped": 5,
                "error": None,
            }

        manager._scrape_group = mock_scrape_group

        # 오류가 발생해도 다른 그룹은 계속 실행되어야 함
        results = await manager.run_all_scrapers()

        # 오류가 포함된 결과도 반환되어야 함
        assert len(results) == 3
        assert any("Scraping failed" in str(result) for result in results)
        assert any(result.get("success") for result in results)  # 일부는 성공

    @pytest.mark.asyncio
    async def test_should_cleanup_on_shutdown(self, mock_group_configs):
        """종료 시 정리 작업 테스트"""
        manager = MultiGroupManager(
            group_configs=mock_group_configs, max_parallel_groups=3
        )

        # Mock 스크래퍼 설정
        mock_scrapers = []
        for i in range(3):
            mock_scraper = AsyncMock()
            mock_scrapers.append(mock_scraper)

        manager.scrapers = {
            f"Group {i+1}": scraper for i, scraper in enumerate(mock_scrapers)
        }

        await manager.shutdown()

        # 모든 스크래퍼의 close 메서드가 호출되어야 함
        for scraper in mock_scrapers:
            scraper.close.assert_called_once()

        assert len(manager.scrapers) == 0


class TestIntegration:
    """통합 테스트"""

    @pytest.mark.asyncio
    async def test_should_integrate_with_ai_summarizer(self):
        """AI 요약기와 통합 테스트"""
        # 이 테스트는 실제 AI 통합이 구현된 후 작성
        pass

    def test_should_save_to_separate_files_per_group(self):
        """그룹별 별도 파일 저장 테스트"""
        # 이 테스트는 파일 저장 로직이 구현된 후 작성
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
