"""
그룹 설정 관리 모듈
YAML 기반 멀티 그룹 설정 로드 및 검증
"""

from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path
import yaml


@dataclass
class GroupConfig:
    """개별 WhatsApp 그룹 설정"""

    name: str
    save_file: str
    scrape_interval: int = 60
    priority: str = "MEDIUM"

    def __post_init__(self):
        """설정 유효성 검증"""
        if self.scrape_interval < 10:
            raise ValueError(
                f"scrape_interval은 최소 10초 이상이어야 합니다: {self.scrape_interval}"
            )

        if self.priority not in ["HIGH", "MEDIUM", "LOW"]:
            raise ValueError(f"유효하지 않은 priority: {self.priority}")

        if not self.name or not self.save_file:
            raise ValueError("name과 save_file은 필수입니다")


@dataclass
class ScraperSettings:
    """스크래퍼 전역 설정"""

    chrome_data_dir: str = "chrome-data"
    headless: bool = True
    timeout: int = 30000
    max_parallel_groups: int = 5

    def __post_init__(self):
        """설정 유효성 검증"""
        if self.timeout < 5000:
            raise ValueError(f"timeout은 최소 5000ms 이상이어야 합니다: {self.timeout}")

        if self.max_parallel_groups < 1 or self.max_parallel_groups > 10:
            raise ValueError(
                f"max_parallel_groups는 1~10 사이여야 합니다: {self.max_parallel_groups}"
            )


@dataclass
class AIIntegrationSettings:
    """AI 통합 설정"""

    enabled: bool = True
    summarize_on_extraction: bool = True
    confidence_threshold: float = 0.90

    def __post_init__(self):
        """설정 유효성 검증"""
        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError(
                f"confidence_threshold는 0.0~1.0 사이여야 합니다: {self.confidence_threshold}"
            )


@dataclass
class MultiGroupConfig:
    """전체 멀티 그룹 설정"""

    whatsapp_groups: List[GroupConfig] = field(default_factory=list)
    scraper_settings: ScraperSettings = field(default_factory=ScraperSettings)
    ai_integration: AIIntegrationSettings = field(default_factory=AIIntegrationSettings)

    @staticmethod
    def load_from_yaml(config_path: str) -> "MultiGroupConfig":
        """
        YAML 파일에서 멀티 그룹 설정 로드

        Args:
            config_path: YAML 설정 파일 경로

        Returns:
            MultiGroupConfig: 로드된 설정 객체

        Raises:
            FileNotFoundError: 설정 파일이 없는 경우
            yaml.YAMLError: YAML 파싱 오류
            ValueError: 설정 검증 실패
        """
        config_file = Path(config_path)

        if not config_file.exists():
            raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {config_path}")

        with open(config_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not data:
            raise ValueError(f"빈 설정 파일입니다: {config_path}")

        # WhatsApp 그룹 파싱
        groups = []
        for group_data in data.get("whatsapp_groups", []):
            group = GroupConfig(
                name=group_data["name"],
                save_file=group_data["save_file"],
                scrape_interval=group_data.get("scrape_interval", 60),
                priority=group_data.get("priority", "MEDIUM"),
            )
            groups.append(group)

        if not groups:
            raise ValueError("최소 1개 이상의 WhatsApp 그룹이 필요합니다")

        # 스크래퍼 설정 파싱
        scraper_data = data.get("scraper_settings", {})
        scraper_settings = ScraperSettings(
            chrome_data_dir=scraper_data.get("chrome_data_dir", "chrome-data"),
            headless=scraper_data.get("headless", True),
            timeout=scraper_data.get("timeout", 30000),
            max_parallel_groups=scraper_data.get("max_parallel_groups", 5),
        )

        # AI 통합 설정 파싱
        ai_data = data.get("ai_integration", {})
        ai_integration = AIIntegrationSettings(
            enabled=ai_data.get("enabled", True),
            summarize_on_extraction=ai_data.get("summarize_on_extraction", True),
            confidence_threshold=ai_data.get("confidence_threshold", 0.90),
        )

        return MultiGroupConfig(
            whatsapp_groups=groups,
            scraper_settings=scraper_settings,
            ai_integration=ai_integration,
        )

    def validate(self) -> bool:
        """
        전체 설정 유효성 검증

        Returns:
            bool: 검증 성공 여부
        """
        # 그룹 이름 중복 체크
        group_names = [g.name for g in self.whatsapp_groups]
        if len(group_names) != len(set(group_names)):
            raise ValueError("중복된 그룹 이름이 있습니다")

        # 저장 파일 중복 체크
        save_files = [g.save_file for g in self.whatsapp_groups]
        if len(save_files) != len(set(save_files)):
            raise ValueError("중복된 save_file 경로가 있습니다")

        # 병렬 처리 수 제한 확인
        if len(self.whatsapp_groups) > self.scraper_settings.max_parallel_groups:
            raise ValueError(
                f"그룹 수({len(self.whatsapp_groups)})가 "
                f"max_parallel_groups({self.scraper_settings.max_parallel_groups})를 초과합니다"
            )

        return True
