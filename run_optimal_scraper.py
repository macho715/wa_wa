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
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from macho_gpt.async_scraper.group_config import (
    GroupConfig,  # noqa: E402
    MultiGroupConfig,
)
from macho_gpt.async_scraper.multi_group_manager import MultiGroupManager  # noqa: E402
from setup.whatsapp_webjs.whatsapp_webjs_bridge import WhatsAppWebJSBridge  # noqa: E402

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, ValueError, OSError):
    pass

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


def print_banner() -> None:
    """배너 출력/Print CLI banner."""
    banner = """
================================================================================

         MACHO-GPT v3.5-optimal Multi-Group WhatsApp Scraper

     Samsung C&T Logistics · HVDC Project · ADNOC·DSV Partnership

                    최적 조합: 성공 시스템 + Enhancement

================================================================================
    """
    print(banner)


def print_usage() -> str:
    """사용법 출력/Print usage text."""
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


async def run_development_tool(tool_name: str) -> None:
    """개발 도구 실행/Run a development tool."""
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


async def run_setup_tool(setup_name: str) -> None:
    """설정 도구 실행/Run a setup helper tool."""
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


<<<<<<< HEAD
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
    include_media: bool = False,
) -> List[Dict[str, Any]]:
    """whatsapp-web.js 백엔드를 실행합니다. (KR)
    Execute the whatsapp-web.js backend. (EN)
    """

=======
def _select_groups(
    config: MultiGroupConfig, names: Optional[Sequence[str]]
) -> List[GroupConfig]:
    """그룹 선택/Select groups based on CLI filters."""

    if not names:
        return list(config.whatsapp_groups)

    selected = [group for group in config.whatsapp_groups if group.name in names]
    if not selected:
        available = ", ".join(group.name for group in config.whatsapp_groups)
        raise ValueError(
            f"선택된 그룹이 없습니다. 사용 가능한 그룹: {available or '없음'}"
        )
    return selected


def _resolve_backend_sequence(selected: str, fallback: bool) -> List[str]:
    """백엔드 실행 순서 계산/Resolve backend execution order."""

    if selected == "auto":
        return ["playwright", "webjs"] if fallback else ["playwright"]

    if selected == "playwright":
        return ["playwright", "webjs"] if fallback else ["playwright"]

    return ["webjs"]


