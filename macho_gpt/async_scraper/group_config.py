from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import yaml


@dataclass
class WebJSSettings:
    """whatsapp-web.js 백엔드 설정입니다. (KR)
    whatsapp-web.js backend settings container. (EN)

    Args:
        script_dir (str): Node.js 스크립트 디렉터리입니다.
        timeout (int): 서브프로세스 실행 타임아웃(초)입니다.
        auto_install_deps (bool): 의존성 자동 설치 여부입니다.
        include_media (bool): 미디어(base64) 포함 여부입니다.
    """

    script_dir: str = "setup/whatsapp_webjs"
    timeout: int = 300
    auto_install_deps: bool = True
    include_media: bool = False

    def __post_init__(self) -> None:
        """설정 값을 검증합니다. (KR)
        Validate field values. (EN)
        """

        if self.timeout <= 0:
            raise ValueError("timeout 값은 0보다 커야 합니다")
        if not self.script_dir:
            raise ValueError("script_dir은 비워 둘 수 없습니다")


@dataclass
class GroupConfig:
    """개별 WhatsApp 그룹 설정입니다. (KR)
    Configuration for a single WhatsApp group. (EN)

    Args:
        name (str): 그룹 이름입니다.
        save_file (str): 메시지를 저장할 파일 경로입니다.
        scrape_interval (int): 스크래핑 주기(초)입니다.
        priority (str): 작업 우선순위입니다.
        max_messages (int): 그룹당 메시지 수집 상한입니다.
    """

    name: str
    save_file: str
    scrape_interval: int = 60
    priority: str = "MEDIUM"
    max_messages: int = 50

    def __post_init__(self) -> None:
        """설정의 유효성을 검사합니다. (KR)
        Validate group configuration fields. (EN)
        """
        if self.scrape_interval < 10:
            raise ValueError(
                "scrape_interval은 최소 10초 이상이어야 합니다: "
                f"{self.scrape_interval}"
            )
        if self.priority not in ["HIGH", "MEDIUM", "LOW"]:
            raise ValueError(f"유효하지 않은 priority: {self.priority}")
        if self.max_messages <= 0:
            raise ValueError("max_messages는 0보다 커야 합니다")
        if not self.name or not self.save_file:
            raise ValueError("name과 save_file은 필수입니다")


@dataclass
class ScraperSettings:
    """스크래퍼 전역 설정입니다. (KR)
    Global scraper configuration. (EN)

    Args:
        chrome_data_dir (str): Chrome 사용자 데이터 디렉터리입니다.
        headless (bool): 헤드리스 모드 사용 여부입니다.
        timeout (int): Playwright 타임아웃(ms)입니다.
        max_parallel_groups (int): 병렬 처리 가능한 최대 그룹 수입니다.
        backend (str): 사용 중인 백엔드 식별자입니다.
        webjs_fallback (bool): Playwright 실패 시 webjs로 전환 여부입니다.
        webjs_settings (WebJSSettings): webjs 관련 설정입니다.
    """

    chrome_data_dir: str = "chrome-data"
    headless: bool = True
    timeout: int = 30000
    max_parallel_groups: int = 5
    backend: str = "playwright"
    webjs_fallback: bool = True
    webjs_settings: WebJSSettings = field(default_factory=WebJSSettings)

    def __post_init__(self) -> None:
        """설정 값을 검증합니다. (KR)
        Validate scraper configuration fields. (EN)
        """

        if self.timeout < 5000:
            raise ValueError(f"timeout은 최소 5000ms 이상이어야 합니다: {self.timeout}")

        if self.max_parallel_groups < 1 or self.max_parallel_groups > 10:
            raise ValueError(
                "max_parallel_groups는 1~10 사이여야 합니다: "
                f"{self.max_parallel_groups}"
            )
        if self.backend not in {"playwright", "webjs", "auto"}:
            raise ValueError(
                "backend는 playwright, webjs, auto 중 하나여야 합니다: "
                f"{self.backend}"
            )


@dataclass
class AIIntegrationSettings:
    """AI 통합 설정입니다. (KR)
    AI integration configuration. (EN)

    Args:
        enabled (bool): AI 통합 활성화 여부입니다.
        summarize_on_extraction (bool): 메시지 추출 시 요약 여부입니다.
        confidence_threshold (float): 요약 신뢰도 임계값입니다.
    """

    enabled: bool = True
    summarize_on_extraction: bool = True
    confidence_threshold: float = 0.90

    def __post_init__(self) -> None:
        """설정 값을 검증합니다. (KR)
        Validate AI integration settings. (EN)
        """

        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError(
                "confidence_threshold는 0.0~1.0 사이여야 합니다: "
                f"{self.confidence_threshold}"
            )


@dataclass
class MultiGroupConfig:
    """멀티 그룹 스크래퍼 전체 설정입니다. (KR)
    Top-level multi-group scraper configuration. (EN)

    Args:
        whatsapp_groups (List[GroupConfig]): 대상 그룹 설정 목록입니다.
        scraper_settings (ScraperSettings): 공통 스크래퍼 설정입니다.
        ai_integration (AIIntegrationSettings): AI 통합 설정입니다.
    """

    whatsapp_groups: List[GroupConfig] = field(default_factory=list)
    scraper_settings: ScraperSettings = field(default_factory=ScraperSettings)
    ai_integration: AIIntegrationSettings = field(default_factory=AIIntegrationSettings)

    @staticmethod
    def load_from_yaml(config_path: str) -> "MultiGroupConfig":
        """YAML 설정을 로드합니다. (KR)
        Load configuration from a YAML file. (EN)"""
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
        scraper_settings = ScraperSettings(
            chrome_data_dir=scraper_data.get("chrome_data_dir", "chrome-data"),
            headless=scraper_data.get("headless", True),
            timeout=scraper_data.get("timeout", 30000),
            max_parallel_groups=scraper_data.get("max_parallel_groups", 5),
            backend=scraper_data.get("backend", "playwright"),
            webjs_fallback=scraper_data.get("webjs_fallback", True),
            webjs_settings=WebJSSettings(
                script_dir=scraper_data.get("webjs_settings", {}).get(
                    "script_dir", "setup/whatsapp_webjs"
                ),
                timeout=scraper_data.get("webjs_settings", {}).get("timeout", 300),
                auto_install_deps=scraper_data.get("webjs_settings", {}).get(
                    "auto_install_deps", True
                ),
                include_media=scraper_data.get("webjs_settings", {}).get(
                    "include_media", False
                ),
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
        """설정 전체를 검증합니다. (KR)
        Validate the entire configuration. (EN)

        Returns:
            bool: 검증 성공 여부입니다.
        """

        group_names = [group.name for group in self.whatsapp_groups]
        if len(group_names) != len(set(group_names)):
            raise ValueError("중복된 그룹 이름이 있습니다")

        save_files = [group.save_file for group in self.whatsapp_groups]
        if len(save_files) != len(set(save_files)):
            raise ValueError("중복된 save_file 경로가 있습니다")

        if len(self.whatsapp_groups) > self.scraper_settings.max_parallel_groups:
            raise ValueError(
                "그룹 수("
                f"{len(self.whatsapp_groups)}"
                ")가 max_parallel_groups("
                f"{self.scraper_settings.max_parallel_groups}"
                ")를 초과합니다"
            )

        return True
