"""
비동기 단일 그룹 WhatsApp 스크래퍼
Playwright 기반 비동기 스크래핑 및 MACHO-GPT AI 통합
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from .group_config import GroupConfig
from .enhancements import LoadingOptimizer, StealthFeatures

logger = logging.getLogger(__name__)


class AsyncGroupScraper:
    """
    비동기 단일 그룹 WhatsApp 스크래퍼

    Features:
    - Playwright 기반 비동기 스크래핑
    - MACHO-GPT AI 요약 통합
    - 에러 처리 및 재시도 로직
    - 세션 영속성 지원
    """

    def __init__(
        self,
        group_config: GroupConfig,
        chrome_data_dir: str = "chrome-data",
        headless: bool = True,
        timeout: int = 30000,
        ai_integration: Optional[Dict[str, Any]] = None,
        enhancements: Optional[Dict[str, Any]] = None,
    ):
        """
        Args:
            group_config: 그룹 설정
            chrome_data_dir: Chrome 데이터 디렉토리
            headless: 헤드리스 모드 여부
            timeout: 타임아웃 (ms)
            ai_integration: AI 통합 설정
            enhancements: Enhancement 설정
        """
        self.group_config = group_config
        self.chrome_data_dir = chrome_data_dir
        self.headless = headless
        self.timeout = timeout
        self.ai_integration = ai_integration or {}
        self.enhancements = enhancements or {}

        # Enhancement 모듈 초기화
        self.loading_optimizer = LoadingOptimizer(
            debug_mode=self.enhancements.get("loading_optimizer", {}).get(
                "debug_screenshots", False
            )
        )
        self.stealth_features = StealthFeatures(
            enabled=self.enhancements.get("stealth_features", {}).get("enabled", False)
        )

        # Playwright 객체들
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

        # 상태 관리
        self.is_running = False
        self.scraped_messages = set()  # 중복 방지용

        logger.info(f"AsyncGroupScraper initialized for group: {group_config.name}")

    async def initialize(self) -> None:
        """브라우저 및 컨텍스트 초기화"""
        try:
            self.playwright = await async_playwright().start()

            # Chrome 브라우저 시작
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                ],
            )

            # 브라우저 컨텍스트 생성
            self.context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
            )

            # 새 페이지 생성
            self.page = await self.context.new_page()

            # 스텔스 설정 적용
            await self.stealth_features.apply_stealth_settings(self.context)

            # WhatsApp Web으로 이동
            await self.page.goto("https://web.whatsapp.com", wait_until="networkidle")

            logger.info(f"Browser initialized for group: {self.group_config.name}")

        except Exception as e:
            logger.error(
                f"Failed to initialize browser for {self.group_config.name}: {e}"
            )
            raise

    async def wait_for_whatsapp_login(self, timeout: int = 60) -> bool:
        """
        WhatsApp 로그인 대기

        Args:
            timeout: 대기 시간 (초)

        Returns:
            bool: 로그인 성공 여부
        """
        try:
            # CAPTCHA 확인 및 해결
            await self.stealth_features.solve_captcha_interactive(self.page)

            # 개선된 로딩 대기 사용
            success = await self.loading_optimizer.wait_for_chat_loading_enhanced(
                self.page, timeout * 1000
            )

            if success:
                logger.info(
                    f"WhatsApp login successful for group: {self.group_config.name}"
                )
                return True
            else:
                logger.warning(f"WhatsApp login failed for {self.group_config.name}")
                return False

        except Exception as e:
            logger.warning(f"WhatsApp login timeout for {self.group_config.name}: {e}")
            return False

    async def find_and_click_group(self) -> bool:
        """
        지정된 그룹 찾기 및 클릭

        Returns:
            bool: 그룹 찾기 성공 여부
        """
        try:
            # 그룹 검색
            search_box = await self.page.wait_for_selector(
                '[data-testid="chat-list-search"]'
            )
            await search_box.click()
            await search_box.fill(self.group_config.name)

            # 검색 결과에서 그룹 클릭
            group_selector = f'[title="{self.group_config.name}"]'
            await self.page.wait_for_selector(group_selector, timeout=10000)
            await self.page.click(group_selector)

            # 그룹 채팅이 로드될 때까지 대기
            await self.page.wait_for_selector(
                '[data-testid="conversation-panel-messages"]', timeout=10000
            )

            logger.info(f"Successfully opened group: {self.group_config.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to find group {self.group_config.name}: {e}")
            return False

    async def scrape_messages(self) -> List[Dict[str, Any]]:
        """
        메시지 스크래핑

        Returns:
            List[Dict]: 스크래핑된 메시지 리스트
        """
        try:
            # 메시지 컨테이너 대기
            await self.page.wait_for_selector(
                '[data-testid="conversation-panel-messages"]'
            )

            # 메시지 요소들 찾기
            message_elements = await self.page.query_selector_all(
                '[data-testid="msg-container"]'
            )

            messages = []
            for element in message_elements:
                try:
                    # 메시지 텍스트 추출
                    text_element = await element.query_selector(
                        '[data-testid="msg-text"]'
                    )
                    if text_element:
                        text = await text_element.text_content()
                        if text and text.strip():
                            # 시간 정보 추출
                            time_element = await element.query_selector(
                                '[data-testid="msg-meta"]'
                            )
                            timestamp = (
                                await time_element.text_content()
                                if time_element
                                else None
                            )

                            # 발신자 정보 추출 (그룹 채팅의 경우)
                            sender_element = await element.query_selector(
                                '[data-testid="msg-sender"]'
                            )
                            sender = (
                                await sender_element.text_content()
                                if sender_element
                                else "Unknown"
                            )

                            message_data = {
                                "text": text.strip(),
                                "sender": sender.strip() if sender else "Unknown",
                                "timestamp": timestamp.strip() if timestamp else None,
                                "scraped_at": datetime.now().isoformat(),
                                "group_name": self.group_config.name,
                            }

                            # 중복 체크
                            message_id = f"{sender}_{text}_{timestamp}"
                            if message_id not in self.scraped_messages:
                                messages.append(message_data)
                                self.scraped_messages.add(message_id)

                except Exception as e:
                    logger.warning(f"Failed to extract message: {e}")
                    continue

            logger.info(
                f"Scraped {len(messages)} new messages from {self.group_config.name}"
            )
            return messages

        except Exception as e:
            logger.error(
                f"Failed to scrape messages from {self.group_config.name}: {e}"
            )
            return []

    async def save_messages(self, messages: List[Dict[str, Any]]) -> None:
        """
        메시지를 파일에 저장

        Args:
            messages: 저장할 메시지 리스트
        """
        if not messages:
            return

        try:
            # 기존 메시지 로드
            save_path = Path(self.group_config.save_file)
            existing_messages = []

            if save_path.exists():
                with open(save_path, "r", encoding="utf-8") as f:
                    existing_messages = json.load(f)

            # 새 메시지 추가
            existing_messages.extend(messages)

            # 파일 저장
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(existing_messages, f, ensure_ascii=False, indent=2)

            logger.info(
                f"Saved {len(messages)} messages to {self.group_config.save_file}"
            )

        except Exception as e:
            logger.error(f"Failed to save messages: {e}")

    async def integrate_with_ai_summarizer(
        self, messages: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        MACHO-GPT AI 요약기와 통합

        Args:
            messages: 요약할 메시지 리스트

        Returns:
            Optional[Dict]: AI 요약 결과
        """
        if not self.ai_integration.get("enabled", False) or not messages:
            return None

        try:
            # MACHO-GPT AI 요약기 import 및 사용
            from macho_gpt.core.logi_ai_summarizer_241219 import LogiAISummarizer

            summarizer = LogiAISummarizer()

            # 메시지 텍스트만 추출
            message_texts = [msg["text"] for msg in messages if msg.get("text")]

            if message_texts:
                # AI 요약 실행
                summary = await summarizer.summarize_messages(
                    messages=message_texts,
                    group_name=self.group_config.name,
                    confidence_threshold=self.ai_integration.get(
                        "confidence_threshold", 0.90
                    ),
                )

                logger.info(f"AI summary generated for {self.group_config.name}")
                return summary

        except Exception as e:
            logger.error(f"Failed to integrate with AI summarizer: {e}")

        return None

    async def run_scraping_cycle(self) -> Dict[str, Any]:
        """
        단일 스크래핑 사이클 실행

        Returns:
            Dict: 실행 결과
        """
        result = {
            "group_name": self.group_config.name,
            "success": False,
            "messages_scraped": 0,
            "ai_summary": None,
            "error": None,
        }

        try:
            # 메시지 스크래핑
            messages = await self.scrape_messages()

            if messages:
                # 메시지 저장
                await self.save_messages(messages)

                # AI 요약 (설정된 경우)
                if self.ai_integration.get("summarize_on_extraction", False):
                    ai_summary = await self.integrate_with_ai_summarizer(messages)
                    result["ai_summary"] = ai_summary

                result["messages_scraped"] = len(messages)
                result["success"] = True

                logger.info(
                    f"Scraping cycle completed for {self.group_config.name}: {len(messages)} messages"
                )
            else:
                logger.info(f"No new messages found for {self.group_config.name}")
                result["success"] = True  # 새 메시지가 없는 것도 성공

        except Exception as e:
            logger.error(f"Scraping cycle failed for {self.group_config.name}: {e}")
            result["error"] = str(e)

        return result

    async def run(self) -> None:
        """
        메인 실행 루프
        """
        self.is_running = True

        try:
            # 브라우저 초기화
            await self.initialize()

            # WhatsApp 로그인 대기
            if not await self.wait_for_whatsapp_login():
                logger.error(
                    f"Failed to login to WhatsApp for {self.group_config.name}"
                )
                return

            # 그룹 찾기 및 클릭
            if not await self.find_and_click_group():
                logger.error(f"Failed to find group {self.group_config.name}")
                return

            # 스크래핑 루프
            while self.is_running:
                try:
                    result = await self.run_scraping_cycle()

                    if result["error"]:
                        logger.warning(
                            f"Scraping error for {self.group_config.name}: {result['error']}"
                        )

                    # 다음 사이클까지 대기
                    await asyncio.sleep(self.group_config.scrape_interval)

                except asyncio.CancelledError:
                    logger.info(f"Scraping cancelled for {self.group_config.name}")
                    break
                except Exception as e:
                    logger.error(
                        f"Unexpected error in scraping loop for {self.group_config.name}: {e}"
                    )
                    await asyncio.sleep(5)  # 오류 시 5초 대기 후 재시도

        except Exception as e:
            logger.error(f"Fatal error in scraper for {self.group_config.name}: {e}")

        finally:
            await self.close()

    async def close(self) -> None:
        """리소스 정리"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()

            self.is_running = False
            logger.info(f"Scraper closed for group: {self.group_config.name}")

        except Exception as e:
            logger.error(f"Error closing scraper for {self.group_config.name}: {e}")

    def stop(self) -> None:
        """스크래핑 중지"""
        self.is_running = False
        logger.info(f"Stop requested for group: {self.group_config.name}")


async def main():
    """CLI 실행 예제"""
    import argparse

    parser = argparse.ArgumentParser(description="Async WhatsApp Group Scraper")
    parser.add_argument("--group", required=True, help="Group name to scrape")
    parser.add_argument("--save-file", required=True, help="Save file path")
    parser.add_argument(
        "--interval", type=int, default=60, help="Scraping interval (seconds)"
    )
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")

    args = parser.parse_args()

    # 그룹 설정 생성
    group_config = GroupConfig(
        name=args.group, save_file=args.save_file, scrape_interval=args.interval
    )

    # 스크래퍼 생성 및 실행
    scraper = AsyncGroupScraper(group_config=group_config, headless=args.headless)

    try:
        await scraper.run()
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())
