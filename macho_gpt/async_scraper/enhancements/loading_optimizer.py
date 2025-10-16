"""
로딩 안정성 개선 모듈
extract_whatsapp_loadfix.py에서 추출한 개선사항들을 통합
"""

import asyncio
import random
import logging
from typing import List, Optional
from playwright.async_api import Page

logger = logging.getLogger(__name__)


class LoadingOptimizer:
    """로딩 안정성 개선 클래스"""

    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.network_idle_timeout = 30000  # 30초
        self.load_timeout = 60000  # 60초

    async def wait_for_chat_loading_enhanced(
        self, page: Page, timeout: int = 30000
    ) -> bool:
        """
        개선된 채팅 로딩 대기

        Args:
            page: Playwright Page 객체
            timeout: 타임아웃 (밀리초)

        Returns:
            bool: 로딩 성공 여부
        """
        try:
            logger.info("채팅방 로딩 대기 중...")

            # 1. 네트워크 유휴 대기
            try:
                await page.wait_for_load_state(
                    "networkidle", timeout=self.network_idle_timeout
                )
                logger.info("네트워크 유휴 상태 확인")
            except Exception as e:
                logger.warning(f"네트워크 유휴 대기 실패: {e}")

            # 2. 다중 셀렉터 백업 전략
            selectors = [
                '[data-testid="chat-list"]',
                '[data-testid="conversation-panel"]',
                ".chat-list",
                ".conversation-panel",
                '[data-testid="main"]',
            ]

            for selector in selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    logger.info(f"셀렉터 성공: {selector}")
                    break
                except Exception as e:
                    logger.debug(f"셀렉터 실패: {selector} - {e}")
                    continue
            else:
                logger.warning("모든 셀렉터 실패")

            # 3. 디버깅 스크린샷 (개발 모드)
            if self.debug_mode:
                try:
                    await page.screenshot(path="debug_loading.png")
                    logger.info("디버깅 스크린샷 저장: debug_loading.png")
                except Exception as e:
                    logger.debug(f"스크린샷 저장 실패: {e}")

            # 4. 추가 안정성 검증
            await self._verify_chat_loaded(page)

            return True

        except Exception as e:
            logger.error(f"채팅 로딩 실패: {e}")
            return False

    async def _verify_chat_loaded(self, page: Page) -> bool:
        """채팅 로딩 상태 검증"""
        try:
            # 메시지 컨테이너 확인
            message_selectors = [
                '[data-testid="conversation-panel-messages"]',
                ".message-list",
                '[data-testid="msg-container"]',
            ]

            for selector in message_selectors:
                try:
                    element = page.locator(selector)
                    if await element.is_visible():
                        logger.info(f"메시지 컨테이너 확인: {selector}")
                        return True
                except Exception:
                    continue

            logger.warning("메시지 컨테이너를 찾을 수 없음")
            return False

        except Exception as e:
            logger.error(f"채팅 로딩 검증 실패: {e}")
            return False

    async def wait_for_element_with_retry(
        self, page: Page, selector: str, max_retries: int = 3, timeout: int = 5000
    ) -> bool:
        """
        재시도 로직이 포함된 요소 대기

        Args:
            page: Playwright Page 객체
            selector: CSS 셀렉터
            max_retries: 최대 재시도 횟수
            timeout: 각 시도당 타임아웃

        Returns:
            bool: 요소 발견 여부
        """
        for attempt in range(max_retries):
            try:
                await page.wait_for_selector(selector, timeout=timeout)
                logger.info(f"요소 발견: {selector} (시도 {attempt + 1})")
                return True
            except Exception as e:
                logger.debug(f"요소 대기 실패 (시도 {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)  # 1초 대기 후 재시도

        logger.warning(f"요소를 찾을 수 없음: {selector}")
        return False

    async def human_like_behavior(self, page: Page) -> None:
        """인간과 유사한 행동 시뮬레이션"""
        try:
            # 랜덤 마우스 움직임
            await page.mouse.move(random.randint(100, 800), random.randint(100, 600))
            await page.wait_for_timeout(random.randint(500, 1500))

            # PageUp 키로 스크롤
            await page.keyboard.press("PageUp")
            await page.wait_for_timeout(random.randint(1000, 3000))

            # 추가 랜덤 지연
            await page.wait_for_timeout(random.randint(2000, 5000))

            logger.debug("인간 행동 시뮬레이션 완료")

        except Exception as e:
            logger.debug(f"인간 행동 시뮬레이션 오류: {e}")

    async def solve_captcha(self, page: Page) -> bool:
        """CAPTCHA 감지 및 해결"""
        try:
            captcha_selectors = [
                "iframe[src*='captcha']",
                "[data-testid='captcha']",
                ".captcha-container",
            ]

            for selector in captcha_selectors:
                try:
                    captcha_element = page.locator(selector)
                    if await captcha_element.is_visible():
                        logger.warning("CAPTCHA 감지됨 - 수동 해결 필요")
                        print("\n[CAPTCHA] CAPTCHA 감지됨!")
                        print("1. 브라우저에서 CAPTCHA를 해결하세요")
                        print("2. 해결 완료 후 Enter를 눌러주세요...")
                        input("CAPTCHA 해결 후 Enter: ")
                        return True
                except Exception:
                    continue

        except Exception as e:
            logger.debug(f"CAPTCHA 확인 중 오류: {e}")

        return False
