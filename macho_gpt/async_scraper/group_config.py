"""그룹 설정 관리 모듈/Configuration loader for multi-group scraping."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import yaml  # type: ignore[import-untyped]


@dataclass(slots=True)
class GroupConfig:
    """WhatsApp 그룹 설정/Configuration for a WhatsApp group."""

    name: str
    save_file: str
    scrape_interval: int = 60
    priority: str = "MEDIUM"
    max_messages: int = 50

    def __post_init__(self) -> None:
        """설정 유효성 검증/Validate group configuration."""

        if self.scrape_interval < 10:
            raise ValueError(
                f"scrape_interval은 최소 10초 이상이어야 합니다: {self.scrape_interval}"
            )

        if self.priority not in ["HIGH", "MEDIUM", "LOW"]:
            raise ValueError(f"유효하지 않은 priority: {self.priority}")

        if self.max_messages < 1:
            raise ValueError("max_messages는 1 이상이어야 합니다")

        if not self.name or not self.save_file:
            raise ValueError("name과 save_file은 필수입니다")


@dataclass(slots=True)
class WebJSSettings:
    """whatsapp-web.js 설정/Settings for whatsapp-web.js backend."""

    script_dir: str = "setup/whatsapp_webjs"
    timeout: int = 300
    auto_install_deps: bool = True
    include_media: bool = False

    def __post_init__(self) -> None:
        """설정 유효성 검증/Validate webjs settings."""

        if self.timeout <= 0:
            raise ValueError("webjs timeout은 1초 이상이어야 합니다")


@dataclass(slots=True)
class ScraperSettings:
    """스크래퍼 전역 설정/Global scraper settings."""

    chrome_data_dir: str = "chrome-data"
    headless: bool = True
    timeout: int = 30000
    max_parallel_groups: int = 5
    backend: str = "playwright"
    webjs_fallback: bool = True
    webjs_settings: WebJSSettings = field(default_factory=WebJSSettings)

    def __post_init__(self) -> None:
        """설정 유효성 검증/Validate scraper settings."""

        if self.timeout < 5000:
            raise ValueError(f"timeout은 최소 5000ms 이상이어야 합니다: {self.timeout}")

        if self.max_parallel_groups < 1 or self.max_parallel_groups > 10:
            raise ValueError(
                "max_parallel_groups는 1~10 사이여야 합니다: "
                f"{self.max_parallel_groups}"
            )

        if self.backend not in {"playwright", "webjs", "auto"}:
            raise ValueError(f"유효하지 않은 backend 값: {self.backend}")


@dataclass(slots=True)
class AIIntegrationSettings:
    """AI 통합 설정/Settings for AI integration."""

    enabled: bool = True
    summarize_on_extraction: bool = True
    confidence_threshold: float = 0.90

    def __post_init__(self) -> None:
        """설정 유효성 검증/Validate AI settings."""

        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError(
                "confidence_threshold는 0.0~1.0 사이여야 합니다: "
                f"{self.confidence_threshold}"
            )


@dataclass(slots=True)
class MultiGroupConfig:
    """전체 멀티 그룹 설정/Complete multi-group configuration."""

    whatsapp_groups: List[GroupConfig] = field(default_factory=list)
    scraper_settings: ScraperSettings = field(default_factory=ScraperSettings)
    ai_integration: AIIntegrationSettings = field(default_factory=AIIntegrationSettings)

    @staticmethod
    def load_from_yaml(config_path: str) -> "MultiGroupConfig":
        """YAML에서 설정 로드/Load configuration from YAML."""

        config_file = Path(config_path)

        if not config_file.exists():
            raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {config_path}")

        with open(config_file, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)

        if not data:
            raise ValueError(f"빈 설정 파일입니다: {config_path}")

        groups: List[GroupConfig] = []
        for group_data in data.get("whatsapp_groups", []):
            group = GroupConfig(
                name=group_data["name"],
                save_file=group_data["save_file"],
                scrape_interval=group_data.get("scrape_interval", 60),
                priority=group_data.get("priority", "MEDIUM"),
                max_messages=group_data.get("max_messages", 50),
            )
            groups.append(group)

        if not groups:
            raise ValueError("최소 1개 이상의 WhatsApp 그룹이 필요합니다")

        scraper_data = data.get("scraper_settings", {})
        webjs_data = scraper_data.get("webjs_settings", {})
        scraper_settings = ScraperSettings(
            chrome_data_dir=scraper_data.get("chrome_data_dir", "chrome-data"),
            headless=scraper_data.get("headless", True),
            timeout=scraper_data.get("timeout", 30000),
            max_parallel_groups=scraper_data.get("max_parallel_groups", 5),
            backend=scraper_data.get("backend", "playwright"),
            webjs_fallback=scraper_data.get("webjs_fallback", True),
            webjs_settings=WebJSSettings(
                script_dir=webjs_data.get(
                    "script_dir", "setup/whatsapp_webjs"
                ),
                timeout=webjs_data.get("timeout", 300),
                auto_install_deps=webjs_data.get("auto_install_deps", True),
                include_media=webjs_data.get("include_media", False),
            ),
        )

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
        """전체 설정 유효성 검증/Validate complete configuration."""

        group_names = [g.name for g in self.whatsapp_groups]
        if len(group_names) != len(set(group_names)):
            raise ValueError("중복된 그룹 이름이 있습니다")

        save_files = [g.save_file for g in self.whatsapp_groups]
        if len(save_files) != len(set(save_files)):
            raise ValueError("중복된 save_file 경로가 있습니다")

        if len(self.whatsapp_groups) > self.scraper_settings.max_parallel_groups:
            raise ValueError(
                (
                    f"그룹 수({len(self.whatsapp_groups)})가 "
                    "max_parallel_groups("
                    f"{self.scraper_settings.max_parallel_groups})를 초과합니다"
                )
            )

        return True