def _persist_webjs_group(
    group_payload: Dict[str, Any], group_config: GroupConfig
) -> None:
    """webjs 결과 저장/Persist whatsapp-web.js group payload."""

    target_path = Path(group_config.save_file)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "status": "SUCCESS",
        "backend": "webjs",
        "saved_at": datetime.utcnow().isoformat(),
        "group": group_payload,
    }

    with open(target_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


async def _run_playwright_backend(
    config: MultiGroupConfig,
    groups: List[GroupConfig],
    *,
    enhance_loading: bool,
    enhance_stealth: bool,
    max_messages: int,
    timeout: int,
    headless: bool,
) -> List[Dict[str, Any]]:
    """Playwright 백엔드 실행/Run the Playwright backend."""

    config.scraper_settings.headless = headless
    config.scraper_settings.timeout = timeout

    if enhance_loading:
        logger.info("Playwright loading enhancement enabled")
    if enhance_stealth:
        logger.info("Playwright stealth enhancement enabled")

    for group in groups:
        group.max_messages = min(group.max_messages, max_messages)

    manager = MultiGroupManager(
        group_configs=groups,
        max_parallel_groups=config.scraper_settings.max_parallel_groups,
        ai_integration=config.ai_integration.__dict__,
        chrome_data_root=config.scraper_settings.chrome_data_dir,
        headless=config.scraper_settings.headless,
        timeout=config.scraper_settings.timeout,
        enhancements=getattr(config, "enhancements", {}),
    )

    logger.info("Playwright backend starting for %d groups", len(groups))
    results = await manager.run_all_groups()
    logger.info("Playwright backend completed")
    return results


async def _run_webjs_backend(
    config: MultiGroupConfig,
    groups: List[GroupConfig],
    *,
    max_messages: int,
    include_media: bool,
) -> List[Dict[str, Any]]:
    """whatsapp-web.js 백엔드 실행/Run the whatsapp-web.js backend."""

    if not groups:
        raise ValueError("whatsapp-web.js 백엔드에 사용할 그룹이 없습니다")

    settings = config.scraper_settings.webjs_settings
>>>>>>> origin/codex/integrate-playwright-with-whatsapp-web.js
    bridge = WhatsAppWebJSBridge(
        script_dir=settings.script_dir,
        timeout=settings.timeout,
        auto_install_deps=settings.auto_install_deps,
    )
<<<<<<< HEAD
    results: List[Dict[str, Any]] = []
    for group_config in group_configs:
        group_config.max_messages = max_messages
        bridge_result = await bridge.scrape_group(
            group_config.name, limit=max_messages, include_media=include_media
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
=======

    include_media_flag = include_media or settings.include_media
    limit_map = {group.name: min(group.max_messages, max_messages) for group in groups}
    latest_results: Dict[str, Dict[str, Any]] = {}
    loop = asyncio.get_running_loop()
    last_scrape = {
        group.name: loop.time() - max(group.scrape_interval, 1) for group in groups
    }

    logger.info("whatsapp-web.js backend polling started for %d groups", len(groups))

    try:
        while True:
            now = loop.time()
            due_groups = [
                group
                for group in groups
                if now - last_scrape[group.name] >= group.scrape_interval
            ]

            if not due_groups:
                await asyncio.sleep(1)
                continue

            group_names = [group.name for group in due_groups]
            group_limits = {name: limit_map[name] for name in group_names}
            global_limit = max(group_limits.values())

            result = await bridge.scrape_groups(
                group_names,
                limit=global_limit,
                include_media=include_media_flag,
                group_limits=group_limits,
            )

            status = result.get("status", "UNKNOWN")
            if status != "SUCCESS":
                logger.warning("whatsapp-web.js returned status %s", status)

            for error in result.get("errors", []):
                logger.warning(
                    "webjs error for group %s: %s",
                    error.get("group"),
                    error.get("reason"),
                )

            group_lookup = {group.name: group for group in groups}
            scrape_completed = loop.time()

            for group_payload in result.get("groups", []):
                name = group_payload.get("name")
                group_config = group_lookup.get(name)
                if not group_config:
                    continue

                _persist_webjs_group(group_payload, group_config)
                latest_results[name] = {
                    "group_name": name,
                    "success": True,
                    "messages_scraped": len(group_payload.get("messages", [])),
                    "backend": "webjs",
                    "saved_at": datetime.utcnow().isoformat(),
                }
                last_scrape[name] = scrape_completed

            await asyncio.sleep(0)
    except asyncio.CancelledError:
        logger.info("whatsapp-web.js backend cancelled")
        raise
    except Exception as exc:  # pragma: no cover - safety net for runtime errors
        logger.exception("whatsapp-web.js backend failed: %s", exc)
        raise

    return list(latest_results.values())
>>>>>>> origin/codex/integrate-playwright-with-whatsapp-web.js


async def run_optimal_scraper(
    config_file: str,
    enhance_loading: bool = False,
    enhance_stealth: bool = False,
    dev_mode: bool = False,
<<<<<<< HEAD
    groups: Optional[List[str]] = None,
=======
    groups: Optional[Sequence[str]] = None,
>>>>>>> origin/codex/integrate-playwright-with-whatsapp-web.js
    max_messages: int = 50,
    timeout: int = 30000,
    headless: bool = True,
    backend: Optional[str] = None,
    webjs_fallback: Optional[bool] = None,
    include_media: bool = False,
) -> List[Dict[str, Any]]:
<<<<<<< HEAD
    """최적화된 스크래퍼를 실행합니다. (KR)
    Run the optimal multi-group scraper. (EN)
    """

    try:
        print_banner()
        config = MultiGroupConfig.load_from_yaml(config_file)
=======
    """최적화된 스크래퍼 실행/Run the optimal scraper."""

    print_banner()
>>>>>>> origin/codex/integrate-playwright-with-whatsapp-web.js

    config = MultiGroupConfig.load_from_yaml(config_file)
    selected_groups = _select_groups(config, groups)

    if enhance_loading:
        logger.info("로딩 안정성 개선 활성화")

    if enhance_stealth:
        logger.info("스텔스 기능 활성화")

<<<<<<< HEAD
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
                include_media=include_media,
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
                        include_media=include_media,
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
                            include_media=include_media,
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
=======
    if dev_mode:
        logger.info("개발 모드 활성화")

    chosen_backend = backend or config.scraper_settings.backend
    fallback_enabled = (
        webjs_fallback
        if webjs_fallback is not None
        else config.scraper_settings.webjs_fallback
    )
    backend_sequence = _resolve_backend_sequence(chosen_backend, fallback_enabled)
    logger.info("Backend sequence: %s", " -> ".join(backend_sequence))

    last_error: Optional[Exception] = None
    for backend_name in backend_sequence:
        try:
            if backend_name == "playwright":
                return await _run_playwright_backend(
                    config,
                    selected_groups,
                    enhance_loading=enhance_loading,
                    enhance_stealth=enhance_stealth,
                    max_messages=max_messages,
                    timeout=timeout,
                    headless=headless,
                )
            if backend_name == "webjs":
                return await _run_webjs_backend(
                    config,
                    selected_groups,
                    max_messages=max_messages,
                    include_media=include_media,
                )
            raise ValueError(f"Unsupported backend requested: {backend_name}")
        except Exception as exc:
            logger.exception("Backend %s failed: %s", backend_name, exc)
            last_error = exc
            continue

    if last_error:
        raise last_error

    raise RuntimeError("No backend executed")
>>>>>>> origin/codex/integrate-playwright-with-whatsapp-web.js


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
<<<<<<< HEAD
        choices=[BACKEND_PLAYWRIGHT, BACKEND_WEBJS, BACKEND_AUTO],
=======
        choices=["playwright", "webjs", "auto"],
>>>>>>> origin/codex/integrate-playwright-with-whatsapp-web.js
        default=None,
        help="스크래핑 백엔드 선택 (기본: 설정 파일)",
    )

    parser.add_argument(
        "--webjs-fallback",
        dest="webjs_fallback",
<<<<<<< HEAD
        action="store_true",
=======
        action="store_const",
        const=True,
        default=None,
>>>>>>> origin/codex/integrate-playwright-with-whatsapp-web.js
        help="Playwright 실패 시 whatsapp-web.js로 자동 전환",
    )
    parser.add_argument(
        "--no-webjs-fallback",
        dest="webjs_fallback",
        action="store_false",
        help="Playwright 실패 시에도 webjs로 전환하지 않음",
    )
    parser.set_defaults(webjs_fallback=None)

    parser.add_argument(
        "--no-webjs-fallback",
        dest="webjs_fallback",
        action="store_const",
        const=False,
        help="Playwright 실패 시에도 whatsapp-web.js로 전환하지 않음",
    )

    # 스크래핑 옵션
    parser.add_argument("--groups", nargs="+", help="스크래핑할 그룹 이름들")

    parser.add_argument("--max-messages", type=int, default=50, help="최대 메시지 수")

    parser.add_argument(
        "--webjs-include-media",
        dest="include_media",
        action="store_true",
        help="whatsapp-web.js에서 미디어(base64) 포함",
    )

    parser.add_argument("--timeout", type=int, default=30000, help="타임아웃 (밀리초)")

    parser.add_argument(
        "--webjs-include-media",
        dest="include_media",
        action="store_true",
        help="whatsapp-web.js에서 미디어(base64) 포함",
    )

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
                include_media=args.include_media,
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
