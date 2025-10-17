#!/usr/bin/env python3
"""
MACHO-GPT v3.5-optimal Multi-Group WhatsApp Scraper CLI
최적 조합: 검증된 성공 시스템 + Enhancement 통합

Features:
- Tier 1: 검증된 Core System (2025-07-25 성공 데이터 기반)
- Tier 2: Enhancement Layer (로딩 안정성 + 스텔스 기능)
- Tier 3: Development Tools (디버깅, 모니터링)
- Tier 4: Setup & Backup (인증, 대안 방법)
"""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from macho_gpt.async_scraper.group_config import (  # noqa: E402
    GroupConfig,
    MultiGroupConfig,
    WebJSSettings,
)
from macho_gpt.async_scraper.multi_group_manager import MultiGroupManager  # noqa: E402
from setup.whatsapp_webjs.whatsapp_webjs_bridge import (  # noqa: E402
    BridgeResult,
    WhatsAppWebJSBridge,
)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/optimal_scraper.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)

BACKEND_PLAYWRIGHT = "playwright"
BACKEND_WEBJS = "webjs"
BACKEND_AUTO = "auto"


def print_banner():
    """배너 출력"""
    banner = """
================================================================================

         MACHO-GPT v3.5-optimal Multi-Group WhatsApp Scraper

     Samsung C&T Logistics · HVDC Project · ADNOC·DSV Partnership

                    최적 조합: 성공 시스템 + Enhancement

================================================================================
    """
    print(banner)


def print_usage():
    """사용법 출력"""
    usage = """
MACHO-GPT v3.5-optimal Multi-Group WhatsApp Scraper

기본 사용법:
  python run_optimal_scraper.py

Enhancement 활성화:
  python run_optimal_scraper.py --enhance-loading
  python run_optimal_scraper.py --enhance-stealth
  python run_optimal_scraper.py --enhance-all

개발 도구:
  python tools/dom_analyzer.py
  python tools/quick_test.py
  python tools/status_monitor.py

자세한 내용은 docs/OPTIMAL_SYSTEM_FINAL.md 참조
    """
    print(usage)
    return usage


async def run_development_tool(tool_name: str):
    """개발 도구 실행"""
    try:
        if tool_name == "dom-analyzer":
            from tools.dom_analyzer import main

            await main()
        elif tool_name == "status-check":
            from tools.status_monitor import main

            await main()
        elif tool_name == "quick-test":
            from tools.quick_test import main

            await main()
        else:
            print(f"알 수 없는 도구: {tool_name}")
            print("사용 가능한 도구: dom-analyzer, status-check, quick-test")
    except Exception as e:
        logger.error(f"개발 도구 실행 실패: {e}")


async def run_setup_tool(setup_name: str):
    """설정 도구 실행"""
    try:
        if setup_name == "manual-auth":
            from setup.manual_auth import main

            await main()
        elif setup_name == "alternative":
            from setup.alternative_methods import main

            await main()
        else:
            print(f"알 수 없는 설정 도구: {setup_name}")
            print("사용 가능한 도구: manual-auth, alternative")
    except Exception as e:
        logger.error(f"설정 도구 실행 실패: {e}")


def _log_backend_switch(from_backend: str, to_backend: str, reason: str) -> None:
    """백엔드 전환을 로깅합니다. (KR)
    Log backend switch details. (EN)
    """

    logger.warning(
        "백엔드를 %s에서 %s로 전환합니다: %s", from_backend, to_backend, reason
    )


async def run_playwright_backend(
    config: MultiGroupConfig, group_configs: List[GroupConfig]
) -> List[Dict[str, Any]]:
    """Playwright 백엔드를 실행합니다. (KR)
    Execute the Playwright backend. (EN)
    """

    manager = MultiGroupManager(
        group_configs=group_configs,
        max_parallel_groups=config.scraper_settings.max_parallel_groups,
        ai_integration=config.ai_integration.__dict__,
    )
    logger.info("Playwright 백엔드로 %d개 그룹을 스크래핑합니다.", len(group_configs))
    return await manager.run_all_groups()


