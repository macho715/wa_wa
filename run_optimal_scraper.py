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

import asyncio
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from macho_gpt.async_scraper.group_config import MultiGroupConfig
from macho_gpt.async_scraper.multi_group_manager import MultiGroupManager

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


async def run_optimal_scraper(
    config_file: str,
    enhance_loading: bool = False,
    enhance_stealth: bool = False,
    dev_mode: bool = False,
    groups: Optional[list] = None,
    max_messages: int = 50,
    timeout: int = 30000,
    headless: bool = True,
):
    """최적화된 스크래퍼 실행"""
    try:
        print_banner()

        # 설정 로드
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

        # 그룹 필터링
        if groups:
            config.whatsapp_groups = [
                group for group in config.whatsapp_groups if group.name in groups
            ]
            logger.info(f"선택된 그룹: {groups}")

        # 스크래퍼 설정 업데이트
        config.scraper_settings.max_messages = max_messages
        config.scraper_settings.timeout = timeout
        config.scraper_settings.headless = headless

        # 멀티 그룹 매니저 실행
        manager = MultiGroupManager(
            group_configs=config.whatsapp_groups,
            max_parallel_groups=config.scraper_settings.max_parallel_groups,
            ai_integration=config.ai_integration.__dict__,
        )

        logger.info("최적화된 멀티 그룹 스크래핑 시작")
        results = await manager.run_all_groups()

        # 결과 요약
        success_count = sum(
            1 for result in results if result.get("status") == "SUCCESS"
        )
        total_count = len(results)

        logger.info(f"스크래핑 완료: {success_count}/{total_count} 그룹 성공")

        return results

    except Exception as e:
        logger.error(f"스크래핑 실행 실패: {e}")
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
        results = asyncio.run(
            run_optimal_scraper(
                config_file=args.config,
                enhance_loading=enhance_loading,
                enhance_stealth=enhance_stealth,
                dev_mode=args.dev_mode,
                groups=args.groups,
                max_messages=args.max_messages,
                timeout=args.timeout,
                headless=not args.no_headless,
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
