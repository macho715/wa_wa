"""
멀티 그룹 병렬 처리 매니저
여러 WhatsApp 그룹을 동시에 스크래핑
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import signal
import sys

from .group_config import GroupConfig, MultiGroupConfig
from .async_scraper import AsyncGroupScraper

logger = logging.getLogger(__name__)


class MultiGroupManager:
    """
    멀티 그룹 병렬 스크래핑 매니저

    Features:
    - 여러 그룹 동시 스크래핑
    - 개별 그룹별 설정
    - 통합 에러 핸들링
    - AI 요약 통합
    - Graceful shutdown
    """

    def __init__(
        self,
        group_configs: List[GroupConfig],
        max_parallel_groups: int = 5,
        ai_integration: Optional[Dict[str, Any]] = None,
    ):
        """
        Args:
            group_configs: 스크래핑할 그룹 설정 리스트
            max_parallel_groups: 최대 병렬 처리 그룹 수
            ai_integration: AI 통합 설정
        """
        self.group_configs = group_configs
        self.max_parallel_groups = min(max_parallel_groups, len(group_configs))
        self.ai_integration = ai_integration or {}

        # 스크래퍼 인스턴스들
        self.scrapers: Dict[str, AsyncGroupScraper] = {}

        # 상태 관리
        self.is_running = False
        self.tasks: List[asyncio.Task] = []

        # 통계
        self.stats = {
            "total_groups": len(group_configs),
            "active_groups": 0,
            "completed_cycles": 0,
            "total_messages": 0,
            "errors": 0,
            "start_time": None,
        }

        logger.info(f"MultiGroupManager initialized with {len(group_configs)} groups")

    def _create_scraper(self, group_config: GroupConfig) -> AsyncGroupScraper:
        """
        개별 그룹용 스크래퍼 생성

        Args:
            group_config: 그룹 설정

        Returns:
            AsyncGroupScraper: 스크래퍼 인스턴스
        """
        scraper = AsyncGroupScraper(
            group_config=group_config, ai_integration=self.ai_integration
        )

        return scraper

    async def _scrape_group(self, group_config: GroupConfig) -> Dict[str, Any]:
        """
        단일 그룹 스크래핑 (독립 태스크)

        Args:
            group_config: 그룹 설정

        Returns:
            Dict: 실행 결과
        """
        result = {
            "group_name": group_config.name,
            "success": False,
            "messages_scraped": 0,
            "ai_summary": None,
            "error": None,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
        }

        scraper = None

        try:
            # 스크래퍼 생성
            scraper = self._create_scraper(group_config)
            self.scrapers[group_config.name] = scraper

            logger.info(f"Starting scraper for group: {group_config.name}")
            self.stats["active_groups"] += 1

            # 스크래핑 실행
            await scraper.run()

            result["success"] = True
            logger.info(
                f"Scraper completed successfully for group: {group_config.name}"
            )

        except asyncio.CancelledError:
            logger.info(f"Scraper cancelled for group: {group_config.name}")
            result["error"] = "cancelled"

        except Exception as e:
            logger.error(f"Error scraping group {group_config.name}: {e}")
            result["error"] = str(e)
            self.stats["errors"] += 1

        finally:
            # 클린업
            if scraper:
                await scraper.close()

            if group_config.name in self.scrapers:
                del self.scrapers[group_config.name]

            self.stats["active_groups"] -= 1
            result["end_time"] = datetime.now().isoformat()

        return result

    async def start_all_scrapers(self) -> None:
        """모든 스크래퍼 시작"""
        logger.info(f"Starting all scrapers for {len(self.group_configs)} groups")

        for group_config in self.group_configs:
            scraper = self._create_scraper(group_config)
            self.scrapers[group_config.name] = scraper
            logger.info(f"Created scraper for group: {group_config.name}")

    async def run_all_scrapers(self) -> List[Dict[str, Any]]:
        """모든 스크래퍼 실행 (run_all_groups의 별칭)"""
        return await self.run_all_groups()

    async def run_all_groups(self) -> List[Dict[str, Any]]:
        """
        모든 그룹을 병렬로 스크래핑

        Returns:
            List[Dict]: 각 그룹의 실행 결과
        """
        logger.info(f"Starting parallel scraping for {len(self.group_configs)} groups")
        self.is_running = True
        self.stats["start_time"] = datetime.now().isoformat()

        try:
            # 모든 그룹에 대한 태스크 생성
            tasks = []
            for group_config in self.group_configs:
                task = asyncio.create_task(self._scrape_group(group_config))
                tasks.append(task)
                self.tasks.append(task)

            # 모든 태스크 병렬 실행
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 결과 처리
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append(
                        {
                            "group_name": self.group_configs[i].name,
                            "success": False,
                            "error": str(result),
                            "start_time": datetime.now().isoformat(),
                            "end_time": datetime.now().isoformat(),
                        }
                    )
                    self.stats["errors"] += 1
                else:
                    processed_results.append(result)
                    if result.get("success"):
                        self.stats["completed_cycles"] += 1
                        self.stats["total_messages"] += result.get(
                            "messages_scraped", 0
                        )

            return processed_results

        except KeyboardInterrupt:
            logger.info("Multi-group scraping interrupted by user")
            return []

        except Exception as e:
            logger.error(f"Fatal error in multi-group scraping: {e}")
            raise

        finally:
            self.is_running = False
            await self.cleanup()

    async def run_limited_parallel(self) -> List[Dict[str, Any]]:
        """
        제한된 병렬 처리로 그룹 스크래핑

        Returns:
            List[Dict]: 각 그룹의 실행 결과
        """
        logger.info(
            f"Starting limited parallel scraping (max {self.max_parallel_groups} groups)"
        )
        self.is_running = True
        self.stats["start_time"] = datetime.now().isoformat()

        results = []

        try:
            # 그룹을 배치로 나누어 처리
            for i in range(0, len(self.group_configs), self.max_parallel_groups):
                batch = self.group_configs[i : i + self.max_parallel_groups]

                logger.info(
                    f"Processing batch {i//self.max_parallel_groups + 1}: {[g.name for g in batch]}"
                )

                # 배치 내 그룹들을 병렬 처리
                batch_tasks = [
                    asyncio.create_task(self._scrape_group(group)) for group in batch
                ]
                batch_results = await asyncio.gather(
                    *batch_tasks, return_exceptions=True
                )

                # 결과 처리
                for j, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        results.append(
                            {
                                "group_name": batch[j].name,
                                "success": False,
                                "error": str(result),
                                "start_time": datetime.now().isoformat(),
                                "end_time": datetime.now().isoformat(),
                            }
                        )
                        self.stats["errors"] += 1
                    else:
                        results.append(result)
                        if result.get("success"):
                            self.stats["completed_cycles"] += 1
                            self.stats["total_messages"] += result.get(
                                "messages_scraped", 0
                            )

                # 배치 간 대기 (리소스 정리)
                if i + self.max_parallel_groups < len(self.group_configs):
                    await asyncio.sleep(2)

            return results

        except KeyboardInterrupt:
            logger.info("Limited parallel scraping interrupted by user")
            return results

        except Exception as e:
            logger.error(f"Fatal error in limited parallel scraping: {e}")
            raise

        finally:
            self.is_running = False
            await self.cleanup()

    async def stop_all(self) -> None:
        """모든 스크래퍼 중지"""
        logger.info("Stopping all scrapers...")
        self.is_running = False

        # 모든 태스크 취소
        for task in self.tasks:
            if not task.done():
                task.cancel()

        # 모든 스크래퍼 중지
        for group_name, scraper in self.scrapers.items():
            try:
                scraper.stop()
                await scraper.close()
                logger.info(f"Stopped scraper for: {group_name}")
            except Exception as e:
                logger.error(f"Error stopping scraper {group_name}: {e}")

        # 태스크 정리
        self.tasks.clear()
        self.scrapers.clear()

    async def shutdown(self) -> None:
        """시스템 종료 (cleanup의 별칭)"""
        await self.cleanup()

    async def cleanup(self) -> None:
        """리소스 정리"""
        try:
            await self.stop_all()
            logger.info("MultiGroupManager cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """현재 통계 반환"""
        current_time = datetime.now()
        if self.stats["start_time"]:
            start_time = datetime.fromisoformat(self.stats["start_time"])
            self.stats["runtime_seconds"] = (current_time - start_time).total_seconds()
        else:
            self.stats["runtime_seconds"] = 0

        return self.stats.copy()

    def get_status(self) -> Dict[str, Any]:
        """현재 상태 반환"""
        return {
            "is_running": self.is_running,
            "active_groups": len(self.scrapers),
            "total_groups": len(self.group_configs),
            "stats": self.get_stats(),
        }


async def main():
    """CLI 실행 예제"""
    import argparse
    import json
    from .group_config import MultiGroupConfig

    parser = argparse.ArgumentParser(description="Multi-Group WhatsApp Scraper")
    parser.add_argument(
        "--config", "-c", required=True, help="YAML config file with group settings"
    )
    parser.add_argument(
        "--max-parallel", type=int, default=5, help="Maximum parallel groups"
    )
    parser.add_argument(
        "--limited-parallel",
        action="store_true",
        help="Use limited parallel processing",
    )

    args = parser.parse_args()

    try:
        # 설정 로드
        config = MultiGroupConfig.load_from_yaml(args.config)
        config.validate()

        # 매니저 생성
        manager = MultiGroupManager(
            group_configs=config.whatsapp_groups,
            max_parallel_groups=args.max_parallel,
            ai_integration=config.ai_integration.__dict__,
        )

        # 시그널 핸들러 설정
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            asyncio.create_task(manager.stop_all())

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # 실행
        if args.limited_parallel:
            results = await manager.run_limited_parallel()
        else:
            results = await manager.run_all_groups()

        # 결과 출력
        print(f"\n=== Scraping Results ===")
        print(f"Total groups: {len(results)}")
        print(f"Successful: {sum(1 for r in results if r.get('success'))}")
        print(f"Failed: {sum(1 for r in results if not r.get('success'))}")
        print(f"Total messages: {sum(r.get('messages_scraped', 0) for r in results)}")

        # 통계 출력
        stats = manager.get_stats()
        print(f"\n=== Statistics ===")
        print(f"Runtime: {stats.get('runtime_seconds', 0):.2f} seconds")
        print(f"Completed cycles: {stats.get('completed_cycles', 0)}")
        print(f"Total messages: {stats.get('total_messages', 0)}")
        print(f"Errors: {stats.get('errors', 0)}")

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        if "manager" in locals():
            await manager.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