async def run_webjs_backend(
    group_configs: List[GroupConfig],
    settings: WebJSSettings,
    *,
    max_messages: int,
) -> List[Dict[str, Any]]:
    """whatsapp-web.js 백엔드를 실행합니다. (KR)
    Execute the whatsapp-web.js backend. (EN)
    """

    bridge = WhatsAppWebJSBridge(settings)
    results: List[Dict[str, Any]] = []
    for group_config in group_configs:
        group_config.max_messages = max_messages
        bridge_result: BridgeResult = await bridge.scrape_group(
            group_config, max_messages=max_messages
        )
        if bridge_result.success and bridge_result.messages is not None:
            save_path = Path(group_config.save_file)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "w", encoding="utf-8") as handle:
                json.dump(bridge_result.messages, handle, ensure_ascii=False, indent=2)
            logger.info(
                "webjs 백엔드가 %s 그룹 메시지 %d건을 저장했습니다.",
                group_config.name,
                bridge_result.messages_scraped,
            )
        else:
            logger.error(
                "webjs 백엔드에서 %s 그룹 스크래핑 실패: %s",
                group_config.name,
                bridge_result.error,
            )
        results.append(
            {
                "group_name": bridge_result.group_name,
                "success": bridge_result.success,
                "messages_scraped": bridge_result.messages_scraped,
                "ai_summary": None,
                "error": bridge_result.error,
                "backend": BACKEND_WEBJS,
            }
        )
    return results


