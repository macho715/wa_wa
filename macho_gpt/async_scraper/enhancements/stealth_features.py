"""
고급 스텔스 기능 모듈
extract_whatsapp_auto.py에서 추출한 스텔스 기능들을 통합
"""

import random
import logging
from typing import List, Optional, Dict, Any
from playwright.async_api import Page, BrowserContext

logger = logging.getLogger(__name__)


class StealthFeatures:
    """고급 스텔스 기능 클래스"""

    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
        ]
        self.current_ua_index = 0

    def get_random_user_agent(self) -> str:
        """랜덤 User-Agent 반환"""
        if not self.enabled:
            return self.user_agents[0]

        ua = random.choice(self.user_agents)
        logger.debug(f"선택된 User-Agent: {ua[:50]}...")
        return ua

    def get_next_user_agent(self) -> str:
        """다음 User-Agent 반환 (로테이션)"""
        if not self.enabled:
            return self.user_agents[0]

        ua = self.user_agents[self.current_ua_index]
        self.current_ua_index = (self.current_ua_index + 1) % len(self.user_agents)
        logger.debug(f"로테이션 User-Agent: {ua[:50]}...")
        return ua

    async def apply_stealth_settings(self, context: BrowserContext) -> None:
        """스텔스 설정 적용"""
        if not self.enabled:
            return

        try:
            # User-Agent 설정
            ua = self.get_random_user_agent()
            await context.set_extra_http_headers({"User-Agent": ua})

            # 추가 헤더 설정
            await context.set_extra_http_headers(
                {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                }
            )

            logger.info("스텔스 설정 적용 완료")

        except Exception as e:
            logger.error(f"스텔스 설정 적용 실패: {e}")

    async def human_like_behavior(self, page: Page, chat_title: str = None) -> None:
        """인간과 유사한 행동 패턴 시뮬레이션"""
        if not self.enabled:
            return

        try:
            # 랜덤 마우스 움직임
            await page.mouse.move(random.randint(1, 200), random.randint(1, 200))
            await page.wait_for_timeout(random.randint(500, 1500))

            # 채팅방 클릭 (제공된 경우)
            if chat_title:
                try:
                    await page.get_by_title(chat_title).click()
                    await page.wait_for_timeout(random.randint(2000, 5000))
                except Exception as e:
                    logger.debug(f"채팅방 클릭 실패: {e}")

            # 스크롤 (PageUp)
            await page.keyboard.press("PageUp")
            await page.wait_for_timeout(random.randint(1000, 3000))

            # 추가 랜덤 지연
            await page.wait_for_timeout(random.randint(2000, 5000))

            logger.debug("인간 행동 시뮬레이션 완료")

        except Exception as e:
            logger.debug(f"인간 행동 시뮬레이션 오류: {e}")

    async def detect_captcha(self, page: Page) -> bool:
        """CAPTCHA 감지"""
        if not self.enabled:
            return False

        try:
            captcha_selectors = [
                "iframe[src*='captcha']",
                "[data-testid='captcha']",
                ".captcha-container",
                "iframe[src*='recaptcha']",
            ]

            for selector in captcha_selectors:
                try:
                    captcha_element = page.locator(selector)
                    if await captcha_element.is_visible():
                        logger.warning("CAPTCHA 감지됨")
                        return True
                except Exception:
                    continue

        except Exception as e:
            logger.debug(f"CAPTCHA 감지 중 오류: {e}")

        return False

    async def solve_captcha_interactive(self, page: Page) -> bool:
        """CAPTCHA 수동 해결"""
        if not self.enabled:
            return False

        if await self.detect_captcha(page):
            print("\n[CAPTCHA] CAPTCHA 감지됨!")
            print("1. 브라우저에서 CAPTCHA를 해결하세요")
            print("2. 해결 완료 후 Enter를 눌러주세요...")
            input("CAPTCHA 해결 후 Enter: ")
            return True

        return False

    def get_proxy_config(
        self, proxy_list: List[str] = None
    ) -> Optional[Dict[str, Any]]:
        """프록시 설정 반환"""
        if not self.enabled or not proxy_list:
            return None

        try:
            proxy = random.choice(proxy_list)
            return {
                "server": proxy,
                "username": None,  # 프록시 인증 정보가 필요한 경우
                "password": None,
            }
        except Exception as e:
            logger.error(f"프록시 설정 실패: {e}")
            return None

    async def random_delay(self, min_ms: int = 1000, max_ms: int = 3000) -> None:
        """랜덤 지연"""
        if not self.enabled:
            return

        delay = random.randint(min_ms, max_ms)
        await asyncio.sleep(delay / 1000)
        logger.debug(f"랜덤 지연: {delay}ms")

    async def simulate_typing(
        self, page: Page, text: str, element_selector: str = None
    ) -> None:
        """타이핑 시뮬레이션"""
        if not self.enabled:
            return

        try:
            if element_selector:
                element = page.locator(element_selector)
                await element.click()

            # 천천히 타이핑
            for char in text:
                await page.keyboard.type(char)
                await asyncio.sleep(random.uniform(0.05, 0.2))  # 50-200ms 지연

        except Exception as e:
            logger.debug(f"타이핑 시뮬레이션 오류: {e}")

    async def random_scroll(self, page: Page) -> None:
        """랜덤 스크롤"""
        if not self.enabled:
            return

        try:
            # 랜덤 스크롤 방향과 거리
            scroll_direction = random.choice(["up", "down"])
            scroll_distance = random.randint(1, 5)

            for _ in range(scroll_distance):
                if scroll_direction == "up":
                    await page.keyboard.press("PageUp")
                else:
                    await page.keyboard.press("PageDown")

                await asyncio.sleep(random.uniform(0.5, 1.5))

        except Exception as e:
            logger.debug(f"랜덤 스크롤 오류: {e}")


# 편의 함수들
async def apply_stealth_to_context(
    context: BrowserContext, enabled: bool = False
) -> None:
    """컨텍스트에 스텔스 설정 적용"""
    stealth = StealthFeatures(enabled=enabled)
    await stealth.apply_stealth_settings(context)


async def simulate_human_behavior(
    page: Page, chat_title: str = None, enabled: bool = False
) -> None:
    """인간 행동 시뮬레이션"""
    stealth = StealthFeatures(enabled=enabled)
    await stealth.human_like_behavior(page, chat_title)