async def run_optimal_scraper(
    config_file: str,
    enhance_loading: bool = False,
    enhance_stealth: bool = False,
    dev_mode: bool = False,
    groups: Optional[List[str]] = None,
    max_messages: int = 50,
    timeout: int = 30000,
    headless: bool = True,
    backend: Optional[str] = None,
    webjs_fallback: Optional[bool] = None,
) -> List[Dict[str, Any]]:
    """최적화된 스크래퍼를 실행합니다. (KR)
    Run the optimal multi-group scraper. (EN)
    """

    try:
        print_banner()
        config = MultiGroupConfig.load_from_yaml(config_file)

        # Enhancement 설정 적용
        if enhance_loading:
            logger.info("로딩 안정성 개선 활성화")
            # 로딩 최적화 설정 적용

        if enhance_stealth:
            logger.info("스텔스 기능 활성화")
            # 스텔스 기능 설정 적용

        if dev_mode:
            logger.info("개발 모드 활성화")
            # 디버그 모드 설정 적용

        selected_groups = config.whatsapp_groups
        if groups:
            selected_groups = [
                group for group in config.whatsapp_groups if group.name in groups
            ]
            logger.info("선택된 그룹: %s", groups)
        if not selected_groups:
            raise ValueError("스크래핑할 그룹이 없습니다")

        for group_config in selected_groups:
            group_config.max_messages = max_messages

        config.scraper_settings.timeout = timeout
        config.scraper_settings.headless = headless
        config.scraper_settings.max_messages = max_messages

        configured_backend = backend or config.scraper_settings.backend
        config.scraper_settings.backend = configured_backend
        fallback_enabled = (
            webjs_fallback
            if webjs_fallback is not None
            else config.scraper_settings.webjs_fallback
        )

        if configured_backend == BACKEND_AUTO:
            fallback_enabled = True
            primary_backend = BACKEND_PLAYWRIGHT
        else:
            primary_backend = configured_backend

        results: List[Dict[str, Any]] = []

        if primary_backend == BACKEND_WEBJS:
            results = await run_webjs_backend(
                selected_groups,
                config.scraper_settings.webjs_settings,
                max_messages=max_messages,
            )
        elif primary_backend == BACKEND_PLAYWRIGHT:
            try:
                results = await run_playwright_backend(config, selected_groups)
            except Exception as exc:
                if fallback_enabled:
                    _log_backend_switch(BACKEND_PLAYWRIGHT, BACKEND_WEBJS, str(exc))
                    results = await run_webjs_backend(
                        selected_groups,
                        config.scraper_settings.webjs_settings,
                        max_messages=max_messages,
                    )
                else:
                    raise
            else:
                for result in results:
                    result["backend"] = BACKEND_PLAYWRIGHT
                if fallback_enabled:
                    failed_group_names = {
                        result.get("group_name")
                        for result in results
                        if not result.get("success", False)
                    }
                    if failed_group_names:
                        fallback_groups = [
                            group
                            for group in selected_groups
                            if group.name in failed_group_names
                        ]
                        _log_backend_switch(
                            BACKEND_PLAYWRIGHT,
                            BACKEND_WEBJS,
                            "Playwright 실패 그룹 감지",
                        )
                        fallback_results = await run_webjs_backend(
                            fallback_groups,
                            config.scraper_settings.webjs_settings,
                            max_messages=max_messages,
                        )
                        for fallback_result in fallback_results:
                            for idx, original in enumerate(results):
                                if original.get("group_name") == fallback_result.get(
                                    "group_name"
                                ):
                                    results[idx] = fallback_result
                                    break
                            else:
                                results.append(fallback_result)
        else:
            raise ValueError(f"지원하지 않는 백엔드입니다: {configured_backend}")

        success_count = sum(1 for result in results if result.get("success", False))
        logger.info("스크래핑 완료: %d/%d 그룹 성공", success_count, len(results))
        return results

    except Exception as error:
        logger.error(f"스크래핑 실행 실패: {error}")
        raise


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="MACHO-GPT v3.5-optimal Multi-Group WhatsApp Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=print_usage(),
    )

    # 기본 옵션
    parser.add_argument(
        "--config",
        default="configs/optimal_multi_group_config.yaml",
        help="설정 파일 경로",
    )

    # Enhancement 옵션
    parser.add_argument(
        "--enhance-loading", action="store_true", help="로딩 안정성 개선 활성화"
    )

    parser.add_argument(
        "--enhance-stealth", action="store_true", help="스텔스 기능 활성화"
    )

    parser.add_argument(
        "--enhance-all", action="store_true", help="모든 Enhancement 활성화"
    )

    # 개발 옵션
    parser.add_argument(
        "--dev-mode", action="store_true", help="개발 모드 (디버깅, 스크린샷 등)"
    )

    parser.add_argument(
        "--tool",
        choices=["dom-analyzer", "status-check", "quick-test"],
        help="개발 도구 실행",
    )

    parser.add_argument(
        "--setup", choices=["manual-auth", "alternative"], help="설정 도구 실행"
    )

    # 백엔드 옵션 (whatsapp-web.js 통합)
    parser.add_argument(
        "--backend",
        choices=[BACKEND_PLAYWRIGHT, BACKEND_WEBJS, BACKEND_AUTO],
        default=None,
        help="스크래핑 백엔드 선택 (기본: 설정 파일)",
    )

    parser.add_argument(
        "--webjs-fallback",
        dest="webjs_fallback",
        action="store_true",
        help="Playwright 실패 시 whatsapp-web.js로 자동 전환",
    )
    parser.add_argument(
        "--no-webjs-fallback",
        dest="webjs_fallback",
        action="store_false",
        help="Playwright 실패 시에도 webjs로 전환하지 않음",
    )
    parser.set_defaults(webjs_fallback=None)

    # 스크래핑 옵션
    parser.add_argument("--groups", nargs="+", help="스크래핑할 그룹 이름들")

    parser.add_argument("--max-messages", type=int, default=50, help="최대 메시지 수")

    parser.add_argument("--timeout", type=int, default=30000, help="타임아웃 (밀리초)")

    parser.add_argument(
        "--no-headless", action="store_true", help="헤드리스 모드 비활성화"
    )

    args = parser.parse_args()

    # Enhancement 설정
    enhance_loading = args.enhance_loading or args.enhance_all
    enhance_stealth = args.enhance_stealth or args.enhance_all

    # 개발 도구 실행
    if args.tool:
        asyncio.run(run_development_tool(args.tool))
        return

    # 설정 도구 실행
    if args.setup:
        asyncio.run(run_setup_tool(args.setup))
        return

    # 스크래퍼 실행
    try:
        asyncio.run(
            run_optimal_scraper(
                config_file=args.config,
                enhance_loading=enhance_loading,
                enhance_stealth=enhance_stealth,
                dev_mode=args.dev_mode,
                groups=args.groups,
                max_messages=args.max_messages,
                timeout=args.timeout,
                headless=not args.no_headless,
                backend=args.backend,
                webjs_fallback=args.webjs_fallback,
            )
        )

        print("\n" + "=" * 60)
        print("스크래핑 완료!")
        print("=" * 60)

    except KeyboardInterrupt:
        logger.info("사용자에 의해 중단됨")
    except Exception as e:
        logger.error(f"실행 중 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
